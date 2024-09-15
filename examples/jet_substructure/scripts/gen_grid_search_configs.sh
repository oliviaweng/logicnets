#!/bin/bash

python3 grid_search.py -c search_configs/jscm_lite_ensemble_grid_search.yml -d ./ensemble_configs/adaboost/jscm_lite_deg2 --experiment_prefix adaboost_jscmlite_deg2

# python3 grid_search.py -c search_configs/jsc_xl_ensemble_grid_search.yml -d ./ensemble_configs/averaging/jsc_xl_deg2 --experiment_prefix averaging_jscxl_deg2