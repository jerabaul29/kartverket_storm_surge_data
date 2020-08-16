#!/bin/bash

path_to_cache="/home/jrlab/.NicedUrlRequest/cache"

#for crrt_file in ${path_to_cache}/.../../**
for crrt_file in ${path_to_cache}/???/????/??/*
do
    echo "${crrt_file}"
    file_size=$(stat -c%s "${crrt_file}")
    echo "size: ${file_size}"
done