#!/bin/bash
set -ex

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

here="$(dirname "${BASH_SOURCE[0]}")"
src=$1
dest=$2
img_name=$3
fn=$(basename "$src")
ext="${fn##*.}"
name="${fn%.*}"
realname=$(finger `whoami` | awk -F: '{ print $3 }' | head -n1 | sed 's/^ //')
hostname=$(hostname -s)
hostip=$(dig +short myip.opendns.com @resolver1.opendns.com)
dashes=$(printf '%*s' 77 | tr ' ' '-')
logit() {
    local history="$1"/history.log
    gecho -e "$(gdate -u --iso-8601=seconds) $2" >> ${history}
}

generate_checksums() {
    local dirn=$(dirname "$1")
    local fn=$(basename "$1")
    local ext="${fn##*.}"
    local name="${fn%.*}"
    local shaname="${name}.sha512"
    local sha512=$(gsha512sum -b "$1" | awk '{print $1;}')
    echo "$sha512  $fn" > "${dirn}/$shaname"
    logit "$dirn" 'generated checksum file '"$shaname"' for file '"$fn"
}

identify_with_jhove() {
    local dirn=$(dirname "$1")
    local fn=$(basename "$1")
    local ext="${fn##*.}"
    local name="${fn%.*}"
    local jhove_path="${dirn}/${name}_jhove.xml"
    "$JHOVEHOME/jhove" -h xml -ks -o "$jhove_path" "$1"
    logit "$dirn" 'generated jhove report file '"$(basename $jhove_path)"' for file '"$fn"
    generate_checksums "$jhove_path"
}

extract_metadata() {
    local dirn=$(dirname "$1")
    local fn=$(basename "$1")
    local ext="${fn##*.}"
    local name="${fn%.*}"
    local exiftool_path="${dirn}/${name}_exiftool.xml"
    exiftool -q -X -struct -u "$1" > "$exiftool_path"
    logit "$dirn" 'generated exiftool report file '"$(basename $exiftool_path)"' for file '"$fn"
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

# copy original to destination (verify with checksum)
if [ "$img_name" != '' ]; then
    imgid="$img_name"
else
    imgid="$name"
fi
target="$dest/$imgid"
mkdir -p "$target"
touch "$target"/history.log

logit $target '\nISAW AWIB package '"$imgid created by $realname ($USER@$hostname=$hostip) using the 'accession.sh' script from isaw.awib to create an AWIB-style package from the unmanaged image $src."
original="$target/original.$ext"
safecopy "$src" "$original"
logit $target "copied $src to $(basename $original)"

# capture information about the original image file
generate_checksums "$original"
identify_with_jhove "$original"
extract_metadata "$original"


# make a master tiff file, copy embedded data, and capture information about it
master="$target/master.tif"
python "$PYTHONPATH/scripts/make_master.py" -q "$original" "$master"
logit $target 'generated master.tif from '"$(basename $original))"' using '"$PYTHONPATH"'/scripts/make_master.py'
exiftool -q -tagsfromfile "$original" -all:all "$master"
# don't bother checksuming until we've added GUID, below
identify_with_jhove "$master"
extract_metadata "$master"

# instantiate metadata file
saxon -s:"${target}/original_exiftool.xml" -xsl:"$here"/exiftool2meta.xsl -o:"$target"/metadata.xml agent="$realname" jhove_file="${dirn}/original_jhove.xml" iptc_name="$img_name"
logit $target 'created metadata.xml file using isaw.awib/scripts/exiftool2meta.xsl to transform metadata extracted with exiftool and with jhove.'
bash "$here"'/make_guid.sh' "$target"
logit $target 'generated and assigned a GUID to this image'
generate_checksums "$master"
generate_checksums "$target"/metadata.xml
logit $target 'ACCESSION COMPLETE: IMAGE PACKAGING COMPLETE\n# '"$dashes"
"$here"/validate.sh "$target"
logit $target 'Package successfully validated with isaw.awib/scripts.validate.sh.'

exit
