#!/bin/sh
mkdir out 2>/dev/null
python ../rst2qhc.py handbook.txt reference.txt -o out --namespace urssus --filterattributes urssus:0.2.13 --rst2htmlopts="--stylesheet=style.css" --manifest MANIFEST
cd out
qcollectiongenerator project.qhcp -o collection.qhc
assistant -collectionFile collection.qhc -register doc.qhc 
assistant -collectionFile collection.qhc&
cd ..
