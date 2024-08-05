#!/bin/bash

CONFIG=./averaging/averaging_small_ensemble_size2/hparams.yml
LOGDIR=./jsc_s_ensemble/verilog
CKPT=./jsc_s_ensemble/buggy_verilog/lut_based_model.pth

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir $LOGDIR \
    --checkpoint $CKPT \
    --add-registers