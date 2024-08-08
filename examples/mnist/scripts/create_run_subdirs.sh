#!/bin/bash

CONFIG_DIR=./ensemble_configs/averaging/deg1

for i in {1..5}; do 
new_dir=${CONFIG_DIR}_configs/config${i}
mkdir -p $new_dir
find -wholename "${CONFIG_DIR}/*.yml" -print | head -n1 | xargs mv -t $new_dir
done