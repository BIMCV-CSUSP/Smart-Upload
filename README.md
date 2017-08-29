# Smart-Upload

Script for uploading dicom files to xnat. This script will clean and decompress the images before uploading them to the ctp. Then, the ctp anonymizes and uploads the files to the xnat platform.

## Previous steps

Before launching the script there are some points to take in account. First, you will need to make a file to describe the info that is independent of the project:

* src_name: this is the root folder where the images are found. This folder will be searched in /mnt
* dst_name: this is the folder where all the logs will be saved. Same as before (in process to move the searched folder to /mnt)
* port: port of the ctp
* pipelines: ctp folder where its own scripts are found

Second, you will need to copy the images to the source folder. There are some ways to organize these folders that will be explained  later.

## Usage

Basic usage:
``` [sh]
./maestro.sh -m machine -p project [-d department]
```
This will all search the images in the source directory. The department is only needed for organizational purposes. If no specified, this will save the logs in destination/project. Otherwise, project will be ignored and department will be used as the project name and saving the logs in destination/project/department
