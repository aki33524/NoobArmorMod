#!/usr/bin/env /bin/sh
find data/vehicles/ -name '*.visual_processed' | xargs ./XmlUnpacker.py
find data/vehicles/ -name '*.model' | xargs ./XmlUnpacker.py
find data/xmls/ -name '*.xml' | grep -v customization | xargs ./XmlUnpacker.py
