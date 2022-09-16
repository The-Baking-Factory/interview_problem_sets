#!/bin/bash

#This bash scripts runs through every data json and passes arguments to compiled cpp parse code
#This results in logged insert/update operations for the db
#Arguments that are malformed or unsupported are handled by the cpp code which throws exceptions

for folder in dat/*/; do
    dtype=`basename $folder`
    if [ $dtype == "stocks" ]
    then
        for file in "$folder"*.json; do
            echo "RUNNING $dtype $file"
            ./dbops $file $dtype
        done
    fi
done