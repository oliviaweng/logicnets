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


# xlabs51
# Averaging
# large model
# tmux new-session -d -s e00 "./scripts/run_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config1"
# tmux new-session -d -s e01 "./scripts/run_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_configs/config2"
# tmux new-session -d -s e02 "./scripts/run_ensemble_exp.sh 1 ./ensemble_configs/averaging/medium_configs/config3"
# tmux new-session -d -s e03 "./scripts/run_ensemble_exp.sh 1 ./ensemble_configs/averaging/medium_configs/config4"
# tmux new-session -d -s e04 "./scripts/run_ensemble_exp.sh 2 ./ensemble_configs/averaging/medium_configs/config5"
# tmux new-session -d -s e05 "./scripts/run_ensemble_exp.sh 2 ./ensemble_configs/averaging/medium_configs/config6"

# small model
# tmux new-session -d -s s00 "./scripts/run_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config1"
# tmux new-session -d -s s01 "./scripts/run_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_configs/config2"
# tmux new-session -d -s s02 "./scripts/run_ensemble_exp.sh 1 ./ensemble_configs/averaging/small_configs/config3"
# tmux new-session -d -s s03 "./scripts/run_ensemble_exp.sh 1 ./ensemble_configs/averaging/small_configs/config4"
# tmux new-session -d -s s04 "./scripts/run_ensemble_exp.sh 2 ./ensemble_configs/averaging/small_configs/config5"
# tmux new-session -d -s s05 "./scripts/run_ensemble_exp.sh 2 ./ensemble_configs/averaging/small_configs/config6"

# Fixed sparsity mask ablation studies

# tmux new-session -d -s f00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_fixed_mask_configs/config3 ./averaging"
# tmux new-session -d -s f01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/medium_fixed_mask_configs/config3 ./averaging"
# tmux new-session -d -s f02 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/averaging/small_fixed_mask_configs/config3 ./averaging"

# tmux new-session -d -s f00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_fixed_mask_configs/config1 ./averaging"
# tmux new-session -d -s f01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_fixed_mask_configs/config2 ./averaging"
# tmux new-session -d -s f00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_fixed_mask_configs/config4 ./averaging"

# config3 and 4 done
# tmux new-session -d -s lf00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_fixed_mask_configs/config1 ./averaging"
# tmux new-session -d -s lf01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_fixed_mask_configs/config2 ./averaging"
# tmux new-session -d -s lf02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_fixed_mask_configs/config6 ./averaging"

# tmux new-session -d -s lf03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_fixed_mask_configs/config5 ./averaging"
# Small
# tmux new-session -d -s sf00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_configs/config1 ./averaging"
# tmux new-session -d -s sf01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_configs/config2 ./averaging"
# tmux new-session -d -s sf02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_configs/config5 ./averaging"

# tmux new-session -d -s sf00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_configs/config4 ./averaging"
# tmux new-session -d -s sf01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_configs/config6 ./averaging"
# tmux new-session -d -s sf02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_configs/config7 ./averaging"

# No weight decay
# CURR
# tmux new-session -d -s swd00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_no_wd_configs/config1 ./averaging"
# tmux new-session -d -s swd01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_fixed_mask_no_wd_configs/config2 ./averaging"
# tmux new-session -d -s lwd00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_fixed_mask_no_wd_configs/config1 ./averaging"
# tmux new-session -d -s lwd01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/large_fixed_mask_no_wd_configs/config2 ./averaging"

# Shared I/O layers
# tmux new-session -d -s hsio00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/small_shared_io_layers_configs/config1 ./averaging"
# tmux new-session -d -s hsio01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/small_shared_io_layers_configs/config2 ./averaging"
# tmux new-session -d -s hsio02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/small_shared_io_layers_configs/config3 ./averaging"

# tmux new-session -d -s hlio00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_io_layers_configs/config1 ./averaging"
# tmux new-session -d -s hlio01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_io_layers_configs/config2 ./averaging"
# tmux new-session -d -s hlio02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/large_shared_io_layers_configs/config3 ./averaging"

# tmux new-session -d -s hs3200 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_io_layers_ensemble32_seed_test_configs/config1 ./averaging"
# tmux new-session -d -s hs3201 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_io_layers_ensemble32_seed_test_configs/config2 ./averaging"
# tmux new-session -d -s hs3202 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/small_shared_io_layers_ensemble32_seed_test_configs/config3 ./averaging"


# Input quantizer
# tmux new-session -d -s hinpq00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/input_quants/small_configs/config1 ./averaging"
# tmux new-session -d -s hinpq01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/input_quants/small_configs/config2 ./averaging"
# tmux new-session -d -s hinpq02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/input_quants/small_configs/config3 ./averaging"
# tmux new-session -d -s hinpq03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/input_quants/small_configs/config4 ./averaging"

