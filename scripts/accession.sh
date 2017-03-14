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
    gsha512sum -b "$1" > "$2.sha512"
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
cp "$src" "$original"
src_sum=$(gmd5sum -b "$src" | awk '{print $1;}')
dest_sum=$(gmd5sum -b "$original" | awk '{print $1}')
if [ "$src_sum" != "$dest_sum" ]
then
    echo "copy from $src to $original failed on checksum verification"
    exit 40
fi

# capture information about the original image file
generate_checksums "$original" "$target/original"
$JHOVEHOME/jhove -h xml -ks -o "$target/original_jhove.xml" "$original"
exiftool -X -struct -u "$original" > "$target/original_exiftool.xml"

# make a master tiff file and capture information about it
master="$target/master.tif"
python "$PYTHONPATH/scripts/make_master.py" -q "$original" "$master"
generate_checksums "$master" "$target/master"
$JHOVEHOME/jhove -h xml -ks -o "$target/master_jhove.xml" "$master"
exiftool -X -struct -u "$master" > "$target/master_exiftool.xml"

exit
