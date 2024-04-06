# CERN LHC High Granularity Calorimeter (HGCal) Autoencoder
We build a LogicNets version of the HGCal autoencoder, which requires 50ns inference latency.

## Download the dataset
Download the dataset. Right now we're only using the `nElinks_5` dataset:
* [HGCal dataset](https://emdhgcalae.nrp-nautilus.io/ttbar/data/HGCal22Data_signal_driven_ttbar_v11/nElinks_5/)
<!-- * [Elegun dataset](https://emdhgcalae.nrp-nautilus.io/EleGun/low_pt_high_eta/data/nElinks_5/) -->

## How to run an ensembling experiment

### Grid search method
1. In `./ensemble_configs`, create a `CONFIG.yml` listing out the (hyper)parameters you would like to keep and change.
2. Update `./scripts/gen_grid_search_configs.sh` with the `CONFIG.yml` you created and then run it.
3. To help parallelize the experiments, update `./scripts/create_run_subdirs.sh` with the number of subdirectories you would like and also the number of files you would like per subdirectory. Run script.
4. Update `./scripts/launch_ensemble_learning.sh` with the config folders you would like to run. Run script.