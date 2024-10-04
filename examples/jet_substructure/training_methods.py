import os
import math
import torch
import datetime
import numpy as np
from tqdm import tqdm, trange
from functools import reduce
from sklearn.metrics import roc_auc_score

import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader

from models import JetSubstructureNeqModel
import wandb

def test(model, dataset_loader, cuda):
    # Configure criterion
    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        model.eval()
        entire_prob = None
        golden_ref = None
        correct = 0
        accLoss = 0.0
        for batch_idx, (data, target) in enumerate(dataset_loader):
            if cuda:
                data, target = data.cuda(), target.cuda()
            output = model(data)
            if cuda:
                output = output.cuda()
            loss = criterion(output, torch.max(target, 1)[1])
            accLoss += loss.detach() * len(data)
            prob = F.softmax(output, dim=1)
            pred = output.detach().max(1, keepdim=True)[1]
            target_label = torch.max(target.detach(), 1, keepdim=True)[1]
            curCorrect = pred.eq(target_label).long().sum()
            curAcc = 100.0 * curCorrect / len(data)
            correct += curCorrect
            if batch_idx == 0:
                entire_prob = prob
                golden_ref = target_label
            else:
                entire_prob = torch.cat((entire_prob, prob), dim=0)
                golden_ref = torch.cat((golden_ref, target_label))
        accLoss /= len(dataset_loader.dataset)
        accuracy = 100 * float(correct) / len(dataset_loader.dataset)
        return accuracy, accLoss


def train(model, datasets, config, cuda=False, log_dir="./jsc", sampler=None):
    # Create data loaders for training and inference:
    if sampler:  # Use the provided sampler
        train_loader = DataLoader(
            datasets["train"],
            batch_size=config["batch_size"],
            shuffle=False,
            sampler=sampler,
        )
    else:  # Default train loader
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
        print(
            f"Epoch: {epoch}/{num_epochs}\tTrain Acc (%): {accuracy.detach().cpu().numpy():.2f}\tTrain Loss: {accLoss.detach().cpu().numpy():.3e}"
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
        if maxAcc < test_accuracy:
            torch.save(modelSave, os.path.join(log_dir, "best_accuracy.pth"))
            maxAcc = test_accuracy
        wandb.log(
            {
                "Train Acc (%)": accuracy.detach().cpu().numpy(),
                "Train Loss(%)": accLoss.detach().cpu().numpy(),
                "Test Acc (%)": test_accuracy,
                "Valid Acc(%)": val_accuracy,
                "Test Loss": test_loss,
                "Val Loss": val_loss,
            }
        )


def train_bagging(model, datasets, config, cuda=False, log_dir="./jsc"):
    """
    Train an ensemble of models using bagging (bootstrap aggregating), where
    each member model has its own training dataset generated from the original
    training set by sampling with replacement.

    By default, we are continuously training each model in the ensemble by starting
    from the best weights of the previous model. This is a form of warm-restarting
    the training process for each model in the ensemble. Based on:
        Zhu et al. Binary Ensemble Neural Network: More bits per Network or More
        Networks per Bit? CVPR'19
    """
    test_loader = DataLoader(
        datasets["test"], batch_size=config["batch_size"], shuffle=False
    )
    # Draw training samples based on equal weights
    num_train_samples = len(datasets["train"])
    for i in range(model.num_models):
        model.single_model_mode = True
        if config["independent"] and i > 0: 
            # Start w/fresh model each time
            print("Independent training mode")
            model.model = JetSubstructureNeqModel(config)
            if cuda:
                model.cuda()
        # Create bagging sampler
        subset_indices = np.random.choice(num_train_samples, size=num_train_samples)
        sampler = torch.utils.data.sampler.SubsetRandomSampler(subset_indices)
        # Train model
        train(model, datasets, config, cuda=cuda, log_dir=log_dir, sampler=sampler)
        # Evaluate best single model on validation data
        best_checkpoint = torch.load(os.path.join(log_dir, "best_accuracy.pth"))
        model.load_state_dict(best_checkpoint["model_dict"])
        print("Evaluate best single model performance")
        test_accuracy, _, test_loss = test(model, test_loader, cuda=cuda)
        # Log single model performance
        os.makedirs(log_dir, exist_ok=True)
        ensemble_perf_log = os.path.join(log_dir, f"ensemble_perf.txt")
        with open(ensemble_perf_log, "a") as f:
            f.write(
                f"Single model {i + 1} test loss: {test_loss}\tAccuracy = {test_accuracy}\n"
            )
        # Save model to ensemble
        snapshot = JetSubstructureNeqModel(config)
        if cuda:
            snapshot.cuda()
        snapshot.load_state_dict(model.model.state_dict())
        model.ensemble.append(snapshot)
        # Evaluate ensemble on validation data and save ensemble checkpoint
        ensemble_test_loss, ensemble_test_acc = evaluate_ensemble(
            model, datasets, config, cuda=cuda, log_dir=log_dir
        )
        ensemble_ckpt = {
            "model_dict": model.state_dict(),
            "test_loss": ensemble_test_loss,
            "test_acc": ensemble_test_acc,
        }
        torch.save(ensemble_ckpt, os.path.join(log_dir, "last_ensemble_ckpt.pth"))
        print(f"Saved Bagging model # {len(model.ensemble)}")


def evaluate_ensemble(model, datasets, config, cuda=False, log_dir="./jsc"):
    """
    Evaluate ensemble performance on test dataset
    """
    print("Evaluate ensemble performance")
    model.single_model_mode = False
    test_loader = DataLoader(
        datasets["test"], batch_size=config["batch_size"], shuffle=False
    )
    test_accuracy, _, test_loss = test(model, test_loader, cuda)
    # Log ensemble performance
    os.makedirs(log_dir, exist_ok=True)
    ensemble_perf_log = os.path.join(log_dir, f"ensemble_perf.txt")
    with open(ensemble_perf_log, "a") as f:
        f.write(
            f"Ensemble size {len(model.ensemble)} test loss: {test_loss}\tAccuracy = {test_accuracy}\n"
        )
    model.single_model_mode = True
    return test_loss, test_accuracy


def train_adaboost(model, datasets, config, cuda=False, log_dir="./jsc"):
    """
    Train an ensemble of models using AdaBoost, where each model is trained
    sequentially with the training data weighted by the performance of the
    previous model. The weights are updated based on the performance of the
    current model.
    """
    test_loader = DataLoader(
        datasets["test"], batch_size=config["batch_size"], shuffle=False
    )
    for i in range(model.num_models):
        model.single_model_mode = True
        if config["independent"] and i > 0: 
            # Start w/fresh model each time
            print("Independent training mode")
            model.model = JetSubstructureNeqModel(config)
            if cuda:
                model.cuda()
        # Draw training samples based on sample weights
        sampler = torch.utils.data.sampler.WeightedRandomSampler(
            model.weights,
            model.num_train_samples,
            replacement=True,
        )
        # Train model
        train(model, datasets, config, cuda=cuda, log_dir=log_dir, sampler=sampler)
        # Evaluate best single model on validation data
        best_checkpoint = torch.load(os.path.join(log_dir, "best_accuracy.pth"))
        model.load_state_dict(best_checkpoint["model_dict"])
        print("Evaluate best single model performance")
        test_accuracy, _, test_loss = test(model, test_loader, cuda=cuda)
        # Log single model performance
        os.makedirs(log_dir, exist_ok=True)
        ensemble_perf_log = os.path.join(log_dir, f"ensemble_perf.txt")
        # Compute model error epsilon
        model_error, incorrect_train_idx = compute_adaboost_model_error(
            model, datasets, config, cuda
        )
        with open(ensemble_perf_log, "a") as f:
            f.write(
                f"Single model {i + 1} test loss: {test_loss}\tModel error: {model_error}\tAccuracy = {test_accuracy}\n"
            )
        if model_error >= 1 - (1 / model.num_classes):
            model.num_models = len(model.ensemble)
            print(
                f"Exiting AdaBoost training early bc model error is worse than random guessing. model_error = {model_error}"
            )
            break
        alpha = model.update_alphas(model_error, cuda=cuda)
        model.update_sample_weights(alpha, incorrect_train_idx)
        # Save model to ensemble
        snapshot = JetSubstructureNeqModel(config)
        if cuda:
            snapshot.cuda()
        snapshot.load_state_dict(model.model.state_dict())
        model.ensemble.append(snapshot)
        # Evaluate ensemble on validation data and save ensemble checkpoint
        ensemble_test_loss, ensemble_test_acc = evaluate_ensemble(
            model, datasets, config, cuda=cuda, log_dir=log_dir
        )
        ensemble_ckpt = {
            "model_dict": model.state_dict(),
            "test_loss": ensemble_test_loss,
            "test_acc": ensemble_test_acc,
            "alphas": model.alphas,
            "weights": model.weights,
        }
        torch.save(ensemble_ckpt, os.path.join(log_dir, "last_ensemble_ckpt.pth"))
        print(f"Saved AdaBoost model # {len(model.ensemble)}")


def compute_adaboost_model_error(model, datasets, config, cuda=False):
    """ "
    Evaluate the model on the training data and compute the weighted error
    epsilon by first getting the indices of the incorrectly classified samples
    and then computing a weighted average using the model's weights.
    """
    model.eval()
    train_loader = DataLoader(
        datasets["train"], batch_size=config["batch_size"], shuffle=False
    )
    with torch.no_grad():
        model.eval()
        incorrect_train_indices = []
        for batch_idx, (data, target) in enumerate(train_loader):
            if cuda:
                data, target = data.cuda(), target.cuda()
            output = model(data)
            pred = output.detach().max(1, keepdim=True)[1]
            target_label = torch.max(target.detach(), 1, keepdim=True)[1]
            curr_incorrect_idx = pred.ne(target_label).long()
            incorrect_train_indices += curr_incorrect_idx
    incorrect_train_indices = torch.Tensor(incorrect_train_indices)
    epsilon = model.weights @ incorrect_train_indices / torch.sum(model.weights)
    return epsilon, incorrect_train_indices