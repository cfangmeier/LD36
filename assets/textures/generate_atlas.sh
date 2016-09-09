#!/usr/bin/env bash
for var in "$@"
do
    rm -f ${var}-0.png $var.atlas
    ../../env/bin/python -m kivy.atlas $var 512x512 ${var}_*.png
done
