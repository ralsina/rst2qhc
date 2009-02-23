#!/bin/sh
mkdir out 2>/dev/null
python ../rst2qhc.py handbook.txt reference.txt demo.txt -o out --namespace rst2qhc.demo --filterattributes rst2qhc --rst2htmlopts="--stylesheet=style.css --link-stylesheet" --manifest MANIFEST --create-qhcp
cd out
qcollectiongenerator project.qhcp -o collection.qhc
assistant -collectionFile collection.qhc -register doc.qhc 
assistant -collectionFile collection.qhc&
cd ..
