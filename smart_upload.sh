#!/bin/bash

# script que lanza limpiador, descomprimir, obtener id y subir.
# este script incluye los paths que serán los que usen el resto.
# precaucion con el slash final de los paths

_path_lib="./lib/"


printHelpAndExit(){
	echo "Usage: ./maestro.sh -m machine -p project [-d department]"
	echo ""
	echo "-m, --machine 		machine file to use"
	echo "-p, --project 		project name"
	echo "-d, --department 	department name"
	echo "-f, --folder		search the DICOM images in source/project/department"
	echo "-a, --all 		upload ALL the projects that are in source folder.
			The projects need to be in a folder tree like source/project/department"
	echo "-b, --batches		upload in batches of the specified size. This will make the script wait until the batches are fully uploaded before upload the next batch"
	echo "--help			print this help and exit"
	exit 0
}


###############################
# trim all spaces from start and end of a string
###############################
trim(){
	#auxiliar variable
	#read var
	var="$*"
	#trim from start
	var="${var#"${var%%[![:space:]]*}"}"
	#trim from end
	var="${var%"${var##*[![:space:]]}"}"
	
	echo "$var"
}

source "$_path_lib"limpiador.sh
source "$_path_lib"descom.sh


#parse arguments
while [ $# -gt 0 ]; do
	case $1 in
		-m | --machine) MACHINE_FILE=$2; shift 2;;
		-p | --project) PROJECT=$2; shift 2;;
		-d | --department) DEPARTMENT=$2; shift 2;;
		-f | --folder) SEARCH_IN_FOLDER="true"; shift 1;;
		-a | --all) SEARCH_IN_FOLDER="true"; SELECT_ALL="true"; shift 1;;
		-b | --batches)  UPLOAD_IN_BATCHES=$2; shift 2;;
		*) printHelpAndExit;;
	esac
done

#check if machine is empty
if [ -z "$MACHINE_FILE" ]; then
	echo "You have to select a machine and a project"
	exit 0
fi

#check if project is empty and search projects is no selected 
if [ -z "$SEARCH_IN_FOLDER"  -a -z "$PROJECT" ]; then
	echo "You have to select a project or use --all option"
	exit 0
fi

#check if machine file exists
if [ ! -f machines/$MACHINE_FILE  ]; then
	echo "The machine selected don't exists"
	exit 0
fi

#parse the file
#first, get all the lines wich start by the key, split them and take the second field
#then, get the last line (just in case there are multiple occurences of the key)
SOURCE=`awk -F: '/^\ysrc_name\y/ { print $2 }' machines/$MACHINE_FILE | tail -n 1`
DEST=`awk -F: '/^\ydst_name\y/ { print $2 }' machines/$MACHINE_FILE | tail -n 1`
PIPELINES=`awk -F: '/^\ypipelines\y/ { print $2 }' machines/$MACHINE_FILE | tail -n 1`
PORT=`awk -F: '/^\yport\y/ { print $2 }' machines/$MACHINE_FILE | tail -n 1`

SOURCE=`trim "$SOURCE"`
DEST=`trim "$DEST"`
PIPELINES=`trim "$PIPELINES"`
PORT=`trim "$PORT"`

#check if all fields are ok
if [ -z "$SOURCE" -o -z "$DEST" -o -z "$PIPELINES" -o -z "$PORT" ]; then
	echo "The specified file is incorrect or incomplete"
	exit 0
fi

SOURCE_PATH="/home/cafetero/ceibanon/data_ra600/${SOURCE}/"
DEST_PATH="/mnt/${DEST}/"

#libs

_puerto=$PORT

PATH_ANONYMIZATION="/home/cafetero/ceibanon/ctp_pipelines/${PIPELINES}/scripts/anonymization.script"
PATH_TEMPLATE="/home/cafetero/ceibanon/ctp_pipelines/${PIPELINES}/scripts/template_anonymization.script"

#check if search for projects is enabled
if [ -z $SELECT_ALL ] ; then
	#if not, build an array of a single project
	BUILDING_PATH="${PROJECT}/"
	if [ ! -z "$DEPARTMENT" ]; then
		BUILDING_PATH="${BUILDING_PATH}${DEPARTMENT}/"
	fi
	PROJECTS_PATHS=("$BUILDING_PATH")
