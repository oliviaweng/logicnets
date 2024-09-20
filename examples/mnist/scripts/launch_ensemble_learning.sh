#!/bin/bash

# single models
# tmux new-session -d -s mxs "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_xs ./minst_single_models/"
# tmux new-session -d -s ms "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_s ./minst_single_models/"
# tmux new-session -d -s mm "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_m ./minst_single_models/"
# tmux new-session -d -s ml "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/mnist_l ./minst_single_models/"

# Averaging
# tmux new-session -d -s ma00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging_configs/config1 ./averaging"
# tmux new-session -d -s ma01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging_configs/config2 ./averaging"
# tmux new-session -d -s ma02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging_configs/config3 ./averaging"
# tmux new-session -d -s ma03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging_configs/config0 ./averaging"

# tmux new-session -d -s xs00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/xs_configs/config1 ./averaging"
# tmux new-session -d -s xs01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/xs_configs/config2 ./averaging"
 # tmux new-session -d -s xs02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/xs_configs/config3 ./averaging"
 tmux new-session -d -s xs03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/xs_configs/config0 ./averaging"
