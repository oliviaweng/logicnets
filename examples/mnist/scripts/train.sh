#!/bin/bash

CUDA_DEVICE=$1
CONFIG=$2
SAVE_DIR=$3

exp_name="${CONFIG%.*}"
echo $exp_name
CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python3 train.py \
    --config $CONFIG \
    --save_dir $SAVE_DIR \
    --experiment_name $exp_name \
    --cuda \
    --device $CUDA_DEVICE


