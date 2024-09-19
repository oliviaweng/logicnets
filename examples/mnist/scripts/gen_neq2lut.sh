#!/bin/bash

CONFIG=$1
LOGDIR=$2
CKPT=$3

python3 neq2lut.py \
    --config $CONFIG \
    --log-dir $LOGDIR \
    --checkpoint $CKPT \
    --add-registers