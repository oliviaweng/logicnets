#!/bin/bash

# model=small_shared_diagonal_output_layer_shared_output_fanin1_ensemble_size2
model=$1
DIR=./ckpts
CONFIG=$DIR/$model/hparams.yml
LOGDIR=./logs_$model/verilog
CKPT=$DIR/$model/best_accuracy.pth
# CKPT="${LOGDIR}/lut_based_model.pth"

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir "${LOGDIR}" \
    --checkpoint $CKPT \
    --add-registers \
    --simulate-pre-synthesis-verilog