import os
import yaml
from argparse import ArgumentParser
import random

import numpy as np

import torch
from torch.utils.data import DataLoader

from training_methods import train, test, train_bagging, train_adaboost

from dataset import JetSubstructureDataset
from models import JetSubstructureNeqModel
from ensemble import AveragingJetNeqModel, BaggingJetNeqModel, AdaBoostJetNeqModel

ENSEMBLING_METHODS = ["adaboost", "averaging", "bagging"]


def main(args):
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    # Create experiment directory
    experiment_dir = os.path.join(args.save_dir, args.experiment_name)
    os.makedirs(experiment_dir, exist_ok=True)

    # Set random seeds
    random.seed(config["seed"])
    np.random.seed(config["seed"])
    torch.manual_seed(config["seed"])
    os.environ["PYTHONHASHSEED"] = str(config["seed"])
    if args.cuda:
        torch.cuda.manual_seed_all(config["seed"])
        torch.backends.cudnn.deterministic = True

    # Fetch the datasets
    dataset = {}
    dataset["train"] = JetSubstructureDataset(
        args.dataset_file, args.dataset_config, split="train"
    )
    # This dataset is so small, we'll just use the training set as the validation set, otherwise we may have too few trainings examples to converge.
    dataset["valid"] = JetSubstructureDataset(
        args.dataset_file, args.dataset_config, split="train"
    )
    dataset["test"] = JetSubstructureDataset(
        args.dataset_file, args.dataset_config, split="test"
    )

    # Instantiate model
    x, y = dataset["train"][0]
    config["input_length"] = len(x)
    config["output_length"] = len(y)

    # Ensemble settings
    quantize_avg = False
    if "quantize_avg" in config:
        quantize_avg = config["quantize_avg"]
    if "post_transform_output" not in config:
        config["post_transform_output"] = True # Default
    if "same_output_scale" not in config:
        config["same_output_scale"] = False # Default
    
    if "ensemble_method" in config:
        if config["ensemble_method"] == "averaging":
            print("Averaging ensemble method")
            model = AveragingJetNeqModel(
                config, config["ensemble_size"], quantize_avg=quantize_avg
            )
        elif config["ensemble_method"] == "bagging":
            print("Bagging ensemble method")
            if "independent" not in config:
                config["independent"] = False # Default
            model = BaggingJetNeqModel(
                config,
                config["ensemble_size"],
                quantize_avg=quantize_avg,
                single_model_mode=args.train,
            )
        elif config["ensemble_method"] == "adaboost":
            print("AdaBoost ensemble method")
            if "independent" not in config:
                config["independent"] = False # Default
            model = AdaBoostJetNeqModel(
                config,
                config["ensemble_size"],
                len(dataset["train"]),
                quantize_avg=quantize_avg,
                single_model_mode=args.train,
            )
        else:
            raise ValueError(f"Unknown ensemble method: {config['ensemble_method']}")
    else:  # Single model learning
        model = JetSubstructureNeqModel(config)
    if args.checkpoint is not None:
        print(f"Loading pre-trained checkpoint {args.checkpoint}")
        checkpoint = torch.load(args.checkpoint, map_location="cpu")
        model.load_state_dict(checkpoint["model_dict"])

    print(f"Model: {model.__class__.__name__}")

    # Print output quantizer scaling factors per model
    out_scale_factor = None
    for i, m in enumerate(model.ensemble):
        quant_state_dict = m.module_list[-1].output_quant.state_dict()
        curr_out_scale_factor = quant_state_dict['brevitas_module.act_quant_proxy.fused_activation_quant_proxy.tensor_quant.scaling_impl.learned_value']
        if curr_out_scale_factor != out_scale_factor:
            print(f"Model {i}")
            print(f"    output scaling factor: {curr_out_scale_factor}")
            if "post_transforms.0.weight" in quant_state_dict:
                print(f"    output post transform weight: {quant_state_dict['post_transforms.0.weight']}")
                print(f"    output post transform bias: {quant_state_dict['post_transforms.0.bias']}")
            print("------")
        out_scale_factor = curr_out_scale_factor



if __name__ == "__main__":
    parser = ArgumentParser(
        description="LogicNets Jet Substructure Classification Example"
    )
    parser.add_argument(
        "--cuda",
        action="store_true",
        default=False,
        help="Train on a GPU (default: %(default)s)",
    )
    parser.add_argument("--train", action="store_true", default=False)
    parser.add_argument("--evaluate", action="store_true", default=False)
    parser.add_argument(
        "--dataset-file",
        type=str,
        default="data/processed-pythia82-lhc13-all-pt1-50k-r1_h022_e0175_t220_nonu_truth.z",
        help="The file to use as the dataset input (default: %(default)s)",
    )
    parser.add_argument(
        "--dataset-config",
        type=str,
        default="config/yaml_IP_OP_config.yml",
        help="The file to use to configure the input dataset (default: %(default)s)",
    )
    parser.add_argument("--save_dir", type=str, default="./jet_tagger")
    parser.add_argument("--experiment_name", type=str, default="jsc")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Load the model from a previous checkpoint (default: %(default)s)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a YAML file containing the model configuration",
    )

    args = parser.parse_args()
    main(args)
