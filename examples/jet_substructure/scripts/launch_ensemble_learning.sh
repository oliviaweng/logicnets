#!/bin/bash


# Uniform input connectivity
# tmux new-session -d -s u00 "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/uniform_input_small ./jsc_single_models/"
# tmux new-session -d -s u01 "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/uniform_input_medium ./jsc_single_models/"
# tmux new-session -d -s u02 "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/uniform_input_large ./jsc_single_models/"
# tmux new-session -d -s uavg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config0 ./averaging"
# tmux new-session -d -s uavg01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config1 ./averaging"
# tmux new-session -d -s uavg02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config2 ./averaging"
# tmux new-session -d -s uavg03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_small_configs/config3 ./averaging"

# tmux new-session -d -s umavg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_medium_configs/config1 ./averaging"
# tmux new-session -d -s umavg01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_medium_configs/config2 ./averaging"
# tmux new-session -d -s umavg02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_medium_configs/config3 ./averaging"
# tmux new-session -d -s ulavg00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/uniform_input_large_configs/config1 ./averaging"
# tmux new-session -d -s ulavg01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/uniform_input_large_configs/config2 ./averaging"
# tmux new-session -d -s ulavg02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/uniform_input_large_configs/config3 ./averaging"

# Uniform connectivity
# tmux new-session -d -s u00 "./scripts/run_gen_ensemble_exp.sh 0 ./logicnet_configs/uniform_all ./jsc_single_models/"

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

# tmux new-session -d -s sinp "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_input_post_trans_sbs ./averaging"
# tmux new-session -d -s minp "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_input_post_trans_sbs ./averaging"
# tmux new-session -d -s linp "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_input_post_trans_sbs ./averaging"

# tmux new-session -d -s sinpq00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_quant_configs/config1 ./averaging"
# tmux new-session -d -s sinpq01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_quant_configs/config2 ./averaging"
# tmux new-session -d -s sinpl00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_layer_configs/config1 ./averaging"
# tmux new-session -d -s sinpl01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_input_layer_configs/config2 ./averaging"

# tmux new-session -d -s sinpl00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_sparse_input_layer_configs/config2 ./averaging"

# tmux new-session -d -s sinpl01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/shared_sparse_input_layer_and_output_sum_configs/config1 ./averaging"

# tmux new-session -d -s sinpl02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_sparse_input_layer_and_output_mean/ ./averaging"

# tmux new-session -d -s avg_jscs00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_sparse_input_layer_configs/config1 ./averaging"
# tmux new-session -d -s avg_jscs01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_sparse_input_layer_configs/config2 ./averaging"
# tmux new-session -d -s avg_jscs02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_sparse_input_layer_configs/config3 ./averaging"
# tmux new-session -d -s avg_jscs03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_sparse_input_layer_configs/config0 ./averaging"

# tmux new-session -d -s avg_jscm00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_shared_sparse_input_layer_configs/config1 ./averaging"
# tmux new-session -d -s avg_jscm01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_shared_sparse_input_layer_configs/config2 ./averaging"

# tmux new-session -d -s out00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_sparse_output_layer ./averaging"

# tmux new-session -d -s io00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_input_output_layers_configs/config1 ./averaging"
# tmux new-session -d -s io01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_input_output_layers_configs/config2 ./averaging"
# tmux new-session -d -s io02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_input_output_layers_configs/config3 ./averaging"

tmux new-session -d -s mio00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_shared_input_output_layers_configs/config1 ./averaging"
tmux new-session -d -s mio01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_shared_input_output_layers_configs/config2 ./averaging"
tmux new-session -d -s mio02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_shared_input_output_layers_configs/config3 ./averaging"

# tmux new-session -d -s lio00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_input_output_layers_configs/config1 ./averaging"
# tmux new-session -d -s lio01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_input_output_layers_configs/config2 ./averaging"
# tmux new-session -d -s lio02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_input_output_layers_configs/config3 ./averaging"

# TODO
# tmux new-session -d -s avg_jscl00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_sparse_input_layer_configs/config1 ./averaging"
# tmux new-session -d -s avg_jscl01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_sparse_input_layer_configs/config2 ./averaging"
# tmux new-session -d -s avg_jscl02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_sparse_input_layer_configs/config3 ./averaging"

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
