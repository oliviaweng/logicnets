#!/bin/bash

# Averaging jet tagger
tmux new-session -d -s jscs00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config1 ./averaging"
tmux new-session -d -s jscs01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config2 ./averaging"
tmux new-session -d -s jscs02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config3 ./averaging"