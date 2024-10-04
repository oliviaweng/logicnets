#!/bin/bash

# model=small_shared_diagonal_output_layer_shared_output_fanin1_ensemble_size2
model=$1
suffix=no_tree
CONFIG=./ckpts/$model/hparams.yml
LOGDIR=./logs_$model/verilog_$suffix
LOGDIR=./final_verilog/$model
CKPT=./ckpts/$model/best_accuracy.pth
# CKPT="${LOGDIR}/lut_based_model.pth"

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir "${LOGDIR}" \
    --checkpoint $CKPT \
    --add-registers \
    >& "${model}_${suffix}.log"