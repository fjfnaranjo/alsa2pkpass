from re import compile

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal


def parse_pdf_page(page_layout):
    ticket = {}
    date_pattern = compile(r"^(\d+) (\w+) (\d{4})\n$")
    time_pattern = compile(r"^(\d\d:\d\d)\n$")
    text_pattern = compile(r"^(\w+)\n$")
    number_pattern = compile(r"^(\d+)\n$")
    service_pattern = compile(r"^Paradas: .*\nLínea: (.*)\n$")
    localizer_pattern = compile(r"^Localizador\n(.*)\n$")

    current = None
    it = iter(page_layout)
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
    ticket["start_date"] = current.groups()
    element = next(it)

    current = time_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = time_pattern.fullmatch(element.get_text())
    ticket["start_time"] = current.group(1)
    element = next(it)

    current = text_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = text_pattern.fullmatch(element.get_text())
    ticket["start_city"] = current.group(1)
    element = next(it)

    current = date_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = date_pattern.fullmatch(element.get_text())
    ticket["end_date"] = current.groups()
    element = next(it)

    current = time_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = time_pattern.fullmatch(element.get_text())
    ticket["end_time"] = current.group(1)
    element = next(it)

    current = text_pattern.fullmatch(element.get_text())
    while current is None:
        element = next(it)
        while not isinstance(element, LTTextBoxHorizontal):
            element = next(it)
        current = text_pattern.fullmatch(element.get_text())
    ticket["end_city"] = current.group(1)
    element = next(it)

    ticket["start_address"] = element.get_text().rstrip("\n")
    element = next(it)
    ticket["end_address"] = element.get_text().rstrip("\n")
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
                if "bus" not in ticket:
                    ticket["bus"] = current_number.group(1)
                else:
                    ticket["seat"] = current_number.group(1)
            if current_service is not None:
                ticket["service"] = current_service.group(1).strip()
            if current_localizer is not None:
                ticket["localizer"] = current_localizer.group(1)
            element = next(it)
            while not isinstance(element, LTTextBoxHorizontal):
                element = next(it)
    except StopIteration:
        pass

    return ticket


def parse_pdf(filename):
    # PDFs for one way tickets have 2 pages, ticket summary and receipt
    # PDFs with return tickets have 4 pages, with receipts in the last two pages
    page_layout = extract_pages(filename)
    ticket_page = None
    return_ticket_page = None
    it = iter(page_layout)
    ticket_page = next(it)
    return_ticket_page = next(it)
    try:
        extra_page = next(it)
    except StopIteration:
        return_ticket_page = None

    return [
        parse_pdf_page(ticket_page),
        (
            parse_pdf_page(return_ticket_page)
            if return_ticket_page is not None
            else None
        ),
    ]
