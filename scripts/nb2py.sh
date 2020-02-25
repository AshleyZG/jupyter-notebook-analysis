#!/bin/bash
OldSuffix=".ipynb"
NewSuffix=".py"
for i in `ls *0.ipynb`;
do
	if [ ! -f "${i/$OldSuffix/$NewSuffix}" ]; then
		jupyter nbconvert --to python $i ;
	fi
done
