#!/bin/bash
set -e

fail () {
    gecho -e 'INVALID: '"$1"
    exit 1
}

# valid the package directory itself
where=$1
if [ ! -d "$where" ]; then
    fail "$where"' must be a directory'
fi

# verify that minimum expected content is present
declare -a expected=(
    'history.log'
    'master.sha512'
    'master.tif'
    'master_exiftool.sha512'
    'master_exiftool.xml'
    'master_jhove.sha512'
    'master_jhove.xml'
    'metadata.sha512'
    'metadata.xml'
    'original.sha512'
    'original_exiftool.sha512'
    'original_exiftool.xml'
    'original_jhove.sha512'
    'original_jhove.xml')
for fn in "${expected[@]}"
do
    if [ ! -f "$where"/"$fn" ]; then
        fail "$fn"' must be a regular file in the package directory ('"$where"')'
    fi
done

# verify that master.tif and original.* are image files
magic=`file "$where"/master.tif |awk -F: '{print $2}'`
if [[ $magic != *"image"* ]] && [[ $magic != *"bitmap"* ]]; then
    fail 'master.tif is not an image file ('"$magic"')'
fi
for orig in `find "${where}" -type f -name 'original.*'`
do
    fn=$(basename "$orig")
    ext="${fn##*.}"   
    if [ "$ext" != 'sha512' ]; then
        magic=`file "$orig" |awk -F: '{print $2}'`
        if [[ $magic != *"image"* ]] && [[ $magic != *"bitmap"* ]]; then
            fail "$fn"' is not an image file ('"$magic"')'
        fi
    fi
done

# verify all checksums
hashfiles=($where/*.sha512)
for hashfile in ${hashfiles[@]}
do
    hash_fn=$(basename "$hashfile")
    hash_ext="${hash_fn##*.}"
    hash_name="${hash_fn%.*}"
    old_sum=$(cat "$hashfile" | awk '{print $1;}')
    matching_files=($where/$hash_name.*)
    for mf in ${matching_files[@]}
    do
        match_fn=$(basename "$mf")
        match_ext="${match_fn##*.}"
        if [ "$match_ext" != 'sha512' ]; then
            new_sum=$(gsha512sum -b "${mf}" | awk '{print $1;}')
            if [ "$old_sum" != "$new_sum" ]; then
                fail 'checksum verification on '"$match_fn"' failed'
            fi
        fi
    done
done

exit
