#!/bin/bash

# single models
# tmux new-session -d -s mxs "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_xs ./minst_single_models/"
# tmux new-session -d -s ms "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_s ./minst_single_models/"
# tmux new-session -d -s mm "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_m ./minst_single_models/"
tmux new-session -d -s ml "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_l ./minst_single_models/"

