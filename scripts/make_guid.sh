#!/bin/bash
set -e

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
pkgpath="$1"
realname=$(finger `whoami` | awk -F: '{ print $3 }' | head -n1 | sed 's/^ //')

insertmeta () {
    local metapath="$pkgpath"'/metadata.xml'
    local xpath=$1
    local ename=$2
    local val=$3
    if [ -z "$val" ]; then
        xml ed -P -L -i "$xpath" -t elem -n "$ename" $metapath
    else
        xml ed -P -L -i "$xpath" -t elem -n "$ename" -v "$val" $metapath
    fi
}

submeta () {
    local metapath="$pkgpath"'/metadata.xml'
    local xpath=$1
    local ename=$2
    local val=$3
    if [ -z "$val" ]; then
        xml ed -P -L -s "$xpath" -t elem -n "$ename" "$metapath"
    else
        xml ed -P -L -s "$xpath" -t elem -n "$ename" -v "$val" "$metapath"
    fi
}

reformatmeta () {
    local metapath="$pkgpath"'/metadata.xml'
    tmp_xml=$(mktemp)
    xml fo -s 3 "$metapath" > "$tmp_xml"
    mv "$tmp_xml" "$metapath"
}

guid=$(python "$PYTHONPATH"'/scripts/make_guid.py' "$pkgpath")
exiftool -DigitalImageGUID="$guid" "$pkgpath"'/master.tif'
insertmeta '/image-info/status' guid "$guid"
insertmeta '//change-history/change[1]' change
submeta '//change[1]' 'date' $(gdate -u --iso-8601=seconds)
submeta '//change[1]' 'agent' "$realname"
submeta '//change[1]' 'description' 'assigned GUID for this image using  isaw.awib/scripts/make_guid.sh'
reformatmeta
exit
