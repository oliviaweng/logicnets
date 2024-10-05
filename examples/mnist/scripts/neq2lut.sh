#!/bin/bash

CONFIG=./mnist_single_models/mnist_m1.1/hparams.yml
LOGDIR=./mnist_m1.1_2ns_synth/verilog
CKPT=./mnist_single_models/mnist_m1.1/best_accuracy.pth

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir $LOGDIR \
    --checkpoint $CKPT \
    --clock-period 2 \
    --add-registers
