#!/bin/bash

# Averaging 
# tmux new-session -d -s pj00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_configs/config1 ./averaging"
# tmux new-session -d -s pj01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_configs/config2 ./averaging"
# tmux new-session -d -s pj02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_configs/config3 ./averaging"

# tmux new-session -d -s pj03 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jsc_xl_deg2_configs/config1 ./polylut_averaging"
# tmux new-session -d -s pj04 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jsc_xl_deg2_configs/config2 ./polylut_averaging"
# tmux new-session -d -s pj05 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jsc_xl_deg2_configs/config3 ./polylut_averaging"


# tmux new-session -d -s pj00 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_shared_io_configs/config1 ./averaging"
# tmux new-session -d -s pj01 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_shared_io_configs/config2 ./averaging"
# tmux new-session -d -s pj02 "./scripts/run_train_exp.sh 0 ./ensemble_configs/averaging/jscm_lite_deg2_shared_io_configs/config3 ./averaging"

# tmux new-session -d -s pj03 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xl_deg2_shared_io_configs/config1 ./averaging"
# tmux new-session -d -s pj04 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xl_deg2_shared_io_configs/config2 ./averaging"
# tmux new-session -d -s pj05 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xl_deg2_shared_io_configs/config3 ./averaging"

# tmux new-session -d -s jxs00 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging/jsc_xs_deg3_shared_io_configs/config1 ./averaging"
# tmux new-session -d -s jxs01 "./scripts/run_train_exp.sh 3 ./ensemble_configs/averaging/jsc_xs_deg3_shared_io_configs/config2 ./averaging"
# tmux new-session -d -s jxs02 "./scripts/run_train_exp.sh 3 ./ensemble_configs/averaging/jsc_xs_deg3_shared_io_configs/config3 ./averaging"

# tmux new-session -d -s jxxs00 "./scripts/run_train_exp.sh 2 ./ensemble_configs/averaging/jsc_xxs_deg3_shared_io_configs/config1 ./averaging"
# tmux new-session -d -s jxxs01 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xxs_deg3_shared_io_configs/config2 ./averaging"
# tmux new-session -d -s jxxs02 "./scripts/run_train_exp.sh 1 ./ensemble_configs/averaging/jsc_xxs_deg3_shared_io_configs/config3 ./averaging"

# Single models
tmux new-session -d -s jxxs "./scripts/run_train_exp.sh 2 ./polylut_configs/jsc_xxs ./averaging"
tmux new-session -d -s jxs "./scripts/run_train_exp.sh 2 ./polylut_configs/jsc_xs ./averaging"



# Bagging
# tmux new-session -d -s bag "./scripts/run_train_exp.sh 1 ./ensemble_configs/bagging/jscm_lite_deg2 ./polylut_bagging"

# AdaBoost
# tmux new-session -d -s ada "./scripts/run_train_exp.sh 1 ./ensemble_configs/adaboost/jscm_lite_deg2 ./polylut_adaboost"

