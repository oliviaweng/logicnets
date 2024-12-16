#!/bin/bash

# Averaging MNIST
# tmux new-session -d -s m00 "conda activate myenv
# ./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/neuralut_same_input_output_scale_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s m01 "conda activate meynv
# ./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging/neuralut_same_input_output_scale_post_trans_configs/config2 ./averaging"
# tmux new-session -d -s m02 "conda activate myenv
# ./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/neuralut_same_input_output_scale_post_trans_configs/config3 ./averaging"
# tmux new-session -d -s m03 "conda activate myenv
# ./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/neuralut_same_input_output_scale_post_trans_configs/config4 ./averaging"
# tmux new-session -d -s m04 "conda activate myenv
# ./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/neuralut_same_input_output_scale_post_trans_configs/config0 ./averaging"

# Averaging JSC
# tmux new-session -d -s nj00 "./scripts/run_train_exp.sh 3 ./ensemble_configs/averaging_small/config1 ./averaging_small_final"
# tmux new-session -d -s nj01 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging_small/config2 ./averaging_small_final"
# tmux new-session -d -s nj02 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging_small/config3 ./averaging_small_final"
# tmux new-session -d -s nj01 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging_small/config2 ./averaging_small_final"
# tmux new-session -d -s nj02 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging_small/config3 ./averaging_small_final"

# tmux new-session -d -s nm00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging_medium/config1 ./averaging_medium"
# tmux new-session -d -s nm01 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging_medium/config2 ./averaging_medium"
# tmux new-session -d -s nm02 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging_medium/config3 ./averaging_medium"

tmux new-session -d -s nb00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging_small_input_bitwidth/config1 ./averaging_small_final"
# tmux new-session -d -s nb01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging_small_input_bitwidth/config2 ./averaging_small_final"
# tmux new-session -d -s nb02 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging_small_input_bitwidth/config1 ./averaging_small_final"
tmux new-session -d -s nb03 "./scripts/run_train_exp.sh 3 ./ensemble_configs/averaging_small_input_bitwidth/config3 ./averaging_small_final"
tmux new-session -d -s nb04 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging_small_input_bitwidth/config4 ./averaging_small_final"
tmux new-session -d -s nb05 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging_small_input_bitwidth/config5 ./averaging_small_final"


# tmux new-session -d -s s00 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s s01 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config2 ./averaging"
# tmux new-session -d -s s02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config3 ./averaging"
# tmux new-session -d -s s03 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg1_same_output_scale_post_trans_configs/config4 ./averaging"

# tmux new-session -d -s m00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg4_configs/config1 ./averaging"
# tmux new-session -d -s m01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg4_configs/config2 ./averaging"
# tmux new-session -d -s m02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/deg4_configs/config3 ./averaging"
# tmux new-session -d -s m03 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/deg4_configs/config0 ./averaging"


# Bagging
# tmux new-session -d -s bag "./scripts/run_train_exp.sh 1 ./ensemble_configs/bagging/deg1_configs ./bagging"
# tmux new-session -d -s bag "./scripts/run_train_exp.sh 0 ./ensemble_configs/bagging/deg4_configs ./bagging"

# AdaBoost
# tmux new-session -d -s ada "./scripts/run_train_exp.sh 0 ./ensemble_configs/adaboost/deg1_configs ./adaboost"
# tmux new-session -d -s ada "./scripts/run_train_exp.sh 1 ./ensemble_configs/adaboost/deg4_configs ./adaboost"
