#!/bin/bash

CONFIG=./mnist_single_models/mnist_s/hparams.yml
LOGDIR=./mnist_s_synth/verilog
CKPT=./mnist_single_models/mnist_s/best_accuracy.pth

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir $LOGDIR \
    --checkpoint $CKPT \
    --add-registers