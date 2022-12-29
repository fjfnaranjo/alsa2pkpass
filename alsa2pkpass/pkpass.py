from datetime import datetime
from zipfile import ZipFile


def format_head(description, serial_number, date_str, time_str):
    day, month, year = date_str
    month = dict(
        {
            "enero": 1,
            "febrero": 2,
            "marzo": 3,
            "abril": 4,
            "mayo": 5,
            "junio": 6,
            "julio": 7,
            "agosto": 8,
            "septiembre": 9,
            "octubre": 10,
            "noviembre": 11,
            "diciembre": 12,
        }
    )[month]
    hour, minute = time_str.split(":")
    date = datetime(int(year), month, int(day), int(hour), int(minute))
    relevant_date_w3c = date.strftime("%Y-%m-%dT%H:%M") + ":00+01:00"
    return f"""{{
    "organizationName": "",
    "description": "{description}",
    "serialNumber": "{serial_number}",
    "relevantDate": "{relevant_date_w3c}",
    "backgroundColor": "rgb(0, 31, 106)",
    "formatVersion": 1,
    "boardingPass": {{
        "primaryFields": ["""


def format_field(key, value, label):
    return f"""
            {{
                "value": "{value}",
                "key": "{key}",
                "label": "{label}"
            }}"""


def format_footer():
    return """
        ],
        "transitType": "PKTransitTypeGeneric"
    },
    "teamIdentifier": ""
}"""


def format_manifest(sha1sum):
    return f"""{{
    "pass.json": "{sha1sum}"
}}"""


def create_pkpass(name, pass_, manifest):
    try:
        pass_file = ZipFile(name, "x")
    except FileExistsError:
        raise RuntimeError("File " + name + " already exists.")

    pass_file.writestr("pass.json", pass_)
    pass_file.writestr("manifest.json", manifest)


def write_pkpass(ticket, serial_number, filename):
    all_fields = [
        format_field("service", ticket["service"], "Linea: "),
        format_field("localizer", ticket["localizer"], "Localizador: "),
        format_field("origin", ticket["start_city"], "Origen: "),
        format_field("destination", ticket["end_city"], "Destino: "),
        format_field("bus", ticket["bus"] if "bus" in ticket else "-", "Bus: "),
        format_field("seat", ticket["seat"] if "seat" in ticket else "-", "Asiento: "),
    ]

    ticket = (
        format_head(
            ticket["service"],
            serial_number,
            ticket["start_date"],
            ticket["start_time"],
        )
        + ",".join(all_fields[0])
        + format_footer()
    )

    ticket_manifest = format_manifest(str(sha1(ticket.encode("utf-8")).hexdigest()))

    create_pkpass(filename, ticket, ticket_manifest)
