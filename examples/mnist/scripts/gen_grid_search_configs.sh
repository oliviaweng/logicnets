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

# MNIST model

# Averaging
# python3 grid_search.py -c search_configs/mnist_s_grid_search.yml -d ./ensemble_configs/averaging --experiment_prefix averaging_small
# python3 grid_search.py -c search_configs/mnist_xs_grid_search.yml -d ./ensemble_configs/averaging --experiment_prefix averaging_xs
# python3 grid_search.py -c search_configs/mnist_m_grid_search.yml -d ./ensemble_configs/averaging/med --experiment_prefix averaging_med
# python3 grid_search.py -c search_configs/mnist_xs_grid_search.yml -d ./ensemble_configs/averaging/non_shared_xs --experiment_prefix averaging_xs_non_shared
# python3 grid_search.py -c search_configs/mnist_xs_grid_search.yml -d ./ensemble_configs/averaging/shared_input_xs --experiment_prefix averaging_xs_shared_input
# python3 grid_search.py -c search_configs/mnist_l_grid_search.yml -d ./ensemble_configs/averaging/averaging_l --experiment_prefix averaging_l
python3 grid_search.py -c search_configs/mnist_l_grid_search.yml -d ./ensemble_configs/averaging/non_shared_l --experiment_prefix non_shared_l


# Bagging
# python3 grid_search.py -c search_configs/mnist_xs_grid_search.yml -d ./ensemble_configs/bagging/xs --experiment_prefix bagging_xs

# Adaboost
# python3 grid_search.py -c search_configs/mnist_xs_grid_search.yml -d ./ensemble_configs/adaboost/xs --experiment_prefix adaboost_xs