else
	#Search for all folders that contains a DICOMDIR file (ie. dicom folders), convert the absolute path to a relative path and take only the first two folders.
	# last, remove duplicates
	mapfile -t PROJECTS_PATHS < <(find $SOURCE_PATH -maxdepth 4 -mindepth 4 -iname dicomdir |\
	                                                   sed "s|$SOURCE_PATH||g" |  awk -F/ '{print $1"/"$2"/"}'|\
	                                                   sort | uniq)
	#same but consider that department is not specified
	mapfile -t PROJECTS_PATHS_2 < <(find $SOURCE_PATH -maxdepth 3 -mindepth 3 -iname dicomdir |\
	                                                      sed "s|$SOURCE_PATH||g" |  awk -F/ '{print $1"/"}'|\
	                                                      sort | uniq)
	#merge the variables
	PROJECTS_PATHS+=("${PROJECTS_PATHS_2[@]}")
	
	if [[ -z "${PROJECTS_PATHS[@]}" ]]; then
		echo "Couldn't find any project"
	fi
fi

echo "Using ${PIPELINES}"
echo "With source folder ${SOURCE_PATH}"
echo "And destination folder ${DEST_PATH}"

echo "These projects will be uploaded (Project/department):"
for TEXT in "${PROJECTS_PATHS[@]}"; do
	echo -e "  > $TEXT"
done

ANSWER=""
echo "Is this true?"
read ANSWER
if [[ ! "${ANSWER,,}" =~ ^(si|s|yes|y)$ ]]; then
	exit 0
fi

FAILED=()
ERRORS=()

