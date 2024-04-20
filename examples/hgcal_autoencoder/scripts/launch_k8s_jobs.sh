#!/bin/bash

ENSEMBLE_METHOD=averaging
EXP_TAG=_fixed_mask
MODELS=("large" "medium" "small")


for MODEL in ${MODELS[@]}; do
K8S_DIR=./k8s/${ENSEMBLE_METHOD}_${MODEL}${EXP_TAG}

for YML in `ls $K8S_DIR`; do

kubectl create -f $K8S_DIR/$YML
# echo $K8S_DIR/$YML

done
done