#! /bin/bash
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
name="${2// }"
metapath="$pkgpath"'/metadata.xml'
realname=$(finger `whoami` | awk -F: '{ print $3 }' | head -n1 | sed 's/^ //')

here="$(dirname "${BASH_SOURCE[0]}")"
if [ "$name" ]; then
    guid=$(python "$PYTHONPATH"'/scripts/make_guid.py' "$pkgpath")
else
    guid=$(python "$PYTHONPATH"'/scripts/make_guid.py' -n "$name" "$pkgpath")
fi
exiftool -q -DigitalImageGUID="$guid" "$pkgpath"'/master.tif'
rm "$pkgpath"'/master.tif_original'
cp -p "$metapath" "$metapath".bak
saxon -s:"$metapath" -xsl:"$here"/setmetaval.xsl -o:"$metapath" agent="$realname" target=guid value="$guid"
rm "$metapath".bak
echo 'assigned unique identifier (GUID): '"$guid"
exit
