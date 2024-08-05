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
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from torchvision import datasets, transforms
from models import MnistNeqModel

# configs = {
#     "hdr": {
#         "hidden_layers": [256, 100, 100, 100, 100],
#         "input_bitwidth": 2,
#         "hidden_bitwidth": 2,
#         "output_bitwidth": 2,
#         "input_fanin": 6,
#         "degree": 4,
#         "hidden_fanin": 6,
#         "output_fanin": 6,
#         "weight_decay": 0,
#         "batch_size": 128,
#         "epochs": 500,
#         "learning_rate": 0.004,
#         "seed": 984237,
#         "checkpoint": None,
#     },
# }

# A dictionary, so we can set some defaults if necessary
# model_config = {
#     "hidden_layers": None,
#     "input_bitwidth": None,
#     "hidden_bitwidth": None,
#     "output_bitwidth": None,
#     "input_fanin": None,
#     "degree": None,
#     "hidden_fanin": None,
#     "output_fanin": None,
# }

# training_config = {
#     "weight_decay": None,
#     "batch_size": None,
#     "epochs": None,
#     "learning_rate": None,
#     "seed": None,
# }

# other_options = {
#     "cuda": None,
#     "log_dir": None,
#     "checkpoint": None,
#     "device": 1,
# }


def train(model, config, cuda=False, log_dir="./mnist"):
    # Create data loaders for training and inference:
    train_loader = DataLoader(
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
    val_loader = DataLoader(
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
    test_loader = DataLoader(
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

    # Configure optimizer
    weight_decay = config["weight_decay"]
    decay_exclusions = [
        "bn",
        "bias",
        "learned_value",
    ]  # Make a list of parameters name fragments which will ignore weight decay TODO: make this list part of the train_cfg
    decay_params = []
    no_decay_params = []
    for pname, params in model.named_parameters():
        if params.requires_grad:
            if reduce(
                lambda a, b: a or b, map(lambda x: x in pname, decay_exclusions)
            ):  # check if the current label should be excluded from weight decay
                # print("Disabling weight decay for %s" % (pname))
                no_decay_params.append(params)
            else:
                # print("Enabling weight decay for %s" % (pname))
                decay_params.append(params)
        # else:
        # print("Ignoring %s" % (pname))
    params = [
        {"params": decay_params, "weight_decay": weight_decay},
        {"params": no_decay_params, "weight_decay": 0.0},
    ]

    optimizer = optim.AdamW(
        params,
        lr=config["learning_rate"],
        betas=(0.5, 0.999),
        weight_decay=weight_decay,
    )

    # Configure scheduler
    steps = len(train_loader)
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=steps * 100, T_mult=1
    )

    # Configure criterion
    criterion = nn.CrossEntropyLoss()

    # Push the model to the GPU, if necessary
    if cuda:
        model.cuda()


    # Main training loop
    maxAcc = 0.0
    num_epochs = config["epochs"]
    for epoch in range(0, num_epochs):
        # Train for this epoch
        model.train()
        accLoss = 0.0
        correct = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            if cuda:
                data, target = data.cuda(), target.cuda()
            optimizer.zero_grad()
            data = data.reshape(-1, 784)
            target = torch.nn.functional.one_hot(target, num_classes=10)
            output = model(data)
            loss = criterion(output, torch.max(target, 1)[1])
            pred = output.detach().max(1, keepdim=True)[1]
            target_label = torch.max(target.detach(), 1, keepdim=True)[1]
            curCorrect = pred.eq(target_label).long().sum()
            curAcc = 100.0 * curCorrect / len(data)
            correct += curCorrect
            accLoss += loss.detach() * len(data)
            loss.backward()
            optimizer.step()
            scheduler.step()

        accLoss /= len(train_loader.dataset)
        accuracy = 100.0 * correct / len(train_loader.dataset)
        val_accuracy = test(model, val_loader, cuda)
        test_accuracy = test(model, test_loader, cuda)
        modelSave = {
            "model_dict": model.state_dict(),
            "optim_dict": optimizer.state_dict(),
            "val_accuracy": val_accuracy,
            "test_accuracy": test_accuracy,
            "epoch": epoch,
        }
        torch.save(modelSave, os.path.join(log_dir, "checkpoint.pth"))
        if maxAcc < test_accuracy:
            torch.save(modelSave, os.path.join(log_dir, "best_accuracy.pth"))
            maxAcc = test_accuracy

        wandb.log(
            {
                "Train Acc (%)": accuracy.detach().cpu().numpy(),
                "Train Loss(%)": accLoss.detach().cpu().numpy(),
                "Test Acc (%)": test_accuracy,
                "Valid Acc(%)": val_accuracy,
            }
        )


def test(model, dataset_loader, cuda):
    model.eval()
    correct = 0
    accLoss = 0.0
    for batch_idx, (data, target) in enumerate(dataset_loader):
        if cuda:
            data, target = data.cuda(), target.cuda()
        data = data.reshape(-1, 784)
        target = torch.nn.functional.one_hot(target, num_classes=10)
        output = model(data)
        pred = output.detach().max(1, keepdim=True)[1]
        target_label = torch.max(target.detach(), 1, keepdim=True)[1]
        curCorrect = pred.eq(target_label).long().sum()
        curAcc = 100.0 * curCorrect / len(data)
        correct += curCorrect
    accuracy = 100 * float(correct) / len(dataset_loader.dataset)
    return accuracy


def main(args):
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    # Create experiment directory
    experiment_dir = os.path.join(args.save_dir, args.experiment_name)
    os.makedirs(experiment_dir, exist_ok=True)
    # defaults = configs[args.arch]
    # options = vars(args)
    # del options["arch"]
    # config = {}
    # for k in options.keys():
    #     config[k] = (
    #         options[k] if options[k] is not None else defaults[k]
    #     )  # Override defaults, if specified.

    # if not os.path.exists("test_" + config["log_dir"]):
    #     os.makedirs("test_" + config["log_dir"])

    # # Split up configuration options to be more understandable
    # model_cfg = {}
    # for k in model_config.keys():
    #     model_cfg[k] = config[k]
    # train_cfg = {}
    # for k in training_config.keys():
    #     train_cfg[k] = config[k]
    # options_cfg = {}
    # for k in other_options.keys():
    #     options_cfg[k] = config[k]

    # Set random seeds
    random.seed(config["seed"])
    np.random.seed(config["seed"])
    torch.manual_seed(config["seed"])
    os.environ["PYTHONHASHSEED"] = str(config["seed"])
    if args.cuda:
        torch.cuda.manual_seed_all(config["seed"])
        torch.backends.cudnn.deterministic = True
        torch.cuda.set_device(args.device)
    config["gpu"] = args.cuda

    # Instantiate model
    config["input_length"] = 784
    config["output_length"] = 10
    model = MnistNeqModel(config)

    if args.checkpoint is not None:
        print(f"Loading pre-trained checkpoint {args.checkpoint}")
        checkpoint = torch.load(args.checkpoint, map_location="cpu")
        model.load_state_dict(checkpoint["model_dict"])

    # start a new wandb run to track this script
    wandb.init(
        # set the wandb project where this run will be logged
        project="PolyLUT",
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
    wandb.watch(model, log_freq=10)
    train(model, config, cuda=args.cuda, log_dir=experiment_dir)
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
    
