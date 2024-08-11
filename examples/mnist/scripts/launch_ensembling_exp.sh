#!/bin/bash

# Averaging MNIST
# tmux new-session -d -s m00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_configs/config1 ./averaging"
# tmux new-session -d -s m01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_configs/config2 ./averaging"
# tmux new-session -d -s m02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_configs/config3 ./averaging"
# tmux new-session -d -s m03 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_configs/config4 ./averaging"
# tmux new-session -d -s m04 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_configs/config5 ./averaging"

tmux new-session -d -s s00 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config1 ./averaging"
tmux new-session -d -s s01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config2 ./averaging"
tmux new-session -d -s s02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config3 ./averaging"
tmux new-session -d -s s03 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config4 ./averaging"