tmux new-session -d -s hinpq00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/input_quants/small_configs/config0 ./input_quants"
tmux new-session -d -s hinpq01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/input_quants/small_configs/config1 ./input_quants"
# tmux new-session -d -s hinpq02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/input_quants/small_configs/config2 ./input_quants"
# tmux new-session -d -s hinpq03 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/input_quants/small_configs/config3 ./input_quants"


# Same io scale
# tmux new-session -d -s hscal00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/same_io_scale/small ./averaging"
# tmux new-session -d -s hscal01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/same_io_scale/large ./averaging"




# weak1 model
# tmux new-session -d -s a00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/weak1_200epochs_configs/config1 ./averaging"
# tmux new-session -d -s a01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/weak1_200epochs_configs/config2 ./averaging"
# tmux new-session -d -s a02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/weak1_200epochs_configs/config4 ./averaging"

# medium model
# xlabs53
# tmux new-session -d -s a00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_fr_configs/config1 ./voting"
# tmux new-session -d -s a01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_fr_configs/config2 ./voting"
# tmux new-session -d -s a02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_fr_configs/config3 ./voting"
# tmux new-session -d -s a03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/medium_fr_configs/config4 ./voting"
# tmux new-session -d -s a04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/medium_fr_configs/config5 ./voting"
# tmux new-session -d -s a05 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/averaging/medium_fr_configs/config6 ./voting"

# FGE
# tmux new-session -d -s f00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/fge/small_configs/config1 ./fge"
# tmux new-session -d -s f01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/fge/small_configs/config2 ./fge"
# tmux new-session -d -s f02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/fge/small_configs/config3 ./fge"
# tmux new-session -d -s f03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/fge/medium_configs/config1 ./fge"
# tmux new-session -d -s f04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/fge/medium_configs/config2 ./fge"
# tmux new-session -d -s f05 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/fge/medium_configs/config3 ./fge"
# tmux new-session -d -s f06 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/fge/large_configs/config1 ./fge"
# tmux new-session -d -s f07 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/fge/large_configs/config2 ./fge"
# tmux new-session -d -s f08 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/fge/large_configs/config3 ./fge"

# Adaboost
# tmux new-session -d -s a00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/small_configs/config1 ./adaboost"
# tmux new-session -d -s a01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/small_configs/config2 ./adaboost"
# tmux new-session -d -s a02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/small_configs/config3 ./adaboost"
# tmux new-session -d -s a03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_configs/config1 ./adaboost"
# tmux new-session -d -s a04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_configs/config2 ./adaboost"
# tmux new-session -d -s a05 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_configs/config3 ./adaboost"
# tmux new-session -d -s a06 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/adaboost/large_configs/config1 ./adaboost"
# tmux new-session -d -s a07 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/adaboost/large_configs/config2 ./adaboost"
# tmux new-session -d -s a08 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/adaboost/large_configs/config3 ./adaboost"

# tmux new-session -d -s a00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/large_fixed_mask_configs/config2  ./adaboost"
# tmux new-session -d -s a01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/medium_fixed_mask_configs/config1 ./adaboost"
# tmux new-session -d -s a02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/small_fixed_mask_configs/config1  ./adaboost"

# tmux kill-session -t a00
# tmux kill-session -t a01
# tmux kill-session -t a02
# tmux kill-session -t a03
# tmux kill-session -t a04
# tmux kill-session -t a05
# tmux kill-session -t a06
# tmux kill-session -t a07
# tmux kill-session -t a08

# Warm restart sequential training w/o fixed decoder
# tmux new-session -d -s seq_ft00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/large_seq_configs/config1  ./adaboost_seq"
# tmux new-session -d -s seq_ft01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/large_seq_configs/config2  ./adaboost_seq"
# tmux new-session -d -s seq_ft02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/large_seq_configs/config3  ./adaboost_seq"

# tmux new-session -d -s seq_ft02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_seq_configs/config1 ./adaboost_seq"
# tmux new-session -d -s seq_ft04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_seq_configs/config2 ./adaboost_seq"
# tmux new-session -d -s seq_ft03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_seq_configs/config3 ./adaboost_seq"

# tmux new-session -d -s seq_ft06 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/small_seq_configs/config1  ./adaboost_seq"
# tmux new-session -d -s seq_ft04 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/adaboost/small_seq_configs/config2  ./adaboost_seq"
# tmux new-session -d -s seq_ft05 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/adaboost/small_seq_configs/config3  ./adaboost_seq"

# CURR
# tmux new-session -d -s a00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/weak1_seq_configs/config1 ./adaboost"
# tmux new-session -d -s a01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/weak2_seq_configs/config1 ./adaboost"


# xlabs55

#AdaBoost mini ablation study

# Finetune decoder but initializing new encoder also initialized decoder this time
# tmux new-session -d -s ind_ft00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/large_ind_decoder_configs/config2  ./adaboost"
# tmux new-session -d -s ind_ft01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/medium_ind_decoder_configs/config2 ./adaboost"
# tmux new-session -d -s ind_ft02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/small_ind_decoder_configs/config1  ./adaboost"

