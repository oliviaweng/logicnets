#  Copyright (C) 2021 Xilinx, Inc
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

import os
import yaml
import time
from argparse import ArgumentParser

import torch
from torch.utils.data import DataLoader

from logicnets.nn import    generate_truth_tables, \
                            lut_inference, \
                            module_list_to_verilog_module , \
                            ensemble_to_verilog_module

from training_methods import test
from dataset import JetSubstructureDataset
from models import JetSubstructureNeqModel, JetSubstructureLutModel
from ensemble import AveragingJetLUTModel, AveragingJetNeqModel
from logicnets.synthesis import synthesize_and_get_resource_counts
from logicnets.util import proc_postsynth_file

other_options = {
    "cuda": None,
    "log_dir": None,
    "checkpoint": None,
    "generate_bench": False,
    "add_registers": False,
    "simulate_pre_synthesis_verilog": False,
    "simulate_post_synthesis_verilog": False,
}

model_config = {
    "jsc-s": {
        "hidden_layers": [64, 32, 32, 32],
        "input_bitwidth": 2,
        "hidden_bitwidth": 2,
        "output_bitwidth": 2,
        "input_fanin": 3,
        "hidden_fanin": 3,
        "output_fanin": 3,
        "weight_decay": 1e-3,
        "batch_size": 1024,
        "epochs": 1000,
        "learning_rate": 1e-3,
        "seed": 2,
        "checkpoint": None,
    },
    "jsc-m": {
        "hidden_layers": [64, 32, 32, 32],
        "input_bitwidth": 3,
        "hidden_bitwidth": 3,
        "output_bitwidth": 3,
        "input_fanin": 4,
        "hidden_fanin": 4,
        "output_fanin": 4,
        "weight_decay": 1e-3,
        "batch_size": 1024,
        "epochs": 1000,
        "learning_rate": 1e-3,
        "seed": 3,
        "checkpoint": None,
    },
    "jsc-l": {
        "hidden_layers": [32, 64, 192, 192, 16],
        "input_bitwidth": 4,
        "hidden_bitwidth": 3,
        "output_bitwidth": 7,
        "input_fanin": 3,
        "hidden_fanin": 4,
        "output_fanin": 5,
        "weight_decay": 1e-3,
        "batch_size": 1024,
        "epochs": 1000,
        "learning_rate": 1e-3,
        "seed": 16,
        "checkpoint": None,
    },
}

