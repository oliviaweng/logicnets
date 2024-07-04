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

# python3 grid_search.py -c search_configs/jsc_s_averaging_grid_search.yml -d ../jet_substructure/ensemble_configs/averaging --experiment_prefix averaging_small
# python3 grid_search.py -c search_configs/jsc_m_averaging_grid_search.yml -d ../jet_substructure/ensemble_configs/averaging --experiment_prefix averaging_medium
# python3 grid_search.py -c search_configs/jsc_l_averaging_grid_search.yml -d ../jet_substructure/ensemble_configs/averaging --experiment_prefix averaging_large

# python3 grid_search.py -c search_configs/jsc_s_averaging_grid_search.yml -d ./ensemble_configs/averaging/small_qavg --experiment_prefix small_qavg
python3 grid_search.py -c search_configs/jsc_m_averaging_grid_search.yml -d ./ensemble_configs/averaging/medium_qavg --experiment_prefix medium_qavg
python3 grid_search.py -c search_configs/jsc_l_averaging_grid_search.yml -d ./ensemble_configs/averaging/large_qavg --experiment_prefix large_qavg

