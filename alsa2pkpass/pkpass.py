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


def tickets_to_pkpass(tickets):
    all_fields = []
    for ticket in tickets:
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
        all_fields.append(
            [
                format_field("service", ticket["service"], "Linea: "),
                format_field("localizer", ticket["localizer"], "Localizador: "),
                format_field("origin", ticket["start_city"], "Origen: "),
                format_field("destination", ticket["end_city"], "Destino: "),
                format_field("bus", ticket["bus"] if "bus" in ticket else "-", "Bus: "),
                format_field(
                    "seat", ticket["seat"] if "seat" in ticket else "-", "Asiento: "
                ),
            ]
        )

    ticket = (
        format_head(
            tickets[0]["service"],
            tickets[0]["localizer"] + "_t",
            tickets[0]["start_date"],
            tickets[0]["start_time"],
        )
        + ",".join(all_fields[0])
        + format_footer()
    )

    ticket_manifest = format_manifest(str(sha1(ticket.encode("utf-8")).hexdigest()))

    ticket_name = "ticket_" + tickets[0]["localizer"] + ".pkpass"
    print("Writing " + ticket_name + " ...")
    create_pkpass(ticket_name, ticket, ticket_manifest)

    if len(tickets) == 2:

        return_ticket = (
            format_head(
                tickets[1]["service"],
                tickets[1]["localizer"] + "_r",
                tickets[1]["start_date"],
                tickets[1]["start_time"],
            )
            + ",".join(all_fields[1])
            + format_footer()
        )

        return_ticket_manifest = format_manifest(
            str(sha1(return_ticket.encode("utf-8")).hexdigest())
        )

        return_ticket_name = "ticket_return_" + tickets[1]["localizer"] + ".pkpass"
        print("Writing " + return_ticket_name + " ...")
        create_pkpass(return_ticket_name, return_ticket, return_ticket_manifest)

    print("Done.")
