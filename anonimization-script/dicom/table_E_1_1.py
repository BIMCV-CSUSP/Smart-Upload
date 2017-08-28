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
'''

import os, sys, bs4_utils

def main():
    
    '''
    DICOM PS3.15 - Security and System Management Profiles
    
    http://dicom.nema.org/medical/dicom/current/output/html/part15.html#table_E.1-1
    
    Table E.1-1. Application Level Confidentiality Profile Attributes
    '''
    
    os.system('clear')
    
    print '\nDICOM PS3.15 - Security and System Management Profiles'
    print '\nTable E.1-1. Application Level Confidentiality Profile Attributes'
    print '\n---\n'
    
    if len(sys.argv) != 1 + 1: # argv[0] script
        
        print 'usage:', 'python', sys.argv[0], 'table_E_1_1.html\n'
        
    else:
        
        print 'working...\n'
        
        f_html = sys.argv[1]
        
        db_table = {}
        
        db_table['headers'] = {
            '0'  : 'Tag',
            '1'  : 'Attribute Name',
            '2'  : 'Retired (from PS3.6)',
            '3'  : 'In Std. Comp. IOD (from PS3.3)',
            '4'  : 'Basic Profile',
            '5'  : 'Retain Safe Private Option',
            '6'  : 'Retain UIDs Option',
            '7'  : 'Retain Device Ident. Option',
            '8'  : 'Retain Patient Chars. Option',
            '9'  : 'Retain Long. Full Dates Option',
            '10' : 'Retain Long. Modif. Dates Option',
            '11' : 'Clean Desc. Option',
            '12' : 'Clean Struct. Cont. Option',
            '13' : 'Clean Graph. Option'
        }
        
        for item in bs4_utils.parse_html_table(f_html):
            
            db_table[(item[1].replace(' ', '')).upper()] = {
                '1'  : item[0],
                '2'  : item[2],
                '3'  : item[3],
                '4'  : item[4],
                '5'  : item[5],
                '6'  : item[6],
                '7'  : item[7],
                '8'  : item[8],
                '9'  : item[9],
                '10' : item[10],
                '11' : item[11],
                '12' : item[12],
                '13' : item[13],
            }
        
        bs4_utils.dict_to_json(f_html.split('.')[0], db_table)
    

if __name__ == '__main__':
    main()
