#!/bin/bash

# Averaging 
tmux new-session -d -s pj00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_configs/config1 ./averaging"

# Bagging
# tmux new-session -d -s bag "./scripts/run_train_exp.sh 0 ./ensemble_configs/bagging/deg4_configs ./bagging"

# AdaBoost
# tmux new-session -d -s ada "./scripts/run_train_exp.sh 0 ./ensemble_configs/adaboost/deg1_configs ./adaboost"
