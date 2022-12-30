from sys import argv

from alsa2pkpass.pdf import parse_pdf
from alsa2pkpass.pkpass import create_pkpass


def main():
    if len(argv) < 2:
        exit("Specify input PDF.")

    try:
        data, return_data = parse_pdf(argv[1])
        filename = "ticket_" + data["localizer"] + ".pkpass"
        print("Writing " + filename + " ...")
        create_pkpass(data, filename)
        if return_data is not None:
            return_filename = "ticket_" + return_data["localizer"] + ".pkpass"
            print("Writing " + return_filename + " ...")
            create_pkpass(return_data, return_filename, is_return=True)

    except FileNotFoundError:
        exit("Error reading input PDF.")

    except RuntimeError as e:
        exit(e)

    print("Done.")
