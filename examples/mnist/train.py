#  This file is part of PolyLUT.
#  
#  PolyLUT is a derivative work based on LogicNets,
#  which is licensed under the Apache License 2.0.

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
from functools import reduce
import random

import numpy as np
import wandb
import random

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from models import MnistNeqModel
from training_methods import train, test, train_bagging, train_adaboost
from ensemble import AveragingMnistNeqModel, BaggingMnistNeqModel, AdaBoostMnistNeqModel

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
    config["gpu"] = args.cuda

    # Create data loaders for training and inference:
    dataloaders = {}
    dataloaders["train"] = DataLoader(
        datasets.MNIST(
            "mnist_data",
            download=False,
            train=True,
            transform=transforms.Compose(
                [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
            ),
        ),
        batch_size=config["batch_size"],
        shuffle=True,
    )
    dataloaders["valid"] = DataLoader(
        datasets.MNIST(
            "mnist_data",
            download=False,
            train=True,
            transform=transforms.Compose(
                [
                    transforms.ToTensor(),  # first, convert image to PyTorch tensor
                    transforms.Normalize((0.1307,), (0.3081,)),  # normalize inputs
                ]
            ),
        ),
        batch_size=config["batch_size"],
        shuffle=False,
    )
    dataloaders["test"] = DataLoader(
        datasets.MNIST(
            "mnist_data",
            download=False,
            train=False,
            transform=transforms.Compose(
                [
                    transforms.ToTensor(),  # first, convert image to PyTorch tensor
                    transforms.Normalize((0.1307,), (0.3081,)),  # normalize inputs
                ]
            ),
        ),
        batch_size=config["batch_size"],
        shuffle=False,
    )

    # Instantiate model
    config["input_length"] = 784
    config["output_length"] = 10

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
            model = AveragingMnistNeqModel(
                config, config["ensemble_size"], quantize_avg=quantize_avg
            )
        elif config["ensemble_method"] == "bagging":
            print("Bagging ensemble method")
            if "independent" not in config:
                config["independent"] = False # Default
            model = BaggingMnistNeqModel(
                config,
                config["ensemble_size"],
                quantize_avg=quantize_avg,
                single_model_mode=args.train,
            )
        elif config["ensemble_method"] == "adaboost":
            print("AdaBoost ensemble method")
            if "independent" not in config:
                    config["independent"] = False # Default
            model = AdaBoostMnistNeqModel(
                config,
                config["ensemble_size"],
                len(dataloaders["train"].dataset),
                num_classes=config["output_length"],
                quantize_avg=quantize_avg,
                single_model_mode=args.train,
            )
        else:
            raise ValueError(f"Unknown ensemble method: {config['ensemble_method']}")
    else:  # Single model learning
        model = MnistNeqModel(config)

    if args.checkpoint is not None:
        print(f"Loading pre-trained checkpoint {args.checkpoint}")
        checkpoint = torch.load(args.checkpoint, map_location="cpu")
        model.load_state_dict(checkpoint["model_dict"])

    print(f"Model: {model.__class__.__name__}")
    # Train
    if args.train:
        # Save hyperparameter config
        hparams_log = os.path.join(experiment_dir, "hparams.yml")
        with open(hparams_log, "w") as f:
            yaml.dump(config, f)
        # start a new wandb run to track this script
        wandb.init(
            # set the wandb project where this run will be logged
            project="PolyLUT",
            name=args.experiment_name,
            # track hyperparameters and run metadata
            config={
                "hidden_layers": config["hidden_layers"],
                "input_bitwidth": config["input_bitwidth"],
                "hidden_bitwidth": config["hidden_bitwidth"],
                "output_bitwidth": config["output_bitwidth"],
                "input_fanin": config["input_fanin"],
                "degree": config["degree"],
                "hidden_fanin": config["hidden_fanin"],
                "output_fanin": config["output_fanin"],
                "weight_decay": config["weight_decay"],
                "batch_size": config["batch_size"],
                "epochs": config["epochs"],
                "learning_rate": config["learning_rate"],
                "seed": config["seed"],
                "dataset": "mnist",
            },
        )

        wandb.define_metric("Train Acc (%)", summary="max")
        wandb.define_metric("Test Acc (%)", summary="max")
        wandb.define_metric("Valid Acc(%)", summary="max")
        wandb.define_metric("Train Loss(%)", summary="min")
        wandb.define_metric("Test Loss", summary="min")
        wandb.define_metric("Val Loss", summary="min")
        wandb.watch(model, log_freq=10)
        if config["ensemble_method"] == "bagging":
            train_bagging(model, dataloaders, config, cuda=args.cuda, log_dir=experiment_dir)
        elif config["ensemble_method"] == "adaboost":
            train_adaboost(model, dataloaders, config, cuda=args.cuda, log_dir=experiment_dir)
        else:
            train(model, dataloaders, config, cuda=args.cuda, log_dir=experiment_dir)
        
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
            config["ensemble_method"] in ENSEMBLING_METHODS
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
        test_accuracy, test_loss = test(model, dataloaders["test"], args.cuda)
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
    wandb.finish()


if __name__ == "__main__":
    parser = ArgumentParser(description="PolyLUT Example")
    parser.add_argument(
        "--cuda",
        action="store_true",
        default=True,
        help="Train on a GPU (default: %(default)s)",
    )
    parser.add_argument("--train", action="store_true", default=False)
    parser.add_argument("--evaluate", action="store_true", default=False)
    parser.add_argument("--save_dir", type=str, default="./mnist")
    parser.add_argument("--experiment_name", type=str, default="hdr")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        metavar="",
        help="Retrain the model from a previous checkpoint (default: %(default)s)",
    )
    parser.add_argument(
        "--device", 
        type=int, 
        default=0, 
        metavar="", 
        help="Device_id for GPU",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a YAML file containing the model configuration",
    )
    args = parser.parse_args()
    main(args)
    