# Fixed decoder with new independent decoder initialization
# tmux new-session -d -s ind_fixed00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/large_fixed_decoder_configs/config1  ./adaboost"
# tmux new-session -d -s ind_fixed01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/medium_fixed_decoder_configs/config1 ./adaboost"
# tmux new-session -d -s ind_fixed02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/adaboost/small_fixed_decoder_configs/config2  ./adaboost"

# Fixed decoder with warm restart sequential training (no encoder/decoder initialization at the start of each boosting)
# tmux new-session -d -s seq_fixed00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/large_seq_fixed_decoder_configs/config2  ./adaboost"
# tmux new-session -d -s seq_fixed01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_seq_fixed_decoder_configs/config2 ./adaboost"
# tmux new-session -d -s seq_fixed02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/small_seq_fixed_decoder_configs/config2  ./adaboost"

# Warm restart sequential training w/o fixed decoder - best so far
# tmux new-session -d -s seq_ft00 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/large_seq_configs/config3  ./adaboost"
# tmux new-session -d -s seq_ft01 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/medium_seq_configs/config2 ./adaboost"
# tmux new-session -d -s seq_ft02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/adaboost/small_seq_configs/config1  ./adaboost"

# Bagging
# tmux new-session -d -s b00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/small_seq_configs/config1  ./bagging"
# tmux new-session -d -s b01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/small_seq_configs/config2  ./bagging"
# tmux new-session -d -s b02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/bagging/small_seq_configs/config3  ./bagging"
# tmux new-session -d -s b03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/bagging/medium_seq_configs/config1 ./bagging"
# tmux new-session -d -s b04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/bagging/medium_seq_configs/config2 ./bagging"
# tmux new-session -d -s b05 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/bagging/medium_seq_configs/config3 ./bagging"
# tmux new-session -d -s b06 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/bagging/large_seq_configs/config1  ./bagging"
# tmux new-session -d -s b07 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/bagging/large_seq_configs/config2  ./bagging"
# tmux new-session -d -s b08 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/bagging/large_seq_configs/config3  ./bagging"


# Snapshot (SSE)
# tmux new-session -d -s sse00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_configs/config1 ./sse"
# tmux new-session -d -s sse01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_configs/config2 ./sse"
# tmux new-session -d -s sse02 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/large_configs/config3 ./sse"
# tmux new-session -d -s sse03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/large_configs/config4 ./sse"
# tmux new-session -d -s sse04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/small_configs/config1 ./sse"
# tmux new-session -d -s sse05 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_configs/config2 ./sse"
# tmux new-session -d -s sse06 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_configs/config3 ./sse"
# tmux new-session -d -s sse07 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_configs/config4 ./sse"

# SSE finetuning
# tmux new-session -d -s ft00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_ft_configs/config1 ./sse"
# tmux new-session -d -s ft01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_ft_configs/config2 ./sse"
# tmux new-session -d -s ft02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_ft_configs/config3 ./sse"
# tmux new-session -d -s ft03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/large_ft_configs/config4 ./sse"
# tmux new-session -d -s ft033 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/large_ft_configs/config5 ./sse"
# tmux new-session -d -s ft04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/small_ft_configs/config1 ./sse"
# tmux new-session -d -s ft05 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/small_ft_configs/config2 ./sse"
# tmux new-session -d -s ft06 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_ft_configs/config3 ./sse"
# tmux new-session -d -s ft07 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_ft_configs/config4 ./sse"
# tmux new-session -d -s ft08 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_ft_configs/config5 ./sse"

# SSE more epochs + finetuning
# tmux new-session -d -s m00 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_more_epochs_configs/config1 ./sse_more_epochs"
# tmux new-session -d -s m01 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_more_epochs_configs/config2 ./sse_more_epochs"
# tmux new-session -d -s m02 "./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/sse/large_more_epochs_configs/config3 ./sse_more_epochs"
# tmux new-session -d -s m03 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/medium_more_epochs_configs/config1 ./sse_more_epochs"
# tmux new-session -d -s m04 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/medium_more_epochs_configs/config2 ./sse_more_epochs"
# tmux new-session -d -s m05 "./scripts/run_gen_ensemble_exp.sh 1 ./ensemble_configs/sse/medium_more_epochs_configs/config3 ./sse_more_epochs"
# tmux new-session -d -s m06 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_more_epochs_configs/config1 ./sse_more_epochs"
# tmux new-session -d -s m07 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_more_epochs_configs/config2 ./sse_more_epochs"
# tmux new-session -d -s m08 "./scripts/run_gen_ensemble_exp.sh 2 ./ensemble_configs/sse/small_more_epochs_configs/config3 ./sse_more_epochs"
