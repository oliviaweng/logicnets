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
from tqdm import tqdm, trange

import numpy as np
from sklearn.metrics import roc_auc_score

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from dataset import JetSubstructureDataset
from models import JetSubstructureNeqModel
from ensemble import AveragingJetNeqModel

# TODO: Replace default configs with YAML files.
configs = {
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

# A dictionary, so we can set some defaults if necessary
model_config = {
    "hidden_layers": None,
    "input_bitwidth": None,
    "hidden_bitwidth": None,
    "output_bitwidth": None,
    "input_fanin": None,
    "hidden_fanin": None,
    "output_fanin": None,
    "ensemble_method": None,
    "ensemble_size": None,
}

training_config = {
    "weight_decay": None,
    "batch_size": None,
    "epochs": None,
    "learning_rate": None,
    "seed": None,
}

dataset_config = {
    "dataset_file": None,
    "dataset_config": None,
}

other_options = {
    "cuda": None,
    "log_dir": None,
    "checkpoint": None,
}

def train(model, datasets, config, cuda=False, log_dir="./jsc"):
    # Create data loaders for training and inference:
    train_loader = DataLoader(datasets["train"], batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(datasets["valid"], batch_size=config['batch_size'], shuffle=False)
    test_loader = DataLoader(datasets["test"], batch_size=config['batch_size'], shuffle=False)

    # Configure optimizer
    weight_decay = config["weight_decay"]
    decay_exclusions = ["bn", "bias", "learned_value"] # Make a list of parameters name fragments which will ignore weight decay TODO: make this list part of the train_cfg
    decay_params = []
    no_decay_params = []
    for pname, params in model.named_parameters():
        if params.requires_grad:
            if reduce(lambda a,b: a or b, map(lambda x: x in pname, decay_exclusions)): # check if the current label should be excluded from weight decay
                print("Disabling weight decay for %s" % (pname))
                no_decay_params.append(params)
            else:
                print("Enabling weight decay for %s" % (pname))
                decay_params.append(params)
        #else:
            #print("Ignoring %s" % (pname))
    params =    [{'params': decay_params, 'weight_decay': weight_decay},
                {'params': no_decay_params, 'weight_decay': 0.0}]
    optimizer = optim.AdamW(params, lr=config['learning_rate'], betas=(0.5, 0.999), weight_decay=weight_decay)

    # Configure scheduler
    steps = len(train_loader)
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=steps*100, T_mult=1)

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
            loss = criterion(output, torch.max(target, 1)[1])
            pred = output.detach().max(1, keepdim=True)[1]
            target_label = torch.max(target.detach(), 1, keepdim=True)[1]
            curCorrect = pred.eq(target_label).long().sum()
            curAcc = 100.0*curCorrect / len(data)
            correct += curCorrect
            accLoss += loss.detach()*len(data)
            loss.backward()
            optimizer.step()
            scheduler.step()
        accLoss /= len(train_loader.dataset)
        accuracy = 100.0*correct / len(train_loader.dataset)
        print(f"Epoch: {epoch}/{num_epochs}\tTrain Acc (%): {accuracy.detach().cpu().numpy():.2f}\tTrain Loss: {accLoss.detach().cpu().numpy():.3e}")
        writer.add_scalar('avg_train_loss', accLoss.detach().cpu().numpy(), (epoch+1)*steps)
        writer.add_scalar('avg_train_accuracy', accuracy.detach().cpu().numpy(), (epoch+1)*steps)
        val_accuracy, val_avg_roc_auc, val_loss = test(model, val_loader, cuda)
        test_accuracy, test_avg_roc_auc, test_loss = test(model, test_loader, cuda)
        modelSave = {   
            'model_dict': model.state_dict(),
            'optim_dict': optimizer.state_dict(),
            'val_accuracy': val_accuracy,
            'test_accuracy': test_accuracy,
            'val_avg_roc_auc': val_avg_roc_auc,
            'test_avg_roc_auc': test_avg_roc_auc,
            'epoch': epoch
        }
        torch.save(modelSave, os.path.join(log_dir, "checkpoint.pth"))
        if maxAcc < val_accuracy:
            torch.save(modelSave, os.path.join(log_dir, "best_accuracy.pth"))
            maxAcc = val_accuracy
        writer.add_scalar('val_accuracy', val_accuracy, (epoch+1)*steps)
        writer.add_scalar('val_loss', val_loss, (epoch+1)*steps)
        writer.add_scalar('test_accuracy', test_accuracy, (epoch+1)*steps)
        writer.add_scalar('test_loss', test_loss, (epoch+1)*steps)
        writer.add_scalar('val_avg_roc_auc', val_avg_roc_auc, (epoch+1)*steps)
        writer.add_scalar('test_avg_roc_auc', test_avg_roc_auc, (epoch+1)*steps)
        print(f"Epoch: {epoch}/{num_epochs}\tValid Acc (%): {val_accuracy:.2f}\tTest Acc: {test_accuracy:.2f}")

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
            loss = criterion(output, torch.max(target, 1)[1])
            accLoss += loss.detach() * len(data)
            prob = F.softmax(output, dim=1)
            pred = output.detach().max(1, keepdim=True)[1]
            target_label = torch.max(target.detach(), 1, keepdim=True)[1]
            curCorrect = pred.eq(target_label).long().sum()
            curAcc = 100.0*curCorrect / len(data)
            correct += curCorrect
            if batch_idx == 0:
                entire_prob = prob
                golden_ref = target_label
            else:
                entire_prob = torch.cat((entire_prob, prob), dim=0)
                golden_ref = torch.cat((golden_ref, target_label))
        accLoss /= len(dataset_loader.dataset)
        accuracy = 100*float(correct) / len(dataset_loader.dataset)
        avg_roc_auc = roc_auc_score(golden_ref.detach().cpu().numpy(), entire_prob.detach().cpu().numpy(), average='macro', multi_class='ovr')
        return accuracy, avg_roc_auc, accLoss


def main(args):
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    # Create experiment directory
    experiment_dir = os.path.join(args.save_dir, args.experiment_name)
    os.makedirs(experiment_dir, exist_ok=True)

    # Set random seeds
    random.seed(config['seed'])
    np.random.seed(config['seed'])
    torch.manual_seed(config['seed'])
    os.environ['PYTHONHASHSEED'] = str(config['seed'])
    if args.cuda:
        torch.cuda.manual_seed_all(config['seed'])
        torch.backends.cudnn.deterministic = True

    # Fetch the datasets
    dataset = {}
    dataset['train'] = JetSubstructureDataset(args.dataset_file, args.dataset_config, split="train")
    # This dataset is so small, we'll just use the training set as the validation set, otherwise we may have too few trainings examples to converge.
    dataset['valid'] = JetSubstructureDataset(args.dataset_file, args.dataset_config, split="train") 
    dataset['test'] = JetSubstructureDataset(args.dataset_file, args.dataset_config, split="test")

    # Instantiate model
    x, y = dataset['train'][0]
    config['input_length'] = len(x)
    config['output_length'] = len(y)

    # Ensemble settings
    quantize_avg = False
    if "quantize_avg" in config:
        quantize_avg = config["quantize_avg"]

    if "ensemble_method" in config:
        if config["ensemble_method"] == "averaging":
            print("Averaging ensemble method")
            model = AveragingJetNeqModel(config, config["ensemble_size"], quantize_avg=quantize_avg)
        else:
            raise ValueError(f"Unknown ensemble method: {config['ensemble_method']}")
    else: # Single model learning
        model = JetSubstructureNeqModel(config)
    if args.checkpoint is not None:
        print(f"Loading pre-trained checkpoint {args.checkpoint}")
        checkpoint = torch.load(args.checkpoint, map_location='cpu')
        model.load_state_dict(checkpoint['model_dict'])

    print(f"Model: {model.__class__.__name__}")

    # Train
    if args.train:
        # Log experiment hyperparameters
        hparams_log = os.path.join(experiment_dir,"hparams.yml")
        with open(hparams_log, "w") as f:
            yaml.dump(config, f)
        train(model, dataset, config, cuda=args.cuda, log_dir=experiment_dir)
    # Evaluate model
    evaluate_model = False
    if args.evaluate:
        if args.checkpoint:
            # Evaluate given checkpoint
            evaluate_model = True
            print(f"Evaluating model saved at: {args.checkpoint}")
        else:
            raise ValueError(
                "No checkpoint provided for evaluation. " \
                "Provide a path to checkpoint argument, " \
                "i.e., --checkpoint CHECKPOINT_PATH"
            ) 
    elif args.train:
        evaluate_model = True # Evaluate the model after training
        ckpt_path = os.path.join(experiment_dir, 'best_accuracy.pth')
        print(f"Evaluating best model saved at: {ckpt_path}")
        best_checkpoint = torch.load(ckpt_path)
        model.load_state_dict(best_checkpoint["model_dict"])
    
    if evaluate_model:
        print("Evaluating model")
        test_loader = DataLoader(dataset["test"], batch_size=config['batch_size'], shuffle=False)
        test_accuracy, test_avg_roc_auc, test_loss = test(model, test_loader, args.cuda)
        eval_tag = "_eval" if args.evaluate else ""
        os.makedirs(experiment_dir, exist_ok=True)
        test_results_log = os.path.join(
            experiment_dir, 
            args.experiment_name \
            + f"_loss={test_loss:.3f}" + eval_tag + "_accuracy.txt"
        )
        print(f"Test Accuracy: {test_accuracy:.2f}%")
        print(f"Test loss: {test_loss:.3f}")
        with open(test_results_log, "w") as f:
            f.write(str(test_accuracy))
            f.close()


if __name__ == "__main__":
    parser = ArgumentParser(description="LogicNets Jet Substructure Classification Example")
    parser.add_argument(
        '--cuda', action='store_true', default=False, help="Train on a GPU (default: %(default)s)"
    )
    parser.add_argument("--train", action="store_true", default=False)
    parser.add_argument("--evaluate", action="store_true", default=False)
    parser.add_argument(
        '--dataset-file', 
        type=str, 
        default='data/processed-pythia82-lhc13-all-pt1-50k-r1_h022_e0175_t220_nonu_truth.z',
        help="The file to use as the dataset input (default: %(default)s)"
    )
    parser.add_argument(
        '--dataset-config', 
        type=str, 
        default='config/yaml_IP_OP_config.yml',
        help="The file to use to configure the input dataset (default: %(default)s)"
    )
    parser.add_argument("--save_dir", type=str, default="./jet_tagger")
    parser.add_argument("--experiment_name", type=str, default="jsc")
    parser.add_argument(
        '--checkpoint', 
        type=str, 
        default=None,
        help="Retrain the model from a previous checkpoint (default: %(default)s)"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default=None, 
        help="Path to a YAML file containing the model configuration"
    )

    args = parser.parse_args()
    main(args)


