from hashlib import sha1
from sys import argv

from alsa2pkpass.pdf import parse_pdf
from alsa2pkpass.pkpass import write_pkpass


def main():
    if len(argv) < 2:
        exit("Specify input PDF.")

    try:
        ticket, return_ticket = parse_pdf(argv[1])
        ticket_serial_number = ticket["localizer"] + "_t"
        ticket_filename = "ticket_" + ticket["localizer"] + ".pkpass"
        print("Writing " + ticket_filename + " ...")
        write_pkpass(ticket, ticket_serial_number, ticket_filename)
        if return_ticket is not None:
            return_ticket_serial_number = return_ticket["localizer"] + "_r"
            return_ticket_filename = "ticket_" + return_ticket["localizer"] + ".pkpass"
            print("Writing " + return_ticket_filename + " ...")
            write_pkpass(
                return_ticket, return_ticket_serial_number, return_ticket_filename
            )

    except FileNotFoundError:
        exit("Error reading input PDF.")

    except RuntimeError as e:
        exit(e)

    print("Done.")
