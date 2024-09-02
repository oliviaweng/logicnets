#!/bin/bash


# Uniform input connectivity
# tmux new-session -d -s u00 "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/uniform_input_small ./jsc_single_models/"
# tmux new-session -d -s u01 "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/uniform_input_medium ./jsc_single_models/"
# tmux new-session -d -s u02 "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/uniform_input_large ./jsc_single_models/"
# tmux new-session -d -s uavg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config0 ./averaging"
# tmux new-session -d -s uavg01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config1 ./averaging"
# tmux new-session -d -s uavg02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config2 ./averaging"
# tmux new-session -d -s uavg03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config3 ./averaging"

tmux new-session -d -s umavg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_medium_configs/config1 ./averaging"
tmux new-session -d -s umavg01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_medium_configs/config2 ./averaging"
# tmux new-session -d -s umavg02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_medium_configs/config3 ./averaging"
tmux new-session -d -s ulavg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_large_configs/config1 ./averaging"
tmux new-session -d -s ulavg01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/uniform_input_large_configs/config2 ./averaging"
tmux new-session -d -s ulavg02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/uniform_input_large_configs/config3 ./averaging"


# Averaging jet tagger
# tmux new-session -d -s jscs00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config1 ./averaging"
# tmux new-session -d -s jscs01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config2 ./averaging"
# tmux new-session -d -s jscs02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config3 ./averaging"
# tmux new-session -d -s jscs03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config4 ./averaging"
# tmux new-session -d -s jscs04 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config5 ./averaging"

# tmux new-session -d -s jscs_avg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_qavg ./averaging"
# tmux new-session -d -s jscm_avg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_qavg_configs/config1 ./averaging"
# tmux new-session -d -s jscl_avg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_qavg_configs/config1 ./averaging"

# tmux new-session -d -s jscm00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config1 ./averaging"
# tmux new-session -d -s jscm01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config2 ./averaging"
# tmux new-session -d -s jscm02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config3 ./averaging"

# tmux new-session -d -s jscl00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_configs/config1 ./averaging"
# tmux new-session -d -s jscl01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_configs/config2 ./averaging"
# tmux new-session -d -s jscl02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_configs/config3 ./averaging"

# tmux new-session -d -s jsc_00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_no_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s jsc_01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_no_post_trans_configs/config2 ./averaging"

# tmux new-session -d -s jsc_02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_no_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s jsc_03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/medium_no_post_trans_configs/config2 ./averaging"

# tmux new-session -d -s jsc_04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_no_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s jsc_05 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_no_post_trans_configs/config2 ./averaging"


# tmux new-session -d -s jsc00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_configs/config1 ./averaging"
# tmux new-session -d -s jsc01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_configs/config2 ./averaging"
# tmux new-session -d -s jsc02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_configs/config3 ./averaging"

# tmux new-session -d -s jscm00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_same_output_scale_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s jscm01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_same_output_scale_post_trans_configs/config2 ./averaging"
# tmux new-session -d -s jscm02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_same_output_scale_post_trans_configs/config3 ./averaging"

# tmux new-session -d -s jscl00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_same_output_scale_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s jscl01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_same_output_scale_post_trans_configs/config2 ./averaging"
# tmux new-session -d -s jscl02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_same_output_scale_post_trans_configs/config3 ./averaging"

# tmux new-session -d -s jsc01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_post_trans ./averaging"

# tmux new-session -d -s jsc_sopt00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_post_trans_configs/config1 ./averaging"
# tmux new-session -d -s jsc_sopt01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_post_trans_configs/config2 ./averaging"
# tmux new-session -d -s jsc_sopt02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_post_trans_configs/config3 ./averaging"

# tmux new-session -d -s jsc_sopt00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_post_trans_configs/config4 ./averaging"
# tmux new-session -d -s jsc_sopt01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_output_scale_post_trans_configs/config5 ./averaging"

# tmux new-session -d -s sinp00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_input_scale_configs/config1 ./averaging"
# tmux new-session -d -s sinp01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_input_scale_configs/config2 ./averaging"
# tmux new-session -d -s sinp02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_same_input_scale_configs/config3 ./averaging"

# tmux new-session -d -s minp00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_same_input_scale_configs/config1 ./averaging"
# tmux new-session -d -s minp01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_same_input_scale_configs/config2 ./averaging"
# tmux new-session -d -s minp02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_same_input_scale_configs/config3 ./averaging"
 
# tmux new-session -d -s linp00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_same_input_scale_configs/config1 ./averaging"
# tmux new-session -d -s linp01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_same_input_scale_configs/config2 ./averaging"
# tmux new-session -d -s linp02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_same_input_scale_configs/config3 ./averaging"

# Bagging
# tmux new-session -d -s jscs_bag "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/small_configs ./bagging"
# tmux new-session -d -s jscm_bag "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/medium_configs ./bagging"
# tmux new-session -d -s jscl_bag "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/bagging/large_configs ./bagging"

# tmux new-session -d -s jscs_bag_ind "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/small_independent_configs ./bagging"
# tmux new-session -d -s jscm_bag_ind "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/medium_independent_configs ./bagging"
# tmux new-session -d -s jscl_bag_ind "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/large_independent_configs ./bagging"


# Adaboost
# tmux new-session -d -s jscs_ada_ind "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/small_independent_configs ./adaboost"
# tmux new-session -d -s jscm_ada_ind "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_independent_configs ./adaboost"
# tmux new-session -d -s jscl_ada_ind "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/large_independent_configs ./adaboost"
