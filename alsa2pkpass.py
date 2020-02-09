from datetime import datetime
from hashlib import sha1
from tempfile import mkdtemp
from re import compile
from sys import argv
from zipfile import ZipFile

from PyPDF2 import PdfFileReader


def format_head(description, serial_number, date_str, time_str):
    day, month, year = date_str.split('/')
    hour, minute = time_str.split(':')
    date = datetime(int(year), int(month), int(day), int(hour), int(minute))
    relevant_date_w3c = date.strftime('%Y-%m-%dT%H:%M') + ':00+01:00'
    return f'''{{
    "organizationName": "",
    "description": "{description}",
    "serialNumber": "{serial_number}",
    "relevantDate": "{relevant_date_w3c}",
    "backgroundColor": "rgb(0, 31, 106)",
    "formatVersion": 1,
    "boardingPass": {{
        "primaryFields": ['''


def format_field(key, value, label):
    return \
        f'''
            {{
                "value": "{value}",
                "key": "{key}",
                "label": "{label}"
            }}'''


def format_footer():
    return '''
        ],
        "transitType": "PKTransitTypeGeneric"
    },
    "teamIdentifier": ""
}'''


def format_manifest(sha1sum):
    return f'''{{
    "pass.json": "{sha1sum}"
}}'''


def create_pkpass(name, pass_, manifest):
    try:
        pass_file = ZipFile(name, 'x')
    except FileExistsError as e:
        exit("File " + name + " already exists.")

    pass_file.writestr('pass.json', pass_)
    pass_file.writestr('manifest.json', manifest)


def main():
    if len(argv)<2 or argv[1] is None:
        exit("Specify input PDF.")

    try:
        pdf = PdfFileReader(argv[1])
    except FileNotFoundError:
        exit("Error reading input PDF.")

    all_text = "".join(page.extractText() for page in pdf.pages)

    dates_regex = compile(r'salida: (\d\d\/\d\d\/\d\d\d\d)')
    times_regex = compile(r'salida: (\d\d:\d\d)')
    localizers_regex = compile(r'Localizador: (.{7})')
    services_regex = compile(r'nea: (.*?)Fecha')
    buses_regex = compile(r'Bus: (.*?)Plaza')
    seats_regex = compile(r'Plaza: (.*?)Localizador')
    origins_regex = compile(r'entre: (.*?)Origen')
    destinations_regex = compile(r'Origen (.*?)Destino')

    dates = dates_regex.findall(all_text)
    times = times_regex.findall(all_text)
    localizers = localizers_regex.findall(all_text)
    services = services_regex.findall(all_text)
    buses = buses_regex.findall(all_text)
    seats = seats_regex.findall(all_text)
    origins = origins_regex.findall(all_text)
    destinations = destinations_regex.findall(all_text)

    all_fields = []

    for idx in range(2):
        all_fields.append([
            format_field('service', services[idx], 'Linea: '),
            format_field('localizer', localizers[idx], 'Localizador: '),
            format_field('origin', origins[idx], 'Origen: '),
            format_field('destination', destinations[idx], 'Destino: '),
            format_field('bus', buses[idx], 'Bus: '),
            format_field('seat', seats[idx], 'Asiento: '),
        ])

    ticket = (
        format_head(services[0], localizers[0] + "_t", dates[0], times[0]) +
        ",".join(all_fields[0]) +
        format_footer()
    )

    ticket_manifest = format_manifest(str(sha1(ticket.encode('utf-8')).hexdigest()))

    return_ticket = (
        format_head(services[1], localizers[1] + "_r", dates[1], times[1]) +
        ",".join(all_fields[1]) +
        format_footer()
    )

    return_ticket_manifest = format_manifest(str(sha1(return_ticket.encode('utf-8')).hexdigest()))

    ticket_name = 'ticket_' + localizers[0] + '.pkpass'
    print("Writing " + ticket_name + " ...")
    create_pkpass(ticket_name, ticket, ticket_manifest)

    return_ticket_name = 'ticket_return_' + localizers[1] + '.pkpass'
    print("Writing " + return_ticket_name + " ...")
    create_pkpass(return_ticket_name, return_ticket, return_ticket_manifest)

    print("Done.")


if __name__ == '__main__':
    main()