for PROJECT_PATH in "${PROJECTS_PATHS[@]}"; do

	PATH_RECOLECTOR="${SOURCE_PATH}"
	#if search in project folder is enabled, append the project folder to the recolector path
	if [ ! -z "$SEARCH_IN_FOLDER" ]; then PATH_RECOLECTOR="${PATH_RECOLECTOR}${PROJECT_PATH}"; fi
	COMMON="${DEST_PATH}${PROJECT_PATH}"

	
	#check if the free space is enough to store the uncompresed images
	#save the free space in source path
	FREE_SPACE=`df -P ${PATH_RECOLECTOR} | awk 'NR==2 {print $4}'`
	#chek all if batches is not active
	if [[ -z "$UPLOAD_IN_BATCHES" ]]; then
		#save the space used by the compressed images
		SPACE_USED=`du -cs ${PATH_RECOLECTOR} | tail -1 | cut -f 1`
		#since the images are going to be reemplaced when we decompress, we will need only 2 times the compressed size
		DECOMPRESSED_SPACE_USED=$(( $SPACE_USED * 3 ))
		NEEDED_SPACE=$(( $DECOMPRESSED_SPACE_USED - $SPACE_USED ))
		if [ $NEEDED_SPACE -gt $FREE_SPACE ]; then
			ANSWER=""
			echo "The free space is probably less than the space needed. Are you sure you want to continue?"
			read ANSWER
			if [[ ! "${ANSWER,,}" =~ ^(si|s|yes|y)$ ]]; then
				exit 0
			fi
		fi
	else 
		# save the space needed
		# first, find all the dicom files and calcule the size of each one
		# take out the total from the results
		# sort the list by size
		# take only the last n files (the bigger) where n is the batch size
		# and use awk to sum all the sizes
		SPACE_USED=`find -L "$PATH_RECOLECTOR" -iname "*.dcm" -exec du -sc {} + | head -n -1 | sort -n | tail -"$UPLOAD_IN_BATCHES" | awk '{ total += $1} END {print total}'`
		NEEDED_SPACE=$(( $SPACE_USED * 3 ))
		if [ $NEEDED_SPACE -gt $FREE_SPACE ]; then
			ANSWER=""
			echo "The free space is probably less than the space needed. Are you sure you want to continue?"
			read ANSWER
			if [[ ! "${ANSWER,,}" =~ ^(si|s|yes|y)$ ]]; then
				exit 0
			fi
		fi

	
	fi
	
	
	#cleaner
	_reg_borrado="${COMMON}registro_limpieza_${SOURCE}_$(date +"%m_%d_%Y__%H-%M").log"
	#decompression
	_reg_descom="${COMMON}registro_descom_${SOURCE}_$(date +"%m_%d_%Y__%H-%M").log"
	#uploading
	_reg_subida="${COMMON}upload_${SOURCE}_$(date +"%m_%d_%Y__%H-%M").log"

	#chek if the source folder exist
	if [ ! -d $PATH_RECOLECTOR ]; then
		echo "Data source folder don't exists"
		exit 0
	else
		#get the number of folders in source
		num=$(ls -F $PATH_RECOLECTOR | grep / | wc -l)
		if [ $num -gt 0 ]; then
			echo "$num folders found into $PATH_RECOLECTOR" 
		else
			#exit if no folders
			echo "Nothing found into $PATH_RECOLECTOR"
			exit 0
		fi
	fi

	if [ ! -d $COMMON ]; then
		mkdir -p $COMMON
		echo "mkdir -p $COMMON"
	fi
	
	

	
	DEPARTMENT=`echo $PROJECT_PATH | awk -F/ '{print $2}'`
	PROJECT=`echo $PROJECT_PATH | awk -F/ '{print $1}'`
	if [ -z "$DEPARTMENT" ]; then
		sed "s/PROJECT_NAME_TEMPLATE/${PROJECT}/g" $PATH_TEMPLATE > $PATH_ANONYMIZATION
	else
		sed "s/PROJECT_NAME_TEMPLATE/${DEPARTMENT}/g" $PATH_TEMPLATE > $PATH_ANONYMIZATION
	fi

	DICOM_LIST=`find -L $PATH_RECOLECTOR -iname "*.dcm"`
		
	#cleaning
	echo "$(date +"%m_%d_%Y__%H-%M") cleaning..."
	{ #try
		#source "$_path_lib"limpiador.sh
		echo "$DICOM_LIST" | parallel --halt 1 test_cleaner >> $_reg_borrado 2>&1 
	}||{ #catch
		#if fail, store the project name and continue with the next project
		echo "Unexpected error while cleaning"
		FAILED+=($PROJECT_PATH)
		ERRORS+=("Unexpected error while cleaning")
		continue
	}
	
	
	DICOM_LIST=`find -L $PATH_RECOLECTOR -iname "*.dcm"`

	#get ids
	echo "$(date +"%m_%d_%Y__%H-%M") taking ids..."
	#source get_ids_angel.sh
	python "${_path_lib}get_ids.py" $PATH_RECOLECTOR $COMMON

	if [[ -z "$UPLOAD_IN_BATCHES" ]]; then
		#decompress
		echo "$(date +"%m_%d_%Y__%H-%M") decompressing..."
		{ #try

			echo "$DICOM_LIST" | parallel --halt 1 testYdescSobreSiMismo >> $_reg_descom 2>&1
		}||{ #catch
			#if fail, store the project name and continue with the next project
			echo "Unexpected error while decompresing"
			FAILED+=($PROJECT_PATH)
			ERRORS+=("Unexpected error while decompresing")
			continue
		}
		
		#check if the xnat is running
		#this will check if the xnat page is down
		PAGE=`wget "https://ceib.cipf.es/xnat/" --no-check-certificate -qO-`
		if [ -z "$PAGE" ]; then
			echo "XNAT seems down, continue anyway?"
			ANSWER=""
			read ANSWER
			if [[ ! "${ANSWER,,}" =~ ^(si|s|yes|y)$ ]]; then
				exit 0
			fi
		fi
		
		#upload
		echo "$(date +"%m_%d_%Y__%H-%M") uploading to xnat..."
		{ #try
			#source "$_path_lib"subida.sh
			
			echo "$DICOM_LIST" | xargs -I {} gdcmscu  -V --store 10.192.176.74 $PORT -i {}   >> $_reg_subida 2>&1
			echo "Upload completed"
		}||{ #catch
			#if fail, store the project name and continue with the next project
			echo "Unexpected error while uploading"
			FAILED+=($PROJECT_PATH)
			ERRORS+=("Unexpected error while uploading")
			continue
		}
	else

		#Get the number of DICOM images 
		NUMBER_OF_DICOMS=`echo "$DICOM_LIST" | wc -l`
		#echo "$DICOM_LIST"
		echo "$(date +"%m_%d_%Y__%H-%M") decompressing and uploading..."

		
		for (( ACTUAL_DICOM=1 ; ACTUAL_DICOM<=NUMBER_OF_DICOMS ; ACTUAL_DICOM+=UPLOAD_IN_BATCHES )) ; do
		

			#get the actual batch of dicom images
			REDUCED_LIST=`echo "$DICOM_LIST" | sed -n "$ACTUAL_DICOM,$((ACTUAL_DICOM + UPLOAD_IN_BATCHES - 1 ))p"`
			
			
			
			#copy the files to uncompress
			echo "$REDUCED_LIST" | while read FILE; do
				#copy the file to the same directory appending _decompressed before the type
				cp "$FILE"  "${FILE/.[dD][cC][mM]/.decompressed.dcm}"
			done
			
			DECOMPRESSED_FILES_LIST=`find -L $PATH_RECOLECTOR -iname "*.decompressed.dcm"`
			#echo "$DECOMPRESSED_FILES_LIST"
			#decompress
			{ #try

				echo "$DECOMPRESSED_FILES_LIST" | parallel --halt 1 testYdescSobreSiMismo >> $_reg_descom 2>&1
			}||{ #catch
				#if fail, store the project name and continue with the next project
				echo "Unexpected error while decompresing"
				FAILED+=($PROJECT_PATH)
				ERRORS+=("Unexpected error while decompresing")
				continue 2
			}
			
			
			#check if the xnat is running
			#this will check if the xnat page is down
			PAGE=`wget "https://ceib.cipf.es/xnat/" --no-check-certificate -qO-`
			if [ -z "$PAGE" ]; then
				echo "XNAT seems down, continue anyway?"
				ANSWER=""
				read ANSWER
				if [[ ! "${ANSWER,,}" =~ ^(si|s|yes|y)$ ]]; then
					exit 0
				fi
			fi
			
			#upload
			#echo "$(date +"%m_%d_%Y__%H-%M") uploading to xnat..."
			{ #try
				#source "$_path_lib"subida.sh
				
				echo "$DECOMPRESSED_FILES_LIST" | xargs -I {} gdcmscu  -V --store 10.192.176.74 $PORT -i {}   >> $_reg_subida 2>&1
				#echo "Upload completed"
			}||{ #catch
				#if fail, store the project name and continue with the next project
				echo "Unexpected error while uploading"
				FAILED+=($PROJECT_PATH)
				ERRORS+=("Unexpected error while uploading")
				continue 2
			}
			

			
			#read the ctp page and take the pending files for the curent pipelines
			IMPORTING_QUEUE=`wget -qO- localhost:8666/summary?suppress | grep ">$PIPELINES<" |   grep -o '>[0-9][0-9]*<' | head -n 1 | sed 's/[<>]//g'`
			EXPORTING_QUEUE=`wget -qO- localhost:8666/summary?suppress | grep ">$PIPELINES<" |   grep -o '>[0-9][0-9]*<' | head -n 1 | sed 's/[<>]//g'`
			#if there are some, wait until all has been uploaded
			echo -n -e "Still left $IMPORTING_QUEUE in the iport queue and $EXPORTING_QUEUE in the export queue\r"
			while (( IMPORTING_QUEUE > 0 || EXPORTING_QUEUE > 0 )); do
				sleep 0.5 
				IMPORTING_QUEUE=`wget -qO- localhost:8666/summary?suppress | grep ">$PIPELINES<" |   grep -o '>[0-9][0-9]*<' | head -n 1 | sed 's/[<>]//g'`
				EXPORTING_QUEUE=`wget -qO- localhost:8666/summary?suppress | grep ">$PIPELINES<" |   grep -o '>[0-9][0-9]*<' | head -n 1 | sed 's/[<>]//g'`
				#show the remaining images to upload
				#this will use escape codes to write over the same line
				#https://en.wikipedia.org/wiki/ANSI_escape_code
				echo -n -e "\033[2KStill left $IMPORTING_QUEUE in the iport queue and $EXPORTING_QUEUE in the export queue\r"
			done
			echo -n -e "\033[2KBatch completed ( $(( ACTUAL_DICOM / UPLOAD_IN_BATCHES + 1 ))/$(( ( NUMBER_OF_DICOMS + UPLOAD_IN_BATCHES - 1 ) / UPLOAD_IN_BATCHES )) )\r"
			
			#delete the temporal files used
			rm $(echo $DECOMPRESSED_FILES_LIST)
		done
		echo -e "\033[2KUpload complete"
	fi		
	echo "" 

done

#show errors if something failed
if [[ ! -z "${FAILED[@]}" ]]; then
	echo "The next projects have errors"
	for INDEX in "{!FAILED[@]}"; do
		echo -e "${FAILED[$INDEX]}: \t\t\t${ERRORS[$INDEX]}"
	done
	
else

	echo "$(date +"%m_%d_%Y__%H-%M") All projects uploaded without errors"

fi

