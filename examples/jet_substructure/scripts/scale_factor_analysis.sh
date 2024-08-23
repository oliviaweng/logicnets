#!/bin/bash

CUDA_DEVICE=0
CONFIG=./averaging/small_same_output_scale_post_trans_ensemble_size32_seed1/hparams.yml
CKPT=./averaging/small_same_output_scale_post_trans_ensemble_size32_seed1/best_accuracy.pth
CONFIG=./averaging/averaging_small_ensemble_size32/hparams.yml
CKPT=./averaging/averaging_small_ensemble_size32/best_accuracy.pth
SAVE_DIR=./scaling_factor_analysis
EXP_NAME=averaging

CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python3 scaling_factor_analysis.py \
    --save_dir $SAVE_DIR \
    --experiment_name $EXP_NAME \
    --evaluate \
    --cuda \
    --config $CONFIG \
    --checkpoint $CKPT