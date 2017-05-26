#!/usr/bin/env /bin/sh
find data/vehicles_level_01/vehicles/ -name '*.visual_processed' | xargs ./XmlUnpacker.py
find data/vehicles_level_01/vehicles/ -name '*.model' | xargs ./XmlUnpacker.py
find data/vehicles/ -name '*.xml' | grep -v customization | xargs ./XmlUnpacker.py
