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


# Pareto models grid search
# python3 grid_search.py -c search_configs/small_model_grid_search.yml -d grid_search_configs/small --experiment_prefix small
# python3 grid_search.py -c search_configs/medium_model_grid_search.yml -d grid_search_configs/medium --experiment_prefix medium
# python3 grid_search.py -c search_configs/large_model_grid_search.yml -d grid_search_configs/large --experiment_prefix large

# Avg EMD Pareto models grid search
# python3 grid_search.py -c search_configs/avg_emd_small_model_grid_search.yml -d grid_search_configs/avg_emd_small --experiment_prefix small
# python3 grid_search.py -c search_configs/avg_emd_medium_model_grid_search.yml -d grid_search_configs/avg_emd_medium --experiment_prefix medium
# python3 grid_search.py -c search_configs/avg_emd_medium_model_grid_search.yml -d grid_search_configs/avg_emd_medium --experiment_prefix medium

# Weak model grid search (+polylut)
# python3 grid_search.py -c search_configs/weak1_model_grid_search.yml -d grid_search_configs/weak1_poly --experiment_prefix weak1_poly
# python3 grid_search.py -c search_configs/weak2_model_grid_search.yml -d grid_search_configs/weak2_poly --experiment_prefix weak2_poly

# Ensemble grid search
# Averaging polylut
python3 grid_search.py -c search_configs/polylut_large_model_grid_search.yml -d ensemble_configs/averaging/large_polylut_shared_io --experiment_prefix large_polylut_shared_io

# Averaging
# python3 grid_search.py -c search_configs/voting_small_model_grid_search.yml -d ensemble_configs/averaging/small --experiment_prefix averaging_small
# python3 grid_search.py -c search_configs/voting_medium_model_grid_search.yml -d ensemble_configs/averaging/medium_fr --experiment_prefix averaging_medium_fr

# python3 grid_search.py -c search_configs/voting_small_model_grid_search.yml -d ensemble_configs/averaging/small_fixed_mask --experiment_prefix averaging_small_fixed_mask
# python3 grid_search.py -c search_configs/voting_medium_model_grid_search.yml -d ensemble_configs/averaging/medium_fixed_mask --experiment_prefix averaging_medium_fixed_mask
# python3 grid_search.py -c search_configs/voting_large_model_grid_search.yml -d ensemble_configs/averaging/large_fixed_mask --experiment_prefix averaging_large_fixed_mask

# python3 grid_search.py -c search_configs/voting_weak1_model_grid_search.yml -d ensemble_configs/averaging/weak1_200epochs --experiment_prefix averaging_weak1_two_hundred_epochs
# python3 grid_search.py -c search_configs/voting_weak2_model_grid_search.yml -d ensemble_configs/averaging/weak2 --experiment_prefix averaging_weak2

# python3 grid_search.py -c search_configs/voting_weak1_model_grid_search.yml -d ensemble_configs/averaging/weak1_fixed_mask --experiment_prefix averaging_weak1_fixed_mask
# python3 grid_search.py -c search_configs/voting_weak2_model_grid_search.yml -d ensemble_configs/averaging/weak2_fixed_mask --experiment_prefix averaging_weak2_fixed_mask

# Snapshot Ensemble
# python3 grid_search.py -c search_configs/sse_large_model_grid_search.yml -d ensemble_configs/sse/large_more_epochs --experiment_prefix sse_large
# python3 grid_search.py -c search_configs/sse_medium_model_grid_search.yml -d ensemble_configs/sse/medium_more_epochs --experiment_prefix sse_medium
# python3 grid_search.py -c search_configs/sse_small_model_grid_search.yml -d ensemble_configs/sse/small_more_epochs --experiment_prefix sse_small

# FGE
# python3 grid_search.py -c search_configs/fge_large_model_grid_search.yml -d ensemble_configs/fge/large --experiment_prefix fge_large
# python3 grid_search.py -c search_configs/fge_medium_model_grid_search.yml -d ensemble_configs/fge/medium --experiment_prefix fge_medium
# python3 grid_search.py -c search_configs/fge_small_model_grid_search.yml -d ensemble_configs/fge/small --experiment_prefix fge_small

# Adaboost
# python3 grid_search.py -c search_configs/adaboost_small_model_grid_search.yml -d ensemble_configs/adaboost/small_seq --experiment_prefix adaboost_small_seq
# python3 grid_search.py -c search_configs/adaboost_medium_model_grid_search.yml -d ensemble_configs/adaboost/medium_seq --experiment_prefix adaboost_medium_seq
# python3 grid_search.py -c search_configs/adaboost_large_model_grid_search.yml -d ensemble_configs/adaboost/large_seq --experiment_prefix adaboost_large_seq

# python3 grid_search.py -c search_configs/adaboost_small_model_grid_search.yml  -d ensemble_configs/adaboost/fixed_mask_10epochs --experiment_prefix  adaboost_small_fixed_mask_10epochs
# python3 grid_search.py -c search_configs/adaboost_medium_model_grid_search.yml -d ensemble_configs/adaboost/fixed_mask_10epochs --experiment_prefix adaboost_medium_fixed_mask_10epochs
# python3 grid_search.py -c search_configs/adaboost_large_model_grid_search.yml  -d ensemble_configs/adaboost/large_fixed_mask --experiment_prefix  adaboost_large_fixed_mask_10epochs

# Bagging
# python3 grid_search.py -c search_configs/bagging_small_model_grid_search.yml  -d ensemble_configs/bagging/small_seq  --experiment_prefix bagging_small_seq
# python3 grid_search.py -c search_configs/bagging_medium_model_grid_search.yml -d ensemble_configs/bagging/medium_seq --experiment_prefix bagging_medium_seq
# python3 grid_search.py -c search_configs/bagging_large_model_grid_search.yml  -d ensemble_configs/bagging/large_seq  --experiment_prefix bagging_large_seq
