#!/bin/bash

# Averaging jet tagger
# tmux new-session -d -s jscs00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config1 ./averaging"
# tmux new-session -d -s jscs01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config2 ./averaging"
# tmux new-session -d -s jscs02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config3 ./averaging"
# tmux new-session -d -s jscs03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config4 ./averaging"
# tmux new-session -d -s jscs04 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config5 ./averaging"

tmux new-session -d -s jscs_avg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_qavg ./averaging"


# tmux new-session -d -s jscm00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config1 ./averaging"
# tmux new-session -d -s jscm01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config2 ./averaging"
# tmux new-session -d -s jscm02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config3 ./averaging"

# TODO
# tmux new-session -d -s jscl00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_configs/config1 ./averaging"
# tmux new-session -d -s jscl01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_configs/config2 ./averaging"
# tmux new-session -d -s jscl02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_configs/config3 ./averaging"