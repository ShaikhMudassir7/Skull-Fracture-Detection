#!/bin/bash

# Unzip and reorganize for a range of folders
process_folders() {
    local base_name="CQ500-CT"
    local start=0
    local end=400
    local zip_extension=".zip"

    for i in $(seq $start $end); do
        local folder="${base_name}-${i}"
        local zip_file="${folder}${zip_extension}"
        local dest="${folder}"

        # Unzip the archive
        unzip "$zip_file" -d "$dest/"

        # Check if the destination has only one subdirectory
        if [[ $(ls "$dest" | wc -l) == 1 ]]; then
            local subdir; subdir=$(ls "$dest")
            mv "$dest/$subdir/"* "$dest/"
            rmdir "$dest/$subdir"
        fi
    done
}

main() {
    process_folders
}

main
