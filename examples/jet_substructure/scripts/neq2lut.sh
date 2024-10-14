#!/bin/bash

# model=small_shared_diagonal_output_layer_shared_output_fanin1_ensemble_size2
model=$1
DIR=./input_quant_ckpts
suffix=no_tree
CONFIG=$DIR/$model/hparams.yml
CKPT=$DIR/$model/best_accuracy.pth
LOGHOME=$DIR/final_verilog
LOGDIR=$LOGHOME/$model

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir "${LOGDIR}" \
    --checkpoint $CKPT \
    --add-registers \
    >& "${LOGHOME}/${model}_${suffix}.log"