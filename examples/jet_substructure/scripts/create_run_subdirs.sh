#!/bin/bash

CONFIG_DIR=./ensemble_configs/averaging/jsc_xxs_deg3_shared_io

for i in {1..3}; do 
new_dir=${CONFIG_DIR}_configs/config${i}
mkdir -p $new_dir
find -wholename "${CONFIG_DIR}/*.yml" -print | head -n1 | xargs mv -t $new_dir
done