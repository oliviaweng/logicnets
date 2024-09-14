#!/bin/python

import os
import subprocess

ps = []
p1 = subprocess.Popen(
    [
        "./scripts/run_gen_ensemble_exp.sh",
        "0",
        "./ensemble_configs/averaging/medium_shared_input_output_layers_configs/config1",
        "./averaging",
    ]
)
p2 = subprocess.Popen(
    [
        "./scripts/run_gen_ensemble_exp.sh",
        "0",
        "./ensemble_configs/averaging/medium_shared_input_output_layers_configs/config2",
        "./averaging",
    ]
)
p3 = subprocess.Popen(
    [
        "./scripts/run_gen_ensemble_exp.sh",
        "0",
        "./ensemble_configs/averaging/medium_shared_input_output_layers_configs/config3",
        "./averaging",
    ]
)

p4 = subprocess.Popen(
    [
        "./scripts/run_gen_ensemble_exp.sh",
        "1",
        "./ensemble_configs/averaging/large_shared_input_output_layers_configs/config1",
        "./averaging",
    ]
)
p5 = subprocess.Popen(
    [
        "./scripts/run_gen_ensemble_exp.sh",
        "1",
        "./ensemble_configs/averaging/large_shared_input_output_layers_configs/config2",
        "./averaging",
    ]
)
p6 = subprocess.Popen(
    [
        "./scripts/run_gen_ensemble_exp.sh",
        "1",
        "./ensemble_configs/averaging/large_shared_input_output_layers_configs/config3",
        "./averaging",
    ]
)
ps.append(p1)
ps.append(p2)
ps.append(p3)
ps.append(p4)
ps.append(p5)
ps.append(p6)

for p in ps:
    p.wait()
    print("Process finished with exit code: ", p.returncode)
