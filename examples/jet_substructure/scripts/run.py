#!/bin/python

import os
import subprocess
# from shell import shell

ps = []
p1 = subprocess.Popen(["./scripts/run_gen_ensemble_exp.sh", "0", "./ensemble_configs/averaging/medium_shared_sparse_input_layer_configs/config1", "./averaging"])
p2 = subprocess.Popen(["./scripts/run_gen_ensemble_exp.sh", "0", "./ensemble_configs/averaging/medium_shared_sparse_input_layer_configs/config2", "./averaging"])
ps.append(p1)
ps.append(p2)

for p in ps:
    p.wait()
    print("Process finished with exit code: ", p.returncode)

# sh1 = shell("./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_shared_sparse_input_layer_configs/config1 ./averaging")
# sh2 = shell("./scripts/run_gen_ensemble_exp.sh 0 ./ensemble_configs/averaging/medium_shared_sparse_input_layer_configs/config2 ./averaging")
# print(sh1.output())
# print(sh1.errors())
# print(sh2.output())
# print(sh2.errors())
# if sh1.pid or sh2.pid:
#     os.wait()
#     print("Process 1 finished with exit code: ", sh1.exit_code)
#     print("Process 2 finished with exit code: ", sh2.exit_code)
