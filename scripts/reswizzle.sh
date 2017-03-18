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
    echo 'unexpected python version: '"$pyver"'; '"$soughtver"' is required.'
    exit 30
fi
here="$(dirname "${BASH_SOURCE[0]}")"
src=$1
dest=$2
colln=$(basename "$src")
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
    exiftool -X -struct -u "$1" > "$exiftool_path"
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

copy_master () {
    local from="${1}/masters/${2}-${3}-master.tif"
    local to="${4}/old_master.tif"
    safecopy $from $to
    generate_checksums $to
    logit $4 "successfully copied $from to $(basename $to)"
    local from="${1}/masters/${2}-${3}-master-jhove.xml"
    local to="${4}/old_master_jhove.xml"
    safecopy $from $to
    logit $4 "copied $from to $(basename $to)"
    generate_checksums $to
}

copy_meta () {
    local from="${1}/meta/${2}-${3}-meta.xml"
    local to="${4}/old_metadata.xml"
    safecopy $from $to
    logit $4 "copied $from to $(basename $to)"
    generate_checksums $to
    saxon -s:"$to" -xsl:"$here"/update_metadata.xsl -o:"$4"/metadata.xml operator="$realname"
    # don't bother generating checksum now; wait till after guid generation 
}

copy_original () {
    for orig in `find "${1}/originals/" -type f -name ''"${2}-${3}"'-original.*'`
    do
        local origfn=$(basename "$orig")
        local ext="${origfn##*.}"
        local from="${1}/originals/${2}-${3}-original.${ext}"
        local to="${4}/original.${ext}"
        safecopy $from $to
        generate_checksums $to
        logit $4 "successfully copied $from to $(basename $to)"
    done
    local from="${1}/originals/${2}-${3}-original-jhove.xml"
    local to="${4}/original_jhove.xml"
    safecopy $from $to
    logit $4 "copied $from to $(basename $to)"
    generate_checksums $to
    local from="${1}/originals/${2}-${3}-original-exiftool.xml"
    local to="${4}/original_exiftool.xml"
    safecopy $from $to
    logit $4 "copied $from to $(basename $to)"
    generate_checksums $to
}

# loop through originals
n=0
for fpath in `find "${src}/meta/" -type f -name '*-meta.xml'`
do
    fn=$(basename "$fpath")
    ext="${fn##*.}"
    name="${fn%.*}"
    chunks=(${name//-/ });
    imgprefix=${chunks[0]}
    imgid=${chunks[1]}
    echo 'processing '"$imgprefix-$imgid"
    target="$dest/$imgprefix-$imgid"
    mkdir "$target"
    touch "$target"/history.log
    logit $target '\nISAW AWIB package '"$imgprefix-$imgid created by $realname ($USER@$hostname=$hostip) using the 'reswizzle' script from isaw.awib to import an old-style AWIB package from $src."
    copy_master $src $imgprefix $imgid $target
    copy_meta $src $imgprefix $imgid $target
    copy_original $src $imgprefix $imgid $target
    original=$(find "$target" -type f -name 'original.*' -exec file {} \; | awk -F: '{if ($2 ~/image/) print $1}')
    master="$target/master.tif"
    python "$PYTHONPATH/scripts/make_master.py" -q "$original" "$master"
    logit $target 'generated master.tif from '"$(basename $original))"' using '"$PYTHONPATH"'/scripts/make_master.py'
    exiftool -tagsfromfile "$original" -all:all "$master"
    logit $target 'copied embedded metadata from '"$original"' to '"$master"' using exiftool'
    bash "$here"'/make_guid.sh' "$target"
    logit $target 'generated image GUID and inserted in master.tif and metadata.xml using '"$PYTHONPATH"'/scripts/make_guid.sh'
    generate_checksums "$master"
    generate_checksums "$target"'/metadata.xml'
    identify_with_jhove "$master"
    extract_metadata "$master"
    logit $target 'RESWIZZLE COMPLETE: PACKAGE IMPORT COMPLETE\n# '"$dashes"
    "$here"/validate.sh "$target"
    logit $target 'Package successfully validated with isaw.awib/scripts.validate.sh.'
    let "n = $n + 1"
done

echo "$n"' image packages were converted from '"$src"' to '"$dest"'.'

exit
