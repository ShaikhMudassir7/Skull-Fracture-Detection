#!/bin/bash

IFS=$'\n'

while read -r studyFolder; do
    subject=$(basename "$(dirname "$(dirname "$studyFolder")")")
    outDir="D:/CQ500/NiftiFiles/"
    
    if [ ! -d "${outDir}${subject}" ]; then
        mkdir "${outDir}${subject}"
    fi
    
    echo "dcm2niix -z y -m y -o \"${outDir}${subject}/\" \"${studyFolder}\"/*.dcm"
done < GoodDicomFolderList.txt