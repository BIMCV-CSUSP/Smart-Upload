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
    Table E.1-1. Application Level Confidentiality Profile Attributes
    
    with VR values from
    
    Table 6-1. Registry of DICOM Data Elements
    
    ---
    
    unknown VR for: (0000,1001)
    unknown VR for: (0000,1000)
    unknown VR for: (0004,1511)
    unknown VR for: (GGGG,EEEE)
    unknown VR for: (0002,0003)
    unknown VR for: (50XX,XXXX)
    
    * VR is VRX for unknown
    '''
    
    os.system('clear')
    
    print '\nTable E.1-1. Application Level Confidentiality Profile Attributes'
    print '\nwith VR values from'
    print '\nTable 6-1. Registry of DICOM Data Elements'
    print '\n---\n'
    
    if len(sys.argv) != 2 + 1: # argv[0] script
        
        print 'usage:', 'python', sys.argv[0], 'table_6_1.json table_E_1_1.json\n'
        
    else:
        
        print 'working...\n'
        
        db_table_6_1   = bs4_utils.json_to_dict(sys.argv[1])
        
        db_table_E_1_1 = bs4_utils.json_to_dict(sys.argv[2])
        
        db_table_E_1_1_VR = {}
        
        # get table_E_1_1 headers
        
        db_headers = db_table_E_1_1['headers']
        
        # set new header
        
        h_new = '14'
        
        db_headers[h_new] = 'VR'
        
        # save new headers in table_E_1_1_VR
        
        db_table_E_1_1_VR['headers'] = db_headers
        
        # fill VR
        
        for tag in db_table_E_1_1:
            
            # get info from db_table_E_1_1
            
            db_info = db_table_E_1_1[tag]
            
            if tag in db_table_6_1:
                
                # set VR from table_6_1
                
                db_info[h_new] = db_table_6_1[tag]['3']
            
            else:
                
                print 'unknown VR for', tag + '\n'
                
                # set unknown VR to VRX
                
                db_info[h_new] = 'VRX'
                
            # save in table_E_1_1_VR
            
            db_table_E_1_1_VR[tag] = db_info
            
        bs4_utils.dict_to_json('table_E_1_1_VR', db_table_E_1_1_VR)
    

if __name__ == '__main__':
    main()
