from hashlib import sha1
from sys import argv

from alsa2pkpass.pdf import parse_pdf
from alsa2pkpass.pkpass import tickets_to_pkpass


def main():
    if len(argv) < 2:
        exit("Specify input PDF.")

    tickets = parse_pdf(argv[1])
    tickets_to_pkpass(tickets)
