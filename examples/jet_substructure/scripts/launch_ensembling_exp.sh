#!/bin/bash

# Averaging 
# tmux new-session -d -s pj00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_configs/config1 ./averaging"
# tmux new-session -d -s pj01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_configs/config2 ./averaging"
# tmux new-session -d -s pj02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_configs/config3 ./averaging"

# tmux new-session -d -s pj03 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jsc_xl_deg2_configs/config1 ./polylut_averaging"
# tmux new-session -d -s pj04 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jsc_xl_deg2_configs/config2 ./polylut_averaging"
# tmux new-session -d -s pj05 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jsc_xl_deg2_configs/config3 ./polylut_averaging"


tmux new-session -d -s pj00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_shared_io_configs/config1 ./averaging"
tmux new-session -d -s pj01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_shared_io_configs/config2 ./averaging"
tmux new-session -d -s pj02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_shared_io_configs/config3 ./averaging"

tmux new-session -d -s pj03 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xl_deg2_shared_io_configs/config1 ./averaging"
tmux new-session -d -s pj04 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xl_deg2_shared_io_configs/config2 ./averaging"
tmux new-session -d -s pj05 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xl_deg2_shared_io_configs/config3 ./averaging"

# Bagging
# tmux new-session -d -s bag "./scripts/run_train_exp.sh 1 ./ensemble_configs/bagging/jscm_lite_deg2 ./polylut_bagging"

# AdaBoost
# tmux new-session -d -s ada "./scripts/run_train_exp.sh 1 ./ensemble_configs/adaboost/jscm_lite_deg2 ./polylut_adaboost"

