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


CONFIG_DIR=./ensemble_configs/averaging/small_same_output_scale

for i in {1..2}; do 
new_dir=${CONFIG_DIR}_configs/config${i}
mkdir -p $new_dir
find -wholename "${CONFIG_DIR}/*.yml" -print | head -n2 | xargs mv -t $new_dir
done
