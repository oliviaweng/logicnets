# CERN LHC High Granularity Calorimeter (HGCal) Autoencoder
We build a LogicNets version of the HGCal autoencoder, which requires 50ns inference latency.

## Download the dataset
Download the dataset. Right now we're only using the `nElinks_5` dataset:
* [HGCal dataset](https://cseweb.ucsd.edu/~oweng/hgcal_datset/)
<!-- * [Elegun dataset](https://emdhgcalae.nrp-nautilus.io/EleGun/low_pt_high_eta/data/nElinks_5/) -->

## How to train a model:
Update relevant  info in `./scripts/train.sh` such as 
* `DATA_DIR`: Directory storing your dataset
* `DATA_FILE`: `.npy` file that stores a compressed version of the dataset (the `--process-data` flag of `train.py` generates this file)
* `SAVE_DIR`: Directory for saving results
* `EXP_NAME`: Experiment name
* `CONFIG`: Path to LogicNet model config
  
in the following script:
```
CUDA_DEVICE=$1

DATA_DIR=./data/hgcal22data_signal_driven_ttbar_v11/nElinks_5/
DATA_FILE=./data/hgcal22data_signal_driven_ttbar_v11/hgcal22data_signal_driven_ttbar_v11_nELinks5.npy 
SAVE_DIR=./voting
EXP_NAME=hparam8_1916071045
CONFIG=./ensemble_configs/hparam8_1916071045.yml

CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python3 train.py \
    --data_dir $DATA_DIR \
    --data_file $DATA_FILE \
    --save_dir $SAVE_DIR \
    --experiment_name $EXP_NAME \
    --train \
    --gpu \
    --hparams_config $CONFIG
    # --process_data # Only need to run once
```
Run the script:
```
./scripts/train.sh CUDA_DEVICE_NUM # If you only have 1 gpu, set CUDA_DEVICE_NUM to 0
```

Your results will be stored in `./SAVE_DIR/EXP_NAME`.

## How to evaluate a model:
Update relevant  info in `./scripts/eval.sh` such as 
* `DATA_DIR`: Directory storing your dataset
* `DATA_FILE`: `.npy` file that stores a compressed version of the dataset (the `--process-data` flag of `train.py` generates this file)
* `SAVE_DIR`: Directory for saving results
* `EXP_NAME`: Experiment name
* `CONFIG`: Path to LogicNet model config
* `CKPT`: Path to LogicNet model checkpoint

in the following script:
```
CUDA_DEVICE=$1

DATA_DIR=./data/hgcal22data_signal_driven_ttbar_v11/nElinks_5/
DATA_FILE=./data/hgcal22data_signal_driven_ttbar_v11/hgcal22data_signal_driven_ttbar_v11_nELinks5.npy 
SAVE_DIR=./test
EXP_NAME=small_lr0.01_warm_restart_freq50_wd0.01_batch_size512
CONFIG=./grid_search_configs/avg_emd_small_configs/config1/small_lr0.01_warm_restart_freq50_wd0.01_batch_size512.yml
CKPT=./sml_avg_emd_hp_grid_search/small_lr0.01_warm_restart_freq50_wd0.01_batch_size512/best_loss.pth


CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python3 train.py \
    --data_dir $DATA_DIR \
    --data_file $DATA_FILE \
    --save_dir $SAVE_DIR \
    --experiment_name $EXP_NAME \
    --evaluate \
    --checkpoint $CKPT \
    --gpu \
    --hparams_config $CONFIG
```

Run the script:
```
./scripts/eval.sh CUDA_DEVICE_NUM # If you only have 1 gpu, set CUDA_DEVICE_NUM to 0
```

Your results will be stored in `./SAVE_DIR/EXP_NAME`.


## How to run an ensembling experiment

### Grid search method
1. In `./ensemble_configs`, create a `CONFIG.yml` listing out the hyperparameters you would like to keep and change.
2. Update `./scripts/gen_grid_search_configs.sh` with the `CONFIG.yml` you created and then run it.
3. To help parallelize the experiments, update `./scripts/create_run_subdirs.sh` with the number of subdirectories you would like and also the number of files you would like per subdirectory. Run script.
4. Update `./scripts/launch_ensemble_learning.sh` with the config folders you would like to run. Run script.