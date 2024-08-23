#!/bin/bash

CONFIG=./jscs_synth_test/hparams.yml
LOGDIR=./jscs_synth_test/verilog
CKPT=./jscs_synth_test/best_accuracy.pth

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir $LOGDIR \
    --checkpoint $CKPT \
    --add-registers