import os
import torch
import numpy as np
from tqdm import tqdm, trange
from functools import reduce

import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter


def test(model, dataset_loader, cuda):
    # Configure criterion
    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        model.eval()
        correct = 0
        accLoss = 0.0
        for _, (data, target) in enumerate(dataset_loader):
            if cuda:
                data, target = data.cuda(), target.cuda()
            output = model(data)
            loss = criterion(output, target)
            pred = output.detach().max(1, keepdim=True)[1]
            target_label = target.detach().unsqueeze(1)
            curCorrect = pred.eq(target_label).long().sum()
            accLoss += loss.detach() * len(data)
            correct += curCorrect
        accuracy = 100 * float(correct) / len(dataset_loader.dataset)
        accLoss /= len(dataset_loader.dataset)
    return accuracy, accLoss


def train(model, datasets, config, cuda=False, log_dir="./mnist", sampler=None):
    # Create data loaders for training and inference:
    train_loader = DataLoader(
        datasets["train"], batch_size=config["batch_size"], shuffle=True
    )
    val_loader = DataLoader(
        datasets["valid"], batch_size=config["batch_size"], shuffle=False
    )
    test_loader = DataLoader(
        datasets["test"], batch_size=config["batch_size"], shuffle=False
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
                print("Disabling weight decay for %s" % (pname))
                no_decay_params.append(params)
            else:
                print("Enabling weight decay for %s" % (pname))
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

    # Setup tensorboard
    writer = SummaryWriter(log_dir)

    # Main training loop
    maxAcc = 0.0
    num_epochs = config["epochs"]
    for epoch in trange(0, num_epochs):
        # Train for this epoch
        model.train()
        accLoss = 0.0
        correct = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            if cuda:
                data, target = data.cuda(), target.cuda()
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            pred = output.detach().max(1, keepdim=True)[1]
            target_label = target.detach().unsqueeze(1)
            curCorrect = pred.eq(target_label).long().sum()
            curAcc = 100.0 * curCorrect / len(data)
            correct += curCorrect
            accLoss += loss.detach() * len(data)
            loss.backward()
            optimizer.step()
            scheduler.step()

        accLoss /= len(train_loader.dataset)
        accuracy = 100.0 * correct / len(train_loader.dataset)
        print(
            f"Epoch: {epoch}/{num_epochs}\tTrain Acc (%): {accuracy.detach().cpu().numpy():.2f}\tTrain Loss: {accLoss.detach().cpu().numpy():.3e}"
        )
        # for g in optimizer.param_groups:
        #        print("LR: {:.6f} ".format(g['lr']))
        #        print("LR: {:.6f} ".format(g['weight_decay']))
        writer.add_scalar(
            "avg_train_loss", accLoss.detach().cpu().numpy(), (epoch + 1) * steps
        )
        writer.add_scalar(
            "avg_train_accuracy", accuracy.detach().cpu().numpy(), (epoch + 1) * steps
        )
        val_accuracy, val_loss = test(model, val_loader, cuda)
        test_accuracy, test_loss = test(model, test_loader, cuda)
        modelSave = {
            "model_dict": model.state_dict(),
            "optim_dict": optimizer.state_dict(),
            "val_accuracy": val_accuracy,
            "test_accuracy": test_accuracy,
            "epoch": epoch,
        }
        torch.save(modelSave, os.path.join(log_dir, "checkpoint.pth"))
        if maxAcc < val_accuracy:
            torch.save(modelSave, os.path.join(log_dir, "best_accuracy.pth"))
            maxAcc = val_accuracy
        writer.add_scalar("val_accuracy", val_accuracy, (epoch + 1) * steps)
        writer.add_scalar("val_loss", val_loss, (epoch + 1) * steps)
        writer.add_scalar("test_accuracy", test_accuracy, (epoch + 1) * steps)
        writer.add_scalar("test_loss", test_loss, (epoch + 1) * steps)
        print(
            f"Epoch: {epoch}/{num_epochs}\tValid Acc (%): {val_accuracy:.2f}\tTest Acc: {test_accuracy:.2f}"
        )
