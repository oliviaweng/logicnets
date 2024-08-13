#!/bin/bash

CUDA_DEVICE=0
CONFIG=./adaboost_eval/hparams.yml
CKPT=./adaboost_eval/last_ensemble_ckpt.pth
SAVE_DIR=./adaboost_eval
EXP_NAME=test

CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python3 train.py \
    --save_dir $SAVE_DIR \
    --experiment_name $EXP_NAME \
    --evaluate \
    --cuda \
    --config $CONFIG \
    --checkpoint $CKPT
