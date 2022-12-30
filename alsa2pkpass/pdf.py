"""Extract relevant ticket data from ALSA PDFs."""
from re import compile

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LAParams


def parse_ticket_page(page):
    ticket_data = {}

    date_pattern = compile(r"^(\d+) (\w+) (\d{4})$")
    time_pattern = compile(r"^\d\d:\d\d$")
    number_pattern = compile(r"^(\d+)$")
    service_pattern = compile(r"^Línea: (.*)$")

    capture_origin = False
    capture_origin_address = False
    capture_destination = False
    capture_destination_address = False
    last_block_size = None
    last_block = []
    date_captures = []
    time_captures = []
    capture_numbers = False
    number_captures = []
    capture_localizer = False

    for element in page:
        if isinstance(element, LTTextBoxHorizontal):
            element_text = element.get_text().rstrip("\n")
            date_match = date_pattern.fullmatch(element_text)
            time_match = time_pattern.fullmatch(element_text)
            number_match = number_pattern.fullmatch(element_text)
            service_match = service_pattern.fullmatch(element_text)

            if any(
                [
                    capture_origin,
                    capture_origin_address,
                    capture_destination,
                    capture_destination_address,
                ]
            ):
                if last_block_size is None:
                    last_block_size = element.height
                    last_block.append(element_text)
                elif last_block_size == element.height:
                    last_block.append(element_text)
                else:
                    block_as_paragraph = "\n".join(last_block)
                    last_block_size = None
                    last_block = []
                    if capture_origin:
                        capture_origin = False
                        capture_origin_address = True
                        ticket_data["start_city"] = block_as_paragraph
                    elif capture_origin_address:
                        capture_origin_address = False
                        ticket_data["start_address"] = block_as_paragraph
                    elif capture_destination:
                        capture_destination = False
                        capture_destination_address = True
                        ticket_data["end_city"] = block_as_paragraph
                    elif capture_destination_address:
                        capture_destination_address = False
                        ticket_data["end_address"] = block_as_paragraph

            elif date_match is not None:
                date_captures.append(date_match.groups())

            elif time_match is not None:
                time_captures.append(time_match.string)
                if "start_city" not in ticket_data:
                    capture_origin = True
                elif "end_city" not in ticket_data:
                    capture_destination = True

            elif element_text == "Asiento":
                capture_numbers = True

            elif capture_numbers and number_match is not None:
                number_captures.append(number_match.group(1))

            elif service_match is not None:
                ticket_data["service"] = service_match.group(1).strip()

            elif element_text == "Localizador":
                capture_localizer = True

            elif capture_localizer:
                capture_localizer = False
                ticket_data["localizer"] = element_text

    ticket_data["start_date"], ticket_data["end_date"], *_ = date_captures
    ticket_data["start_time"], ticket_data["end_time"], *_ = time_captures

    if len(number_captures) == 1:
        ticket_data["bus"] = number_captures[0]
    else:
        ticket_data["bus"], ticket_data["seat"], *_ = number_captures

    for field in [
        "service",
        "localizer",
        "start_city",
        "end_city",
    ]:
        if field not in ticket_data:
            raise RuntimeError(f"Field {field} missing in ticket: {ticket}.")

    return ticket_data


def parse_pdf(filename):
    # PDFs for one way tickets have 2 pages, ticket summary and receipt
    # PDFs with return tickets have 4 pages, with receipts in the last two pages
    pages = extract_pages(filename, laparams=LAParams(line_margin=0))
    page_iterator = iter(pages)
    ticket_page = next(page_iterator)
    return_ticket_page = next(page_iterator)
    try:
        extra_page = next(page_iterator)
    except StopIteration:
        return_ticket_page = None

    ticket_data = parse_ticket_page(ticket_page)
    return_ticket_data = (
        parse_ticket_page(return_ticket_page)
        if return_ticket_page is not None
        else None
    )

    return ticket_data, return_ticket_data
