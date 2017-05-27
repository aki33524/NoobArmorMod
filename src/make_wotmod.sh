#!/usr/bin/env /bin/sh
for d in *; do cd $d && zip -r -0 ../NoobArmorMod/$d.wotmod res/ && cd ../; done;
