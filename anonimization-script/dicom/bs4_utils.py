#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Subdirección General de Sistemas de Información para la Salud

Centro de Excelencia e Innovación Tecnológica de Bioimagen de la Conselleria de Sanitat

http://ceib.san.gva.es/

María de la Iglesia Vayá

Ángel Fernández-Cañada Vilata

Jorge Isnardo Altamirano

---

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.

---

Prerequisites

sudo apt-get install python-bs4
'''

from bs4 import BeautifulSoup

import json

def parse_html_table(f_html):
    
    html = ''
    
    with open(f_html, 'r') as r_file:
        html = r_file.read()
    r_file.close()
    
    bs = BeautifulSoup(html)
    
    table = bs.find('table')
    
    tbody = table.find('tbody')
    
    rows = tbody.find_all('tr')
    
    data = []
    
    for row in rows:
        cols = row.find_all('td')
        data.append([value.text.strip() for value in cols])
    
    return data

def dict_to_json(f_file, d_dict):
    f_file += '.json'
    with open(f_file, 'w') as w_file:
        json.dump(d_dict, w_file, indent=4)
    w_file.close()
    print 'Done! -> ' + f_file + '\n'

def json_to_dict(f_file):
    d_dict = {}
    with open(f_file, 'r') as f_file:
        d_dict = dict(json.load(f_file))
    f_file.close()
    return d_dict
