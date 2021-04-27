#!/bin/sh

echo Setup QGIS Enviroments...
export PATH=/Applications/QGIS.app/Contents/MacOS/bin:$PATH
export PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python
export LD_LIBRARY_PATH=/Applications/QGIS.app/lib
export DYLD_LIBRARY_PATH=/Applications/QGIS.app/lib
export QT_QPA_PLATFORM_PLUGIN_PATH=/Applications/QGIS.app/Contents/PlugIns/platforms
export DYLD_INSERT_LIBRARIES=/Applications/QGIS.app/Contents/MacOS/lib/libsqlite3.dylib
echo Done.
