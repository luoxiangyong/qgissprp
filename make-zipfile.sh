#!/bin/bash
version=`grep version= metadata.txt | awk -F"=" '{print $2}'`
echo The sprp VERSION:${version}
cd ..
zip -r  qgis-plugins/qgissprp-${version}.zip  qgissprp/ -x "*/.git/*" \
    -x "*/.git" -x "*/__pycache__/*" -x "*/.vscode/*"\
    -x "*/help/build/*" -x "*/.DS_Store"
cd qgissprp
