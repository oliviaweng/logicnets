#!/bin/bash

CUDA_DEVICE=$1
CONFIG_DIR=$2
SAVE_DIR=$3

for config in `ls $CONFIG_DIR`; do
exp_name="${config%.*}"
echo $exp_name

CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python3 train.py \
    --config "${CONFIG_DIR}/${config}" \
    --save_dir $SAVE_DIR \
    --experiment_name $exp_name \
    --train \
    --cuda
done