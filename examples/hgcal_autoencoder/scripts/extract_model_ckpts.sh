#!/bin/bash

MODEL_CKPTS_DIR=./model_ckpts/small_averaging_fixed_mask
EXP_DIR=./averaging
EXP_NAME=averaging_small_fixed_mask_ensemble_size


mkdir -p $MODEL_CKPTS_DIR
for exp in `ls $EXP_DIR`; do

if [[ $exp == *"$EXP_NAME"* ]]; then
    # echo $exp
    ckpt=$EXP_DIR/$exp/best_loss.pth
    yml=$EXP_DIR/$exp/hparams.yml
    ckpt_exp_dir=$MODEL_CKPTS_DIR/$exp
    echo $ckpt_exp_dir
    mkdir -p $ckpt_exp_dir
    cp $ckpt $ckpt_exp_dir/best_loss.pth
    cp $yml $ckpt_exp_dir/hparams.yml
fi 

done