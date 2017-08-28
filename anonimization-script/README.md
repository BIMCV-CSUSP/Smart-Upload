**Instructions**

---

Last provided anonymization script build is for DICOM Standard 2015c.

Tue Sep 8 11:58:24 EDT 2015.

[DICOM Standard Status](http://www.dclunie.com/dicom-status/status.html)

---

**1) Get a copy of the latest html code of Table 6-1. Registry of DICOM Data Elements.**

bimcv/src/dicom/2015c/table_6_1.html

**2) Get a copy of the latest html code of Table E.1-1. Application Level Confidentiality Profile Attributes.**

bimcv/src/dicom/2015c/table_E_1_1.html

Remove "where gggg is odd" from "<span class="italic">(gggg,eeee)</span>"

**3) Convert them to json (table_6_1.json / table_E_1_1.json)**

bimcv/src/dicom/2015c/

    python ../table_6_1.py table_6_1.html
    
    python ../table_E_1_1.py table_E_1_1.html

**4) Get Table E.1-1 VR values from Table 6-1 (table_E_1_1_VR.json)**

bimcv/src/dicom/2015c/

    python ../table_E_1_1_VR.py table_6_1.json table_E_1_1.json

**5) Build the anonymization.script for the Clinical Trial Processor.**

bimcv/src/anonymization/2015c/

    python ../generate_anon_script.py ../../dicom/2015c/table_E_1_1_VR.json XNAT_Project_ID

---

**The** [DICOM](http://dicom.nema.org/) [Standard](http://medical.nema.org/standard.html)

---

**DICOM Part 6: Data Dictionary**

**PS3.6**

[DICOM PS3.6 - Data Dictionary](http://medical.nema.org/medical/dicom/current/output/html/part06.html)

[Table 6-1. Registry of DICOM Data Elements](http://medical.nema.org/medical/dicom/current/output/html/part06.html#chapter_6)

---

**DICOM Part 15: Security and System Management Profiles**

**PS3.15**

[DICOM PS3.15 - Security and System Management Profiles](http://medical.nema.org/medical/dicom/current/output/html/part15.html)

[Table E.1-1. Application Level Confidentiality Profile Attributes](http://medical.nema.org/medical/dicom/current/output/html/part15.html#table_E.1-1)

---

**CTP-The RSNA [Clinical Trial Processor](http://mircwiki.rsna.org/index.php?title=CTP-The_RSNA_Clinical_Trial_Processor)**

**RSNA MIRC [site](http://mirc.rsna.org)**
