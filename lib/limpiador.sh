#!/bin/bash

#script de test, limpia archivos, comparadolos con una lista negra


#Uso
#
#bash limpiador_VVD17RA03.sh 
#_reg_borrado="/home/cafetero/logs/registro_limpieza_VVD17RABIOBANCO03_$(date +"%m_%d_%Y__%H-%M").log"
#PATH_RECOLECTOR="/home/cafetero/ceibanon/data_ra600/VVD17RABIOBANCO03"
function test_cleaner() {
	
	CABECERA_DICOM=$(gdcmdump $1)
	#SERIE_DESCRIPTION=$(gdcmdump $1 | grep '0008,103e')
	SERIE_DESCRIPTION=$(echo "$CABECERA_DICOM" | grep '0008,103e')
	MODALIDAD=$(echo "$CABECERA_DICOM" | grep '0008,0060')
	##########lista negra
	declare -a list=("patient aligned mpr awplan_smartplan_type_brain" "survey" "examcard" "screen save" "cal scan" "reformatted" "sorted" "calibration" "processed images" "pasted images" "LOCALIZADOR" "ASSET Cal" "AxPROBESVPRESS35TES" "AxPROBESVPRESS144TES" "ScreenSave" "ASSETCal" "s3D_CAROTIDS" "sSUSTRACCION" "LOCCEREBRAL" "LOCCERVICAL" "CALIBRACION" "VEN_3D_PCA" "LOCALIZER" "loc" "Informe" "LST" "ReportSC")
	#####################
	if [[ $MODALIDAD = *"[SR]"* ]]; then
		echo -e "$1 \nborrado, debido modalidad: SR\n\n"
		rm $1
	elif [[ $MODALIDAD = *"[PR]"* ]]; then
		echo -e "$1 \nborrado, debido modalidad: PR\n\n"
		rm $1
	elif [[ $MODALIDAD = *"[OT]"* ]]; then
		echo -e "$1 \nborrado, debido modalidad: OT\n\n"
		rm $1
	elif [[ $MODALIDAD = *"[CS]"* ]]; then
		echo -e "$1 \nborrado, debido modalidad: CS\n\n"
		rm $1
	else
		for item in "${list[@]}"
		do
				#echo -e "${item,,}\n"
				#echo -e "${SERIE_DESCRIPTION,,}\n"
				#if [[ $SERIE_DESCRIPTION = *"$item"* ]]; then
				if [[ "${SERIE_DESCRIPTION,,}" = *"${item,,}"* ]]; then # busco comparar todo en minusculas
					echo -e "$1 \nborrado, contiene elemento: $item\n\n" 
					rm $1
					break
				fi
		done
	fi
}
export -f test_cleaner
#find -L $PATH_RECOLECTOR -iname "*.dcm" -exec bash -c 'test_cleaner "$0"' {} \;
#find -L $PATH_RECOLECTOR -iname "*.dcm" | parallel --halt 1 test_cleaner 2> >(tee -a $_reg_borrado) >> $_reg_borrado
#{ #try
#	find -L $PATH_RECOLECTOR -iname "*.dcm" | parallel --halt 1 test_cleaner >> $_reg_borrado 2>&1 
#}||{ #catch
#	return 1
#}
