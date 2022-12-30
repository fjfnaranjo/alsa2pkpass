"""Extract relevant ticket data from ALSA PDFs."""
from re import compile

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal


def parse_ticket_page(page):
    ticket_data = {}
    date_pattern = compile(r"^(\d+) (\w+) (\d{4})\n$")
    time_pattern = compile(r"^(\d\d:\d\d)\n$")
    text_pattern = compile(r"^(\w+)\n$")
    number_pattern = compile(r"^(\d+)\n$")
    service_pattern = compile(r"^Paradas: .*\nLínea: (.*)\n$")
    localizer_pattern = compile(r"^Localizador\n(.*)\n$")

    current = None
    it = iter(page)
    element = next(it)

    while (
        not isinstance(element, LTTextBoxHorizontal)
        or element.get_text() != "Tu billete\n"
    ):
        element = next(it)
    element = next(it)

    current = date_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = date_pattern.fullmatch(element.get_text())
    ticket_data["start_date"] = current.groups()
    element = next(it)

    current = time_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = time_pattern.fullmatch(element.get_text())
    ticket_data["start_time"] = current.group(1)
    element = next(it)

    current = text_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = text_pattern.fullmatch(element.get_text())
    ticket_data["start_city"] = current.group(1)
    element = next(it)

    current = date_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = date_pattern.fullmatch(element.get_text())
    ticket_data["end_date"] = current.groups()
    element = next(it)

    current = time_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = time_pattern.fullmatch(element.get_text())
    ticket_data["end_time"] = current.group(1)
    element = next(it)

    current = text_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = text_pattern.fullmatch(element.get_text())
    ticket_data["end_city"] = current.group(1)
    element = next(it)

    ticket_data["start_address"] = element.get_text().rstrip("\n")
    element = next(it)
    ticket_data["end_address"] = element.get_text().rstrip("\n")
    element = next(it)

    current_number = None
    current_service = None
    current_localizer = None
    try:
        while True:
            current_number = number_pattern.fullmatch(element.get_text())
            current_service = service_pattern.fullmatch(element.get_text())
            current_localizer = localizer_pattern.fullmatch(element.get_text())
            if current_number is not None:
                if "bus" not in ticket_data:
                    ticket_data["bus"] = current_number.group(1)
                else:
                    ticket_data["seat"] = current_number.group(1)
            if current_service is not None:
                ticket_data["service"] = current_service.group(1).strip()
            if current_localizer is not None:
                ticket_data["localizer"] = current_localizer.group(1)
            element = next(it)
            while not isinstance(element, LTTextBoxHorizontal):
                element = next(it)
    except StopIteration:
        pass

    return ticket_data


def check_missing_fields(ticket):
    for field in [
        "service",
        "localizer",
        "start_city",
        "end_city",
        "start_date",
        "start_time",
    ]:
        if field not in ticket:
            raise RuntimeError(f"Field {field} missing in ticket: {ticket}.")


def parse_pdf(filename):
    # PDFs for one way tickets have 2 pages, ticket summary and receipt
    # PDFs with return tickets have 4 pages, with receipts in the last two pages
    pages = extract_pages(filename)
    page_iterator = iter(pages)
    ticket_page = next(page_iterator)
    return_ticket_page = next(page_iterator)
    try:
        extra_page = next(page_iterator)
    except StopIteration:
        return_ticket_page = None

    ticket_data = check_missing_fields(parse_ticket_page(ticket_page))
    return_ticket_data = (
        check_missing_fields(parse_ticket_page(return_ticket_page))
        if return_ticket_page is not None
        else None,
    )

    return (ticket_data, return_ticket_data)
