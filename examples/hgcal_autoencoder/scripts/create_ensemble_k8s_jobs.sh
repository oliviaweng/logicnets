#!/bin/bash
set -e

ENSEMBLE_METHOD=averaging
EXP_TAG=_fixed_mask
POD_TAG=fixed
MODELS=("large" "medium" "small")
CONFIG_NUMS=(1 2 4 5 6) # config dir nums
OUTPUT_DIR=./averaging

for MODEL in ${MODELS[@]}; do 
for CONFIG_NUM in ${CONFIG_NUMS[@]}; do 

K8S_DIR=${ENSEMBLE_METHOD}_${MODEL}${EXP_TAG}

POD_NAME=${ENSEMBLE_METHOD}-${MODEL}-${POD_TAG}-${CONFIG_NUM}
NAME=${ENSEMBLE_METHOD}_${MODEL}${EXP_TAG}_${CONFIG_NUM}
CONFIG_DIR=./ensemble_configs/${ENSEMBLE_METHOD}/${MODEL}${EXP_TAG}_configs/config${CONFIG_NUM}

mkdir -p k8s/${K8S_DIR}
cp k8s/ensemble_template.yml k8s/${K8S_DIR}/${NAME}.yml

sed -i'' "s|PODNAME|${POD_NAME}|g" k8s/${K8S_DIR}/${NAME}.yml
sed -i'' "s|CONFIGDIR|${CONFIG_DIR}|g" k8s/${K8S_DIR}/${NAME}.yml
sed -i'' "s|OUTPUTDIR|${OUTPUT_DIR}|g" k8s/${K8S_DIR}/${NAME}.yml

echo ${NAME}.yml

done
done