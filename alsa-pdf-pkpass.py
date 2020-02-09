# -*- coding: utf-8 -*-

from tempfile import mkdtemp
from re import compile
from sys import argv

from PyPDF2 import PdfFileReader
from ypassbook import Pass, Field


pdf = PdfFileReader(argv[1])

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

pass_ticket = []
pass_data = []

def clear_utf8(string):
    return string.encode('ascii', 'ignore')

for idx in range(2):
    pass_ticket.append(Pass(Pass.BOARDINGPASS, '', '', ['ida', 'vuelta'][idx], '', localizers[idx]))
    pass_ticket[idx].addPrimaryField(Field('service',clear_utf8(services[idx]),'Linea: '))
    pass_ticket[idx].addPrimaryField(Field('localizer',clear_utf8(localizers[idx]),'Localizador: '))
    pass_ticket[idx].addPrimaryField(Field('origin',clear_utf8(origins[idx]),'Origen: '))
    pass_ticket[idx].addPrimaryField(Field('destination',clear_utf8(destinations[idx]),'Destino: '))
    pass_ticket[idx].addPrimaryField(Field('date',clear_utf8(dates[idx]),'Fecha: '))
    pass_ticket[idx].addPrimaryField(Field('time',clear_utf8(times[idx]),'Hora: '))
    pass_ticket[idx].addPrimaryField(Field('bus',clear_utf8(buses[idx]),'Bus: '))
    pass_ticket[idx].addPrimaryField(Field('seat',clear_utf8(seats[idx]),'Asiento: '))

ticket_dir = mkdtemp()
return_ticket_dir = mkdtemp()
pass_ticket[0].savePackage(ticket_dir)
pass_ticket[1].savePackage(return_ticket_dir)

