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

import sys, os, re

sys.path.append('../../dicom') # Location of bs4_utils lib

import bs4_utils

'''
This code creates an anonymization script based on:
    
    + the selected DICOM profiles
    + the defined special cases
    + and the indicated non standard tags
'''

def main():
    
    os.system('clear')
    
    print '\nRSNA Clinical Trial Processor CEIB-CS script builder'
    print '\nThis code creates an anonymization script based on:'
    print '\n    + the selected DICOM profiles'
    print '\n    + the defined special cases'
    print '\n    + and the indicated non standard tags'
    print '\n---\n'
    
    if len(sys.argv) != 2 + 1: # argv[0] script
        
        print 'usage:', 'python', sys.argv[0], '../dicom/table_E_1_1_VR.json XNAT_Project_ID\n'
        
    else:
        
        db_table_E_1_1_VR = bs4_utils.json_to_dict(sys.argv[1])
        XNAT_Project_ID   = sys.argv[2]
        
        # remove undesired keys
        
        del db_table_E_1_1_VR['headers']
        del db_table_E_1_1_VR['(50XX,XXXX)']
        del db_table_E_1_1_VR['(GGGG,EEEE)']
        
        '''
        Possible actions:
            
            D : Replace with non zero length dummy value
            Z : Replace with zero length value or non zero length dummy value
            X : Remove
            K : Keep Unchanged for non-sequence attributes, cleaned for sequences
            C : Clean Replace the value with values of similar meaning known not to contain identifying information
            U : Replace with non zero length UID that is internally consistent with a set of instances
        '''
        
        actions = {
            'X'     : '@remove()',
            'X/Z'   : '@remove()',
            'X/D'   : '@remove()',
            'X/Z/D' : '@remove()',
            'X/Z/U' : '@remove()',
            'K'     : '@keep()',
            'U'     : '@hashuid(@UIDROOT,this)',
            'Z'     : 'check_vr',
            'Z/D'   : 'check_vr',
            'D'     : 'check_vr',
            'C'     : '@empty()'
        }
        
        special_case = {
            '00100010' : '@hash(this, 64)',                                         # Patient Name                     | Standard says Z
            '00100020' : '@hash(this, 64)',                                         # Patient ID                       | Standard says Z
            '00100030' : '@keep()',                                                 # Patient Birth Date               | Standard says Z
            '00081030' : '@always()@contents(this,".+","' + XNAT_Project_ID + '")', # Study Description                | Standard says X
            '0008103E' : '@always()@contents(SeriesDescription,"\W+")',             # Series Description (XNAT Needed) | Standard says X
            '00181030' : '@always()@contents(ProtocolName,"\W+")'                   # Protocol Name (XNAT Needed)      | Standard says X
        }
        
        # http://www.na-mic.org/Wiki/index.php/NAMIC_Wiki:DTI:DICOM_for_DWI_and_DTI
        
        non_standard = [
            ['00080060', 'Modality' , '@keep()'], # Modality (XNAT Needed)
            
            ['00189075', 'Diffusion Directionality'              , '@keep()'], # Recommended DWI / DTI
            ['00189076', 'Diffusion Gradient Direction Sequence' , '@keep()'], # Recommended DWI / DTI
            ['00189087', 'Diffusion b-value'                     , '@keep()'], # Recommended DWI / DTI
            ['00189089', 'Diffusion Gradient Orientation'        , '@keep()'], # Recommended DWI / DTI
            ['00189117', 'MR Diffusion Sequence'                 , '@keep()'], # Recommended DWI / DTI
            ['00189147', 'Diffusion Anisotropy Type'             , '@keep()'], # Recommended DWI / DTI
            
            ['001910e0', 'DTI diffusion directions'                  , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # release 10.0 and above
            ['001910df', 'DTI diffusion directions'                  , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # release 9.0 & below
            ['001910d9', 'Concatenated SAT DTI diffusion directions' , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # release 9.0 and below
            ['0021105a', 'Diffusion direction'                       , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later)
            ['00431039', 'Slop_int_6... slop_int_9'                  , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # (in the GEMS_PARM_01 block)
            ['00181312', 'Phase encoding direction'                  , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # Dartmouth DWI data
            ['001910bb', 'image columns or rows '                    , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # Dartmouth DWI data
            ['001910bc', 'image rows or columns'                     , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # Dartmouth DWI data
            ['001910bd', 'image slices'                              , '@keep()'], # Private vendor GE (Signa Excite Scanner 12.0 and later) # Dartmouth DWI data
            
            ['00291010', 'Diffusion gradient information and coordinate frame' , '@keep()'], # Private vendor Siemens
            ['0019000a', 'NumberOfImagesInMosaic'                              , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            ['0019000b', 'SliceMeasurementDuration'                            , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            ['0019000c', 'B_value'                                             , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            ['0019000d', 'DiffusionDirectionality'                             , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            ['0019000e', 'DiffusionGradientDirection'                          , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            ['0019000f', 'GradientMode'                                        , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            ['00190027', 'B_matrix'                                            , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            ['00190028', 'BandwidthPerPixelPhaseEncode'                        , '@keep()'], # Private vendor Siemens # MR scanner software (2006)
            
            ['20011003', 'B_value'            , '@keep()'], # Private vendor Philips
            ['20011004', 'Diffusion direction', '@keep()'], # Private vendor Philips
            
            ['00189087', 'B_value'                        , '@keep()'], # Private vendor Toshiba (Titan 3T (console software V2.30*R005))
            ['00291001', 'Private Sequence'               , '@keep()'], # Private vendor Toshiba (Titan 3T (console software V2.30*R005))
            ['00291090', 'Private Byte Data'              , '@keep()'], # Private vendor Toshiba (Titan 3T (console software V2.30*R005))
            ['00189089', 'Diffusion Gradient Orientation' , '@keep()']  # Private vendor Toshiba (Titan 3T (console software V2.30*R005))
        ]
        
        vrs = {
            'SQ' : '@remove()', # Sequence of zero or more Items
            'PN' : '@empty()',  # Person Name
            'LO' : '@empty()',  # Long String
            'TM' : '@time()',   # A string of characters of the format HHMMSS.FFFFFF where FFFFFF are milliseconds
            'DA' : '@date()',   # Date
            'CS' : '@empty()',  # Code String
            'SH' : '@empty()'   # Short String
        }
        
        '''
        RETAIN_LONG_FULL_DATES and RETAIN_LONG_MODIF_DATES are not compatibles.
        
        BASIC PROFILE is mandatory.
        '''
        
        profiles = [
            ['BASIC',                    '4', True],
            ['RETAIN_SAFE_PRIVATE',      '5', False],
            ['RETAIN_UIDS',              '6', True],
            ['RETAIN_DEVICE_IDENT',      '7', True],
            ['RETAIN_PATIENT_CHARS',     '8', True],
            ['RETAIN_LONG_FULL_DATES',   '9', True],
            ['RETAIN_LONG_MODIF_DATES', '10', False],
            ['CLEAN_DESC',              '11', False],
            ['CLEAN_STRUCT_CONT',       '12', False],
            ['CLEAN_GRAPH',             '13', False]
        ]
        
        profiles_applied = []
        
        for profile, index, is_applied in profiles:
            
            if(is_applied):
                
                profiles_applied.insert(0, index)
            
        if('9' in profiles_applied and '10' in profiles_applied):
            
            print profiles[5], 'and', profiles[6], "can't be applied simultaneously" # RETAIN_LONG_FULL_DATES | RETAIN_LONG_MODIF_DATES
            
        elif('4' not in profiles_applied):
            
            print profiles[0], 'PROFILE is mandatory' # BASIC
            
        else:
            
            with open('anonymization.script', 'w') as w_file:
                
                w_file.write(
                    append('<script>') +
                    append_comment('Subdireccion General de Sistemas de Informacion para la Salud') +
                    append_comment('Centro de Excelencia e Innovacion Tecnologica de Bioimagen de la Conselleria de Sanitat') +
                    append_comment('http://ceib.san.gva.es/') +
                    append_comment('Maria de la Iglesia Vaya') +
                    append_comment('Angel Fernandez-Canada Vilata') +
                    append_comment('Jorge Isnardo Altamirano') +
                    append_comment('It is up to the user to inspect and clean all tags of PHI'))
                    
                for pa in profiles_applied:
                    for p in profiles:
                        if pa == p[1]:
                            w_file.write(append_comment('Profile ' + p[0] + ' applied'))
                            break
                        
                    
                w_file.write(
                    append_comment('Some special attribute cases and non standard are checked due particular purposes') +
                    append_comment('Works with CTP version 2015.04.10'))
                
                '''
                
                https://github.com/johnperry/CTP/tree/master/source/files/profiles/dicom
                
                ---
                
                DATEINC (date offset)
                
                Recommended value is between -1700 and -3500 (~5-10 years)
                
                ---
                
                The parameter "UIDROOT" below is a default UID root used by TCIA.
                
                http://www.cancerimagingarchive.net/
                
                We reccomend that you register for your own root, however, it is ok to use this one.
                '''
                
                w_file.write(
                    # append_p('DATEINC'    , '-3210') +
                    append_p('NOTICE1'    , 'IMPORTANT: Be sure to review Series Descriptions for PHI.') +
                    append_p('NOTICE2'    , 'IMPORTANT: Tags inside of sequences may contain PHI.') +
                    append_p('PROFILENAME', 'CEIBANON') +
                    append_p('PROJECTNAME', XNAT_Project_ID) +
                    append_p('SITEID'     , '1') +
                    append_p('SITENAME'   , 'http://ceib.bioinfo.cipf.es/xnat') +
                    append_p('SUBJECT'    , XNAT_Project_ID + ' subjects') +
                    append_p('TRIALNAME'  , 'Trial') +
                    append_p('UIDROOT'    , '1.3.6.1.4.1.14519.5.2.1.9999.9999'))
                
                for key in db_table_E_1_1_VR:
                    
                    item = db_table_E_1_1_VR[key]
                    
                    action_to_apply = 'F'
                    tag             = re.sub('[(),]', '', key) # (0000,0000) -> 00000000
                    description     = item['1']
                    action          = ''
                    
                    # Special case attributes
                    
                    if(tag in special_case):
                        
                        action          = special_case[tag]
                        action_to_apply = 'T'
                        
                    else:
                        
                        for profile_index in profiles_applied:
                            
                            ac_key = item[profile_index].replace('*', '')
                            
                            if (ac_key != ''):
                                
                                if (ac_key in actions.keys()):
                                    
                                    action = actions[ac_key]
                                    
                                    if(action == 'check_vr'):
                                        
                                        vr     = item['14']
                                        action = vrs[vr]
                                        
                                        if(action == ''):
                                            
                                            print '\n' + ac_key
                                            print 't=' + tag + ' n=' + description
                                            print vr
                                        
                                    elif(action == ''):
                                        
                                        print '\n' + ac_key
                                        print 't=' + tag + ' n=' + description
                                    
                                    if (action != ''):
                                        
                                        action_to_apply = 'T'
                                        break
                                    
                                else:
                                    
                                    print '\nt=' + tag + ' n=' + description
                                    print 'Key', ac_key, 'not found in actions dictionary'
                                
                            
                        # end for
                    
                    w_file.write(append_e(action_to_apply, tag, description, action))
                    
                # end for
                
                # non_standard attributes
                
                for item in non_standard:
                    
                    tag         = item[0]
                    description = item[1]
                    action      = item[2]
                    
                    w_file.write(append_e('T', tag, description, action))
                
                # Some DICOM-PS3.15-CleanGraphics and TCIA-Basic options
                
                w_file.write(
                    append_r('T', 'curves',        'Remove curves') +
                    append_r('T', 'overlays',      'Remove overlays') +
                    append_r('T', 'privategroups', 'Remove private groups'))
                
                w_file.write('</script>')
                
            w_file.close()
            
            print 'Done!\n'
            
        
    

nline = '\r\n'

def append_r(v1, v2, v3):
    return '<r en="' + v1 + '" t="' + v2 + '">' + v3 + '</r>' + nline

def append_e(v1, v2, v3, v4):
    return '<e en="' + v1 + '" t="' + v2 + '" n="' + v3 + '">' + v4 + '</e>' + nline

def append_p(v1, v2):
    return '<p t="' + v1 + '">' + v2 + '</p>' + nline

def append_comment(v):
    return '<!-- ' + v + ' -->' + nline

def append(v):
    return v + nline

if __name__ == '__main__':
    main()
