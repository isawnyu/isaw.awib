#!/bin/bash
set -e

generate_checksums() {
    local dirn=$(dirname "$1")
    local fn=$(basename "$1")
    local ext="${fn##*.}"
    local name="${fn%.*}"
    local shaname="${name}.sha512"
    local sha512=$(gsha512sum -b "$1" | awk '{print $1;}')
    echo "$sha512  $fn" > "${dirn}/$shaname"
}

safecopy () {
    cp $1 $2
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
    local to="${4}/${2}-${3}-master.tif"
    safecopy $from $to
    generate_checksums $to
    local from="${1}/masters/${2}-${3}-master-jhove.xml"
    local to="${4}/${2}-${3}-master-jhove.xml"
    safecopy $from $to
    generate_checksums $to
}

copy_meta () {
    local from="${1}/meta/${2}-${3}-meta.xml"
    local to="${4}/${2}-${3}-meta.xml"
    safecopy $from $to
    generate_checksums $to
}

copy_original () {
    for orig in `find "${1}/originals/" -type f -name ''"${2}-${3}"'-original.*'`
    do
        local origfn=$(basename "$orig")
        local ext="${origfn##*.}"
        local from="${1}/originals/${2}-${3}-original.${ext}"
        local to="${4}/${2}-${3}-original.${ext}"
        safecopy $from $to
        generate_checksums $to
    done
    local from="${1}/originals/${2}-${3}-original-jhove.xml"
    local to="${4}/${2}-${3}-original-jhove.xml"
    safecopy $from $to
    generate_checksums $to
    local from="${1}/originals/${2}-${3}-original-exiftool.xml"
    local to="${4}/${2}-${3}-original-exiftool.xml"
    safecopy $from $to
    generate_checksums $to
}

copy_review () {
    local from="${1}/review-images/${2}-${3}-review.jpg"
    local to="${4}/${2}-${3}-review.jpg"
    safecopy $from $to    
    generate_checksums $to
}

copy_thumb () {
    local from="${1}/thumbnails/${2}-${3}-thumb.jpg"
    local to="${4}/${2}-${3}-thumb.jpg"
    safecopy $from $to    
    generate_checksums $to
}

src=$1
dest=$2
colln=$(basename "$src")
ext="${fn##*.}"
name="${fn%.*}"

# loop through originals
for fpath in `find "${src}/meta/" -type f -name '*-meta.xml'`
do
    fn=$(basename "$fpath")
    ext="${fn##*.}"
    name="${fn%.*}"
    chunks=(${name//-/ });
    imgprefix=${chunks[0]}
    imgid=${chunks[1]}
    target="$dest/$imgprefix-$imgid"
    mkdir "$target"
    copy_master $src $imgprefix $imgid $target
    copy_original $src $imgprefix $imgid $target
    copy_review $src $imgprefix $imgid $target
    copy_thumb $src $imgprefix $imgid $target
done

exit
