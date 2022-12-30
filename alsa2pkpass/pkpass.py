"""Create a valid PKPASS file from ticket data."""
from datetime import datetime
from hashlib import sha1
from zipfile import ZipFile


def format_field(key, value, label):
    return f"""
            {{
                "value": "{value}",
                "key": "{key}",
                "label": "{label}"
            }}"""


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


def write_pkpass(name, passport, manifest):
    try:
        pass_file = ZipFile(name, "x")
    except FileExistsError:
        raise RuntimeError("File " + name + " already exists.")

    pass_file.writestr("pass.json", passport)
    pass_file.writestr("manifest.json", manifest)


def create_pkpass(data, filename, is_return=False):
    fields = [
        format_field("service", data["service"], "Linea: "),
        format_field("localizer", data["localizer"], "Localizador: "),
        format_field("origin", data["start_city"], "Origen: "),
        format_field("destination", data["end_city"], "Destino: "),
        format_field("bus", data["bus"] if "bus" in data else "-", "Bus: "),
        format_field("seat", data["seat"] if "seat" in data else "-", "Asiento: "),
    ]

    passport = (
        format_head(
            f"ALSA {data['start_city']} -> {data['end_city']}",
            data["localizer"] + "_t" if not is_return else "_r",
            data["start_date"],
            data["start_time"],
        )
        + ",".join(fields)
        + format_footer()
    )

    manifest = format_manifest(str(sha1(passport.encode("utf-8")).hexdigest()))

    write_pkpass(filename, passport, manifest)
