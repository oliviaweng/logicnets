CUDA_DEVICE=$1

SAVE_DIR=./test
EXP_NAME=small_lr0.01_warm_restart_freq50_wd0.01_batch_size512
CONFIG=/home/ma11418/ensemble_new/logicnets/examples/mnist/averaging_wider_v2/w16_ensemble_size8_smaller_fanin/hparams.yml
CKPT=/home/ma11418/ensemble_new/logicnets/examples/mnist/averaging_wider_v2/w16_ensemble_size8_smaller_fanin/best_accuracy.pth

CUDA_VISIBLE_DEVICES=$CUDA_DEVICE python3 train.py \
    --save_dir $SAVE_DIR \
    --experiment_name $EXP_NAME \
    --evaluate \
    --checkpoint $CKPT \
    --gpu \
    --hparams_config $CONFIG