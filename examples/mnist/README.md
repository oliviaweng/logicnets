# LogicNets for MNIST Classification

This example shows the accuracy that is attainable using the LogicNets methodology on the MNIST hand-written character classification task.

## Prerequisites

* LogicNets
* numpy
* torchvision

## Installation

If you're using the docker image, all the above prerequisites will be already installed.
Otherwise, you can install the above dependencies with pip and/or conda.

## Download the Dataset

The MNIST dataset will download automatically when the training script is first run.
You only need to make sure the necessary directory has been created:

```bash
mkdir -p data
```

## Usage

To train the \"MNIST-S\", \"MNIST-M\" and \"MNIST-L\" networks,
run the following:

```bash
python train.py --arch <mnist-s|mnist-m|mnist-l> --log-dir ./<mnist_s|mnist_m|mnist_l>/
```

To then generate verilog from this trained model, run the following:

```bash
python neq2lut.py --arch <mnist-s|mnist-m|mnist-l> --checkpoint ./<mnist_s|mnist_m|mnist_l>/best_accuracy.pth --log-dir ./<mnist_s|mnist_m|mnist_l>/verilog/ --add-registers
```

## Results

Your results may vary slightly, depending on your system configuration.
The following results are attained when training on a CPU and synthesising with Vivado 2019.2:

| Network Architecture  | Test Accuracy (%) | LUTs  | Flip Flops    | Fmax (Mhz)    | Latency (Cycles)  |
| --------------------- | ----------------- | ----- | ------------- | ------------- | ----------------- |
| MNIST-S               |                   |       |               |               |                   |
| MNIST-M               |                   |       |               |               |                   |
| MNIST-L               |                   |       |               |               |                   |

## Citation

If you find this work useful for your research, please consider citing
our paper below:

```bibtex
@inproceedings{umuroglu2020logicnets,
  author = {Umuroglu, Yaman and Akhauri, Yash and Fraser, Nicholas J and Blott, Michaela},
  booktitle = {Proceedings of the International Conference on Field-Programmable Logic and Applications},
  title = {LogicNets: Co-Designed Neural Networks and Circuits for Extreme-Throughput Applications},
  year = {2020},
  pages = {291-297},
  publisher = {IEEE Computer Society},
  address = {Los Alamitos, CA, USA},
  month = {sep}
}
```