if __name__ == "__main__":
    parser = ArgumentParser(description="Synthesize convert a PyTorch trained model into verilog")
    # parser.add_argument('--arch', type=str, choices=configs.keys(), default="jsc-s",
    #     help="Specific the neural network model to use (default: %(default)s)")
    parser.add_argument('--batch-size', type=int, default=None, metavar='N',
        help="Batch size for evaluation (default: %(default)s)")
    parser.add_argument('--input-bitwidth', type=int, default=None,
        help="Bitwidth to use at the input (default: %(default)s)")
    parser.add_argument('--hidden-bitwidth', type=int, default=None,
        help="Bitwidth to use for activations in hidden layers (default: %(default)s)")
    parser.add_argument('--output-bitwidth', type=int, default=None,
        help="Bitwidth to use at the output (default: %(default)s)")
    parser.add_argument('--input-fanin', type=int, default=None,
        help="Fanin to use at the input (default: %(default)s)")
    parser.add_argument('--hidden-fanin', type=int, default=None,
        help="Fanin to use for the hidden layers (default: %(default)s)")
    parser.add_argument('--output-fanin', type=int, default=None,
        help="Fanin to use at the output (default: %(default)s)")
    parser.add_argument('--hidden-layers', nargs='+', type=int, default=None,
        help="A list of hidden layer neuron sizes (default: %(default)s)")
    parser.add_argument('--dataset-file', type=str, default='data/processed-pythia82-lhc13-all-pt1-50k-r1_h022_e0175_t220_nonu_truth.z',
        help="The file to use as the dataset input (default: %(default)s)")
    parser.add_argument('--clock-period', type=float, default=1.0,
        help="Target clock frequency to use during Vivado synthesis (default: %(default)s)")
    parser.add_argument('--dataset-config', type=str, default='config/yaml_IP_OP_config.yml',
        help="The file to use to configure the input dataset (default: %(default)s)")
    parser.add_argument('--dataset-split', type=str, default='test', choices=['train', 'test'],
        help="Dataset to use for evaluation (default: %(default)s)")
    parser.add_argument('--log-dir', type=str, default='./log',
        help="A location to store the log output of the training run and the output model (default: %(default)s)")
    parser.add_argument('--checkpoint', type=str, required=True,
        help="The checkpoint file which contains the model weights")
    parser.add_argument('--generate-bench', action='store_true', default=False,
        help="Generate the truth table in BENCH format as well as verilog (default: %(default)s)")
    parser.add_argument('--dump-io', action='store_true', default=False,
        help="Dump I/O to the verilog LUT to a text file in the log directory (default: %(default)s)")
    parser.add_argument('--add-registers', action='store_true', default=False,
        help="Add registers between each layer in generated verilog (default: %(default)s)")
    parser.add_argument('--simulate-pre-synthesis-verilog', action='store_true', default=False,
        help="Simulate the verilog generated by LogicNets (default: %(default)s)")
    parser.add_argument('--simulate-post-synthesis-verilog', action='store_true', default=False,
        help="Simulate the post-synthesis verilog produced by vivado (default: %(default)s)")
    parser.add_argument(
        "--config", 
        type=str, 
        default=None, 
        help="Path to a YAML file containing the model configuration"
    )
    args = parser.parse_args()
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)

    # Fetch the test set
    dataset = {}
    dataset["test"] = JetSubstructureDataset(args.dataset_file, args.dataset_config, split="test")
    test_loader = DataLoader(dataset["test"], batch_size=config['batch_size'], shuffle=False)

    # Instantiate the PyTorch model
    x, y = dataset[args.dataset_split][0]
    config['input_length'] = len(x)
    config['output_length'] = len(y)
    # Ensemble settings
    quantize_avg = False
    if "quantize_avg" in config:
        quantize_avg = config["quantize_avg"]
    if "post_transform_output" not in config:
        config["post_transform_output"] = True # Default
    if "same_output_scale" not in config:
        config["same_output_scale"] = False # Default

    # Instantiate NEQ and LUT-based models
    if "ensemble_method" in config:
        if config["ensemble_method"] == "averaging":
            print("Averaging ensemble method")
            model = AveragingJetNeqModel(config, config["ensemble_size"])
            lut_model = AveragingJetLUTModel(
                config, config["ensemble_size"], quantize_avg=quantize_avg
            )
        # elif config["ensemble_method"] == "bagging":
        #     print("Bagging ensemble method")
        #     if "independent" not in config:
        #         config["independent"] = False # Default
        #     lut_model = BaggingJetNeqModel(
        #         config,
        #         config["ensemble_size"],
        #         quantize_avg=quantize_avg,
        #         single_model_mode=args.train,
        #     )
        # elif config["ensemble_method"] == "adaboost":
        #     print("AdaBoost ensemble method")
        #     if "independent" not in config:
        #         config["independent"] = False # Default
        #     lut_model = AdaBoostJetNeqModel(
        #         config,
        #         config["ensemble_size"],
        #         len(dataset["train"]),
        #         quantize_avg=quantize_avg,
        #         single_model_mode=args.train,
        #     )
        else:
            raise ValueError(f"Unknown ensemble method: {config['ensemble_method']}")
    else:  # Single model learning
        model = JetSubstructureNeqModel(config)
        lut_model = JetSubstructureLutModel(config)
    
    # Load the model weights
    checkpoint = torch.load(args.checkpoint, map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_dict'])
    # Test the PyTorch model
    print("Running inference on baseline model...")
    model.eval()
    baseline_accuracy, baseline_avg_roc_auc, _ = test(model, test_loader, cuda=False)
    print("Baseline accuracy: %f" % (baseline_accuracy))
    print("Baseline AVG ROC AUC: %f" % (baseline_avg_roc_auc))
    # Load LUT model weights
    lut_model.load_state_dict(checkpoint['model_dict'])

    # Generate the truth tables in the LUT module
    print("Converting to NEQs to LUTs...")
    generate_truth_tables(lut_model, verbose=True)

    # Test the LUT-based model
    print("Running inference on LUT-based model...")
    lut_inf_start_time = time.time()
    lut_inference(lut_model)
    lut_model.eval()
    lut_accuracy, lut_avg_roc_auc, _ = test(lut_model, test_loader, cuda=False)
    print("LUT-Based Model accuracy: %f" % (lut_accuracy))
    print("LUT-Based AVG ROC AUC: %f" % (lut_avg_roc_auc))
    print(f"LUT inference took: {time.time() - lut_inf_start_time} s")
    modelSave = {   'model_dict': lut_model.state_dict(),
                    'test_accuracy': lut_accuracy,
                    'test_avg_roc_auc': lut_avg_roc_auc}

    torch.save(modelSave, args.log_dir + "/lut_based_model.pth")

    print("Generating verilog in %s..." % (args.log_dir))
    if "ensemble_method" in config:
        ensemble_to_verilog_module(
            lut_model.ensemble,
            "logicnet", 
            args.log_dir, 
            add_registers=args.add_registers,
            generate_bench=args.generate_bench,
        )
    else: # single model
        module_list_to_verilog_module(
            lut_model.module_list, 
            "logicnet", 
            args.log_dir, 
            add_registers=args.add_registers,
            generate_bench=args.generate_bench,
        )
        print("Top level entity stored at: %s/logicnet.v ..." % (args.log_dir))

    # END - pyverilator doesn't really work well...


    if args.dump_io:
        io_filename = os.path.join(args.log_dir, f"io_{args.dataset_split}.txt")
        with open(io_filename, 'w') as f:
            pass # Create an empty file.
        print(f"Dumping verilog I/O to {io_filename}...")
    else:
        io_filename = None

    if args.simulate_pre_synthesis_verilog:
        print("Running inference simulation of Verilog-based model...")
        lut_model.verilog_inference(args.log_dir, "logicnet.v", logfile=io_filename, add_registers=args.add_registers)
        verilog_accuracy, verilog_avg_roc_auc, _ = test(lut_model, test_loader, cuda=False)
        print("Verilog-Based Model accuracy: %f" % (verilog_accuracy))
        print("Verilog-Based AVG ROC AUC: %f" % (verilog_avg_roc_auc))

    print("Running out-of-context synthesis")
    ret = synthesize_and_get_resource_counts(
        args.log_dir, 
        "logicnet", 
        # fpga_part="xcu280-fsvh2892-2L-e", 
        fpga_part="xcvu9p-flgb2104-2-i", # LogicNets default
        clk_period_ns=args.clock_period, 
        post_synthesis=1
    )

    # if args.simulate_post_synthesis_verilog:
    #     print("Running post-synthesis inference simulation of Verilog-based model...")
    #     proc_postsynth_file(options_cfg["log_dir"])
    #     lut_model.verilog_inference(options_cfg["log_dir"]+"/post_synth", "logicnet_post_synth.v", io_filename, add_registers=options_cfg["add_registers"])
    #     post_synth_accuracy, post_synth_avg_roc_auc = test(lut_model, test_loader, cuda=False)
    #     print("Post-synthesis Verilog-Based Model accuracy: %f" % (post_synth_accuracy))
    #     print("Post-synthesis Verilog-Based AVG ROC AUC: %f" % (post_synth_avg_roc_auc))
    
