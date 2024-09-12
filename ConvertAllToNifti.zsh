#! /bin/zsh

IFS=$'\n'

for studyFolder in $(cat GoodDicomFolderList.txt); do
    subject=$studyFolder:h:h:t:t:t
    outDir="D:/CQ500/ConvOuch-master/ConvOuch-master/NiftiFiles/"
    
    if [ ! -d "${outDir}${subject}" ]; then
        mkdir "${outDir}${subject}"
    fi
    
    # Now, dcm2niix command will expand the *.dcm properly
    dcm2niix -z y -m y -o "${outDir}${subject}/" "${studyFolder}"/*.dcm
done
