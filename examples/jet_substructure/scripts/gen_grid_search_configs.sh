#!/bin/bash

python3 grid_search.py -c search_configs/jscm_lite_ensemble_grid_search.yml -d ./ensemble_configs/bagging/jscm_lite_deg2_independent --experiment_prefix averaging_jscm_lite_deg2_shared_io

python3 grid_search.py -c search_configs/jsc_xl_ensemble_grid_search.yml -d ./ensemble_configs/averaging/jsc_xl_deg2_independent --experiment_prefix averaging_jscxl_deg2_shared_io
