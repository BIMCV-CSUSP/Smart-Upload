#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import dicom
from datetime import datetime as dt
tab='\t'


def get_ids(full_path_dicom,output_folder):
	
	# Check if input folder exists
	if(os.path.exists(full_path_dicom)==False):
		print "Path to DICOM don't exists"
		return 1
	
	# Check if output folder exists if not we'll create it
	if(os.path.exists(output_folder)==False):
		print "Output folder don't exists"
		print "Creating folders"
		os.makedirs(output_folder)
	
	# Create id file report name
	log_name= os.path.join(output_folder,'log_ids_'+str(dt.now().strftime('%Y-%m-%d_%H_%M_%S'))+'.tsv')
	print 'Log will be found at',log_name
	
	with open(log_name, "w") as id_report:
		id_report.write('Patient ID' + tab +'Access Number' + tab +'Patients Name' + tab + 'Study date' + tab +'Gender' +tab + 'Age' + tab + 'Study instance UID\n')
		
		
		# get files
		file_list= get_dcm_list(full_path_dicom)
		print len(file_list),'files selected' 
		
		subjects={}
		for file_ in file_list:
			# Get DICOM data
			tags = ['0x10,0x20','0x08,0x50','0x10,0x10','0x08,0x20','0x10,0x40','0x10,0x30','0x20,0x0D'];
			'''
				(0010,0020) Patients ID
				(0008,0050) Access Number
				(0010,0010) Patients Name
				(0008,0020) Study Date
				(0010,0040) Patients Sex
				(0010,0030) Patients Birth Date
				(0020,000D) Study instance UID
			'''
			
			# Load dicom data
			data = get_dicom_data(tags,file_)
			
			subject_id=data['0x10,0x20']
			experiment_id=data['0x20,0x0D'].replace('.','')
			index=subject_id+experiment_id
			
			if ( index not in subjects.keys()):
				subjects[index]=''
				try:
					# Get age
					birth = dt.strptime(data['0x10,0x30'], '%Y%m%d')
					study_date=data['0x08,0x20']
					study = dt.strptime(study_date, '%Y%m%d')
					age= study.year - birth.year
				except:
					age=''
					pass
				
				line= subject_id + tab + data['0x08,0x50'] + tab + data['0x10,0x10'] + tab + study_date + tab + data['0x10,0x40'] + tab + str(age)+ tab + experiment_id+'\n'
				print line
				id_report.write(line)
			
	id_report.close()
	return 0

'''
def get_dcm_list(dir_name):
	# get a dcm list one per folder
	outputList = []
	last_dir=' '
	for root, dirs, files in os.walk(dir_name):
		if not str(last_dir.split('/')[-1])==str(root.split('/')[-2]):
			for f in files:
				if (f.lower()).endswith('.dcm'):
					outputList.append(os.path.join(root, f))
					last_dir=root
					break
	return outputList
'''
def get_dcm_list(dir_name):
	import subprocess
	sujetos= subprocess.Popen(["find",dir_name, "-maxdepth", "1" ,"-type" ,"d"],stdout=subprocess.PIPE)
	l_sujetos=(sujetos.stdout.read()).split("\n")
	
	l_dicoms=[]
	for folder in l_sujetos[1:-1]:
		dicom= subprocess.Popen(["find",folder, "-iname", "*.dcm", "-print", "-quit"],stdout=subprocess.PIPE)
		dicom_file = dicom.stdout.read()
		if(len(dicom_file)>0):
			l_dicoms.append(dicom_file.replace("\n",""))
	return l_dicoms

def get_dicom_data(tags,file_):
	# Get tags from DICOM file
	res={}
	data = dicom.read_file(file_)
	for tag in tags:
		tag_parts = tag.split(",")
		tag_data= data[tag_parts[0],tag_parts[1]].value
		res[tag]=tag_data
	return res

if __name__ == "__main__":
	print ''
	if len(sys.argv[1:]) == 2:
		full_path_dicom = sys.argv[1]
		output_folder = sys.argv[2]
		res=get_ids(full_path_dicom,output_folder)
		if res == 1:
			sys.exit(1)
		else:
			sys.exit(0)
	else:
		print 'Incorrect arguments number'
		sys.exit(1)
	

