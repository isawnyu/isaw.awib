#!/bin/bash
set -e

if [ -z ${JHOVEHOME+x} ]
then 
    echo "the JHOVEHOME environment variable is not set"
    exit 10
fi
if [ -z ${PYTHONPATH+x} ]
then 
    echo "the PYTHONPATH environment variable is not set"
    exit 20
fi
pyver=$(python -c 'import sys; print(sys.version_info[:])')
soughtver="(3, 6, 0, 'final', 0)"
if [ "$pyver" != "$soughtver" ]
then
    echo "unexpected python version: $pyver"
    exit 30
fi

generate_checksums() {
    local dirn=$(dirname "$1")
    local fn=$(basename "$1")
    local ext="${fn##*.}"
    local name="${fn%.*}"
    local shaname="${name}.sha512"
    local sha512=$(gsha512sum -b "$1" | awk '{print $1;}')
    echo "$sha512  $fn" > "${dirn}/$shaname"
}

identify_with_jhove() {
    local dirn=$(dirname "$1")
    local fn=$(basename "$1")
    local ext="${fn##*.}"
    local name="${fn%.*}"
    local jhove_path="${dirn}/${name}_jhove.xml"
    "$JHOVEHOME/jhove" -h xml -ks -o "$jhove_path" "$1"
    generate_checksums "$jhove_path"
}

extract_metadata() {
    local dirn=$(dirname "$1")
    local fn=$(basename "$1")
    local ext="${fn##*.}"
    local name="${fn%.*}"
    local exiftool_path="${dirn}/${name}_exiftool.xml"
    exiftool -X -struct -u "$1" > "$exiftool_path"
    generate_checksums "$exiftool_path"
}

safecopy () {
    cp -p $1 $2
    local src_sum=$(gmd5sum -b "$1" | awk '{print $1;}')
    local dest_sum=$(gmd5sum -b "$2" | awk '{print $1}')
    if [ "$src_sum" != "$dest_sum" ]
    then
        echo "copy from $1 to $2 failed on checksum verification"
        exit 40
    fi
}

src=$1
dest=$2
fn=$(basename "$src")
ext="${fn##*.}"
name="${fn%.*}"

# copy original to destination (verify with checksum)
target="$dest/$name"
mkdir "$target"
temp="$target/.tmp"
mkdir "$temp"
original="$target/original.$ext"
safecopy "$src" "$original"

# capture information about the original image file
generate_checksums "$original"
identify_with_jhove "$original"
extract_metadata "$original"

# make a master tiff file and capture information about it
master="$target/master.tif"
python "$PYTHONPATH/scripts/make_master.py" -q "$original" "$master"
generate_checksums "$master"
identify_with_jhove "$master"
extract_metadata "$master"

exit
