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

    # Ensemble default settings
    quantize_avg = False
    if "quantize_avg" in config:
        quantize_avg = config["quantize_avg"]
    if "post_transform_output" not in config:
        config["post_transform_output"] = True 
    if "same_output_scale" not in config:
        config["same_output_scale"] = False
    if "same_output_scale_sum" not in config:
        config["same_output_scale_sum"] = False
    if "same_input_scale" not in config:
        config["same_input_scale"] = False
    if "input_post_trans_sbs" not in config:
        config["input_post_trans_sbs"] = False
    if "input_post_trans_ssb" not in config:
        config["input_post_trans_ssb"] = False
    if "shared_input_quant" not in config:
        config["shared_input_quant"] = False 
    if "shared_input_layer" not in config:
        config["shared_input_layer"] = False
    if "uniform_input_connectivity" not in config:
        config["uniform_input_connectivity"] = False 
    if "uniform_connectivity" not in config:
        config["uniform_connectivity"] = False 

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

    # Train
    if args.train:
        # Log experiment hyperparameters
        hparams_log = os.path.join(experiment_dir, "hparams.yml")
        with open(hparams_log, "w") as f:
            yaml.dump(config, f)
        if "ensemble_method" in config and config["ensemble_method"] != "averaging":
            if config["ensemble_method"] == "bagging":
                train_bagging(
                    model, dataset, config, cuda=args.cuda, log_dir=experiment_dir
                )
            elif config["ensemble_method"] == "adaboost":
                train_adaboost(
                    model, dataset, config, cuda=args.cuda, log_dir=experiment_dir
                )
        else: # Single model / Averaging training
            train(model, dataset, config, cuda=args.cuda, log_dir=experiment_dir)
    # Evaluate model
    evaluate_model = False
    if args.evaluate:
        if args.checkpoint:
            # Evaluate given checkpoint
            evaluate_model = True
            print(f"Evaluating model saved at: {args.checkpoint}")
            checkpoint = torch.load(args.checkpoint)
            model.load_state_dict(checkpoint["model_dict"])
            if (
                config["ensemble_method"] in ENSEMBLING_METHODS
                and config["ensemble_method"] != "averaging"
            ):
                model.single_model_mode = False
        else:
            raise ValueError(
                "No checkpoint provided for evaluation. "
                "Provide a path to checkpoint argument, "
                "i.e., --checkpoint CHECKPOINT_PATH"
            )
    elif args.train:
        evaluate_model = True  # Evaluate the model after training
        if (
            "ensemble_method" in config
            and config["ensemble_method"] in ENSEMBLING_METHODS
            and config["ensemble_method"] != "averaging"
        ):
            ensemble_ckpt_path = os.path.join(experiment_dir, "last_ensemble_ckpt.pth")
            print(f"Evaluating last ensemble saved at: {ensemble_ckpt_path}")
            best_checkpoint = torch.load(ensemble_ckpt_path)
            model.single_model_mode = False
        else:
            ckpt_path = os.path.join(experiment_dir, "best_accuracy.pth")
            print(f"Evaluating best model saved at: {ckpt_path}")
            best_checkpoint = torch.load(ckpt_path)
        model.load_state_dict(best_checkpoint["model_dict"])

    if evaluate_model:
        if args.cuda:
            model.cuda()
        print("Evaluating model")
        test_loader = DataLoader(
            dataset["test"], batch_size=config["batch_size"], shuffle=False
        )
        test_accuracy, test_avg_roc_auc, test_loss = test(model, test_loader, args.cuda)
        eval_tag = "_eval" if args.evaluate else ""
        os.makedirs(experiment_dir, exist_ok=True)
        test_results_log = os.path.join(
            experiment_dir,
            args.experiment_name
            + f"_loss={test_loss:.3f}"
            + eval_tag
            + "_accuracy.txt",
        )
        print(f"Test Accuracy: {test_accuracy:.2f}%")
        print(f"Test loss: {test_loss:.3f}")
        with open(test_results_log, "w") as f:
            f.write(str(test_accuracy))
            f.close()


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
