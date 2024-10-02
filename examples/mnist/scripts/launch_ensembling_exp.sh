#!/bin/bash

# Averaging MNIST
# tmux new-session -d -s m00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_configs/config1 ./averaging"
# tmux new-session -d -s m01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_configs/config2 ./averaging"
# tmux new-session -d -s m02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_configs/config3 ./averaging"
# tmux new-session -d -s m03 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_configs/config4 ./averaging"
# tmux new-session -d -s m04 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_configs/config5 ./averaging"

# tmux new-session -d -s s00 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s s01 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config2 ./averaging"
# tmux new-session -d -s s02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config3 ./averaging"
# tmux new-session -d -s s03 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config4 ./averaging"

# tmux new-session -d -s m00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg4_configs/config1 ./averaging"
# tmux new-session -d -s m01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg4_configs/config2 ./averaging"
# tmux new-session -d -s m02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg4_configs/config3 ./averaging"
# tmux new-session -d -s m03 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg4_configs/config0 ./averaging"

# tmux new-session -d -s m00 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg3_configs/config1 ./averaging"
tmux new-session -d -s m01 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg3_configs/config2 ./averaging"
# tmux new-session -d -s m02 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg3_configs/config3 ./averaging"

# tmux new-session -d -s ms00 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging/deg3_shared_io_configs/config1 ./averaging"
tmux new-session -d -s ms01 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging/deg3_shared_io_configs/config2 ./averaging"
# tmux new-session -d -s ms02 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging/deg3_shared_io_configs/config3 ./averaging"

# Bagging
# tmux new-session -d -s bag "./scripts/run_train_exp.sh 1 ./ensemble_configs/bagging/deg1_configs ./bagging"
# tmux new-session -d -s bag "./scripts/run_train_exp.sh 0 ./ensemble_configs/bagging/deg4_configs ./bagging"

# AdaBoost
# tmux new-session -d -s ada "./scripts/run_train_exp.sh 0 ./ensemble_configs/adaboost/deg1_configs ./adaboost"
# tmux new-session -d -s ada "./scripts/run_train_exp.sh 1 ./ensemble_configs/adaboost/deg4_configs ./adaboost"