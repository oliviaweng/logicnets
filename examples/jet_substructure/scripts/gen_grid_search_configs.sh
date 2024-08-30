#!/bin/bash
#  Copyright (C) 2023, Advanced Micro Devices, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# Jet tagger model

# python3 grid_search.py -c search_configs/jsc_s_ensemble_grid_search.yml -d ./logicnet_configs/uniform_input_small --experiment_prefix uniform_input_small
# python3 grid_search.py -c search_configs/jsc_m_ensemble_grid_search.yml -d ./logicnet_configs/uniform_input_medium --experiment_prefix uniform_input_medium
# python3 grid_search.py -c search_configs/jsc_l_ensemble_grid_search.yml -d ./logicnet_configs/uniform_input_large --experiment_prefix uniform_input_large

python3 grid_search.py -c search_configs/jsc_s_ensemble_grid_search.yml -d ./ensemble_configs/averaging/uniform_input_small --experiment_prefix uniform_input_small

# Averaging
# python3 grid_search.py -c search_configs/jsc_s_averaging_grid_search.yml -d ../jet_substructure/ensemble_configs/averaging --experiment_prefix averaging_small
# python3 grid_search.py -c search_configs/jsc_m_averaging_grid_search.yml -d ../jet_substructure/ensemble_configs/averaging --experiment_prefix averaging_medium
# python3 grid_search.py -c search_configs/jsc_l_averaging_grid_search.yml -d ../jet_substructure/ensemble_configs/averaging --experiment_prefix averaging_large

# python3 grid_search.py -c search_configs/jsc_s_ensemble_grid_search.yml -d ./ensemble_configs/averaging/small_same_output_scale --experiment_prefix small_same_output_scale
# python3 grid_search.py -c search_configs/jsc_m_ensemble_grid_search.yml -d ./ensemble_configs/averaging/medium_same_output_scale --experiment_prefix medium_same_output_scale
# python3 grid_search.py -c search_configs/jsc_l_ensemble_grid_search.yml -d ./ensemble_configs/averaging/large_same_output_scale --experiment_prefix large_same_output_scale

# python3 grid_search.py -c search_configs/jsc_s_ensemble_grid_search.yml -d ./ensemble_configs/averaging/small_same_output_scale_post_trans --experiment_prefix small_same_output_scale_post_trans
# python3 grid_search.py -c search_configs/jsc_m_ensemble_grid_search.yml -d ./ensemble_configs/averaging/medium_same_output_scale_post_trans --experiment_prefix medium_same_output_scale_post_trans
# python3 grid_search.py -c search_configs/jsc_l_ensemble_grid_search.yml -d ./ensemble_configs/averaging/large_same_output_scale_post_trans --experiment_prefix large_same_output_scale_post_trans

# python3 grid_search.py -c search_configs/jsc_s_ensemble_grid_search.yml -d ./ensemble_configs/averaging/small_same_input_scale --experiment_prefix small_same_input_scale
# python3 grid_search.py -c search_configs/jsc_m_ensemble_grid_search.yml -d ./ensemble_configs/averaging/medium_same_input_scale --experiment_prefix medium_same_input_scale
# python3 grid_search.py -c search_configs/jsc_l_ensemble_grid_search.yml -d ./ensemble_configs/averaging/large_same_input_scale --experiment_prefix large_same_input_scale

# Bagging
# python3 grid_search.py -c search_configs/jsc_s_ensemble_grid_search.yml -d ./ensemble_configs/bagging/small_independent_configs --experiment_prefix bagging_small_independent
# python3 grid_search.py -c search_configs/jsc_m_ensemble_grid_search.yml -d ./ensemble_configs/bagging/medium_independent_configs  --experiment_prefix bagging_medium_independent
# python3 grid_search.py -c search_configs/jsc_l_ensemble_grid_search.yml -d ./ensemble_configs/bagging/large_independent_configs  --experiment_prefix bagging_large_independent

# AdaBoost
# python3 grid_search.py -c search_configs/jsc_s_ensemble_grid_search.yml -d ./ensemble_configs/adaboost/small_independent_configs --experiment_prefix adaboost_small_independent
# python3 grid_search.py -c search_configs/jsc_m_ensemble_grid_search.yml -d ./ensemble_configs/adaboost/medium_independent_configs  --experiment_prefix adaboost_medium_independent
# python3 grid_search.py -c search_configs/jsc_l_ensemble_grid_search.yml -d ./ensemble_configs/adaboost/large_independent_configs  --experiment_prefix adaboost_large_independent