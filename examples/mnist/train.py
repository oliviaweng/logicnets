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
from functools import reduce, partial
import random

import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms
from torchvision.datasets import MNIST

from training_methods import test, train, train_bagging, train_adaboost

from models import MnistNeqModel
from ensemble import AveragingMnistNeqModel, AdaBoostMnistNeqModel, BaggingMnistNeqModel

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

    # Data augmentation and normalization for training
    trans = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
            transforms.Lambda(partial(torch.reshape, shape=(-1,))),
        ]
    )

    # Fetch the datasets
    dataset = {}
    dataset["train"] = MNIST("./data", train=True, download=True, transform=trans)
    dataset["valid"] = MNIST("./data", train=False, download=True, transform=trans)
    dataset["test"] = MNIST("./data", train=False, download=True, transform=trans)

    # Instantiate model
    x, y = dataset["train"][0]
    config["input_length"] = len(x)
    config["output_length"] = 10

    # Ensemble default settings
    if "shared_input_layer" not in config:
        config["shared_input_layer"] = False
    if "shared_output_layer" not in config:
        config["shared_output_layer"] = False

    # Instantiate the model
    if "ensemble_method" in config:
        if config["ensemble_method"] == "averaging":
            print("Averaging ensemble method")
            model = AveragingMnistNeqModel(
                config, config["ensemble_size"],
            )
        elif config["ensemble_method"] == "bagging":
            print("Bagging ensemble method")
            if "independent" not in config:
                config["independent"] = False # Default
            model = BaggingMnistNeqModel(
                config,
                config["ensemble_size"],
                single_model_mode=args.train,
            )
        elif config["ensemble_method"] == "adaboost":
            print("AdaBoost ensemble method")
            if "independent" not in config:
                config["independent"] = False # Default
            model = AdaBoostMnistNeqModel(
                config,
                config["ensemble_size"],
                len(dataset["train"]),
                single_model_mode=args.train,
            )
        else:
            raise ValueError(f"Unknown ensemble method: {config['ensemble_method']}")
    else:  # Single model learning
        model = MnistNeqModel(config)

    if config["checkpoint"] is not None:
        print(f"Loading pre-trained checkpoint {config['checkpoint']}")
        checkpoint = torch.load(config["checkpoint"], map_location="cpu")
        model.load_state_dict(checkpoint["model_dict"])

    print(f"Model: {model.__class__.__name__}")

    # train(model, dataset, train_cfg, options_cfg)
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
        else:  # Single model / Averaging training
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
        test_accuracy, test_loss = test(model, test_loader, args.cuda)
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
    parser = ArgumentParser(description="LogicNets MNIST Classification Example")
    parser.add_argument(
        "--cuda",
        action="store_true",
        default=False,
        help="Train on a GPU (default: %(default)s)",
    )
    parser.add_argument("--train", action="store_true", default=False)
    parser.add_argument("--evaluate", action="store_true", default=False)
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

    # parser.add_argument('--arch', type=str, choices=configs.keys(), default="mnist-s",
    #     help="Specific the neural network model to use (default: %(default)s)")
    # parser.add_argument('--weight-decay', type=float, default=None, metavar='D',
    #     help="Weight decay (default: %(default)s)")
    # parser.add_argument('--batch-size', type=int, default=None, metavar='N',
    #     help="Batch size for training (default: %(default)s)")
    # parser.add_argument('--epochs', type=int, default=None, metavar='N',
    #     help="Number of epochs to train (default: %(default)s)")
    # parser.add_argument('--learning-rate', type=float, default=None, metavar='LR',
    #     help="Initial learning rate (default: %(default)s)")
    # parser.add_argument('--seed', type=int, default=None,
    #     help="Seed to use for RNG (default: %(default)s)")
    # parser.add_argument('--input-bitwidth', type=int, default=None,
    #     help="Bitwidth to use at the input (default: %(default)s)")
    # parser.add_argument('--hidden-bitwidth', type=int, default=None,
    #     help="Bitwidth to use for activations in hidden layers (default: %(default)s)")
    # parser.add_argument('--output-bitwidth', type=int, default=None,
    #     help="Bitwidth to use at the output (default: %(default)s)")
    # parser.add_argument('--input-fanin', type=int, default=None,
    #     help="Fanin to use at the input (default: %(default)s)")
    # parser.add_argument('--hidden-fanin', type=int, default=None,
    #     help="Fanin to use for the hidden layers (default: %(default)s)")
    # parser.add_argument('--output-fanin', type=int, default=None,
    #     help="Fanin to use at the output (default: %(default)s)")
    # parser.add_argument('--hidden-layers', nargs='+', type=int, default=None,
    #     help="A list of hidden layer neuron sizes (default: %(default)s)")
    # parser.add_argument('--input-dropout', type=float, default=None,
    #     help="The amount of dropout to apply at the model input (default: %(default)s)")
    # parser.add_argument('--log-dir', type=str, default='./log',
    #     help="A location to store the log output of the training run and the output model (default: %(default)s)")
    # parser.add_argument('--checkpoint', type=str, default=None,
    #     help="Retrain the model from a previous checkpoint (default: %(default)s)")
