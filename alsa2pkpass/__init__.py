from hashlib import sha1
from sys import argv

from alsa2pkpass.pdf import parse_pdf
from alsa2pkpass.pkpass import tickets_to_pkpass


def main():
    if len(argv) < 2:
        exit("Specify input PDF.")

    try:
        tickets = parse_pdf(argv[1])
    except FileNotFoundError:
        exit("Error reading input PDF.")

    try:
        tickets_to_pkpass(tickets)
    except RuntimeError as e:
        exit(e)
