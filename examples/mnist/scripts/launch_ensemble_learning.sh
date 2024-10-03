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
#  tmux new-session -d -s xs03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/xs_configs/config0 ./averaging"
# tmux new-session -d -s xs04 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/xs_configs/config4 ./averaging"
# tmux new-session -d -s xs05 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/xs_configs/config5 ./averaging"

# tmux new-session -d -s xsn01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/non_shared_xs_configs/config2 ./averaging"
# tmux new-session -d -s xsn00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/non_shared_xs_configs/config1 ./averaging"
# tmux new-session -d -s xsn02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/non_shared_xs_configs/config3 ./averaging"

# tmux new-session -d -s xsi01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_xs_configs/config1 ./averaging"
# tmux new-session -d -s xsi02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_xs_configs/config2 ./averaging"
# tmux new-session -d -s xsi03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_xs_configs/config3 ./averaging"
# tmux new-session -d -s xsi00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_xs_configs/config0 ./averaging"

# tmux new-session -d -s m00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/med_configs/config1 ./averaging"
# tmux new-session -d -s m01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/med_configs/config2 ./averaging"
# tmux new-session -d -s m02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/med_configs/config3 ./averaging"

# tmux new-session -d -s l01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/averaging_l_configs/config1 ./averaging"
# tmux new-session -d -s l03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/averaging_l_configs/config3 ./averaging"
# tmux new-session -d -s l02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/averaging_l_configs/config2 ./averaging"

# tmux new-session -d -s l02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/non_shared_l_configs/config1 ./averaging"
# tmux new-session -d -s lns03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/non_shared_l_configs/config3 ./averaging"
tmux new-session -d -s lns02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/non_shared_l_configs/config2 ./averaging"

# Bagging
# tmux new-session -d -s mb00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/bagging/xs_configs/config1 ./bagging"

# Adaboost
# tmux new-session -d -s mada00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/xs_configs/config1 ./adaboost"
