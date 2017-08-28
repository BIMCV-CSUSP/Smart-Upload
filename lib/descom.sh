#!/bin/bash

#script de comprobacion si la imagen DICOM esta comprimida
#y la devuelve en raw

#Uso
#
#bash descompresionDICOM.sh 
#_log="/home/cafetero/logs/registro_descom_VVD17RABIOBANCO03_$(date +"%m_%d_%Y__%H-%M").log"
#PATH_RECOLECTOR="/home/cafetero/ceibanon/data_ra600/VVD17RABIOBANCO03"
function testYdescSobreSiMismo() {
	#echo "$1"
	#CHECK_COMPRESSED=$(gdcminfo --check-compression $1 | grep 'TransferSyntax is 1.2.840.10008.1.2.1')
	# TRANSFER_SYNTAX_UID=$(gdcminfo --check-compression $1 | grep 'TransferSyntax is')
	
	# case "$TRANSFER_SYNTAX_UID" in
		# 'TransferSyntax is 1.2.840.10008.1.2 [Implicit VR Endian: Default Transfer Syntax for DICOM]')
			# echo $TRANSFER_SYNTAX_UID
			# echo -e "No descomprimo\n"
			# ;;
		# 'TransferSyntax is 1.2.840.10008.1.2.1 [Explicit VR Little Endian]')
			# echo $TRANSFER_SYNTAX_UID
			# echo -e "No descomprimo\n"
			# ;;	
		# 'TransferSyntax is 1.2.840.10008.1.2.1.99 [Deflated Explicit VR Little Endian]')
			# echo $TRANSFER_SYNTAX_UID
			# echo -e "No descomprimo\n"
			# ;;
		# 'TransferSyntax is 1.2.840.10008.1.2.2 [Explicit VR Big Endian]')
			# echo $TRANSFER_SYNTAX_UID
			# echo -e "No descomprimo\n"
			# ;;	
		# *)
			# echo $TRANSFER_SYNTAX_UID
			# gdcmconv --raw -i $1 -o $1
			# echo -e "Descomprimo\n"			
			# ;;
	# esac
	testAndDecompress $1 $1
}
export -f testYdescSobreSiMismo

function testAndDecompress(){
	echo "$1"
	#CHECK_COMPRESSED=$(gdcminfo --check-compression $1 | grep 'TransferSyntax is 1.2.840.10008.1.2.1')
	TRANSFER_SYNTAX_UID=$(gdcminfo --check-compression $1 | grep 'TransferSyntax is')
	
	case "$TRANSFER_SYNTAX_UID" in
		'TransferSyntax is 1.2.840.10008.1.2 [Implicit VR Endian: Default Transfer Syntax for DICOM]')
			echo $TRANSFER_SYNTAX_UID
			echo -e "No descomprimo\n"
			;;
		'TransferSyntax is 1.2.840.10008.1.2.1 [Explicit VR Little Endian]')
			echo $TRANSFER_SYNTAX_UID
			echo -e "No descomprimo\n"
			;;	
		'TransferSyntax is 1.2.840.10008.1.2.1.99 [Deflated Explicit VR Little Endian]')
			echo $TRANSFER_SYNTAX_UID
			echo -e "No descomprimo\n"
			;;
		'TransferSyntax is 1.2.840.10008.1.2.2 [Explicit VR Big Endian]')
			echo $TRANSFER_SYNTAX_UID
			echo -e "No descomprimo\n"
			;;	
		*)
			echo $TRANSFER_SYNTAX_UID
			gdcmconv --raw -i $1 -o $2
			echo -e "Descomprimo\n"			
			;;
	esac
}
export -f testAndDecompress



#find -L $PATH_RECOLECTOR -iname "*.dcm" -exec bash -c 'testYdescSobreSiMismo "$0"' {} \;
#find -L $PATH_RECOLECTOR -iname "*.dcm" | parallel  bash -c testYdescSobreSiMismo  {}
#find -L $PATH_RECOLECTOR -iname "*.dcm" | parallel --halt 1 testYdescSobreSiMismo 2> >(tee -a $_reg_descom) >> $_reg_descom
#{ #try
#	find -L $PATH_RECOLECTOR -iname "*.dcm" | parallel --halt 1 testYdescSobreSiMismo >> $_reg_descom 2>&1
#}||{ #catch
#	return 1
#}
#find -L $PATH_RECOLECTOR -iname "*.dcm" | parallel --dryrun --progress testYdescSobreSiMismo
