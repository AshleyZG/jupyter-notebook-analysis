#!/bin/bash

for i in `ls`;
do
# echo $i is file name\! ;
jupyter nbconvert --to python $i ;
done
