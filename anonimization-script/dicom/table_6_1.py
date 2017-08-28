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

import os, sys, re, bs4_utils

def main():
    
    '''
    DICOM PS3.6 - Data Dictionary
    
    http://dicom.nema.org/medical/dicom/current/output/html/part06.html#chapter_6
    
    Table 6-1. Registry of DICOM Data Elements
    '''
    
    os.system('clear')
    
    print '\nDICOM PS3.6 - Data Dictionary'
    print '\nTable 6-1. Registry of DICOM Data Elements'
    print '\n---\n'
    
    if len(sys.argv) != 1 + 1: # argv[0] script
        
        print 'usage:', 'python', sys.argv[0], 'table_6_1.html\n'
        
    else:
        
        print 'working...\n'
        
        f_html = sys.argv[1]
        
        db_table = {}
        
        db_table['headers'] = {
            '0' : 'Tag',
            '1' : 'Name',
            '2' : 'Keyword',
            '3' : 'VR',
            '4' : 'VM',
            '5' : 'Notes'
        }
        
        for item in bs4_utils.parse_html_table(f_html):
            
            db_table[(item[0].replace(' ', '')).upper()] = {
                '1' : item[1],
                '2' : re.sub(u'\s|\u200b', '', item[2]), # Remove zero-width space
                '3' : item[3],
                '4' : item[4],
                '5' : item[5]
            }
            
        bs4_utils.dict_to_json(f_html.split('.')[0], db_table)
        
    

if __name__ == '__main__':
    main()
