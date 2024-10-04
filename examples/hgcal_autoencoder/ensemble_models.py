# Copyright (c) 2020 Daniel Friedman
# Copyright (C) 2023, Advanced Micro Devices, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import copy
import torch
import torch.nn as nn
import numpy as np
import os
import math
from pyverilator import PyVerilator
from functools import reduce

from brevitas.core.quant import QuantType
from brevitas.nn import QuantHardTanh
from brevitas.core.scaling import ScalingImplType

from encoder import EncoderNeqModel
from decoder import Decoder
from logicnets.quant import QuantBrevitasActivation
from logicnets.nn import (
    RandomFixedSparsityMask2D,
    SparseLinearNeq_mask,
    ScalarBiasScale,
    calculate_bits,
)

from dataset import ARRANGE, ARRANGE_MASK

CALQ_MASK = torch.tensor(
    [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
    ]
)


def to_twos_complement(val, bits):
    # print(val)
    retval =bin(int(val) & 2**bits-1)[2:] 
    # print(retval)
    return retval.zfill(bits)
    # return bin(int(val) & 2**bits-1)[2:]

def from_twos_complement(binary_str):
    # Determine the length of the binary string
    n = len(binary_str)
    
    # Convert the binary string to an integer
    int_value = int(binary_str, 2)
    
    # Check if the most significant bit (MSB) is 1 (indicating a negative number)
    if binary_str[0] == '1':  # negative value in 2's complement
        int_value -= 2 ** n
    
    return int_value

def bits_to_ints(binary_str, bits):
    return [from_twos_complement(binary_str[i:i+bits]) for i in range(0,len(binary_str),bits)][::-1]

def hex_to_bin(hex_value):
    length = int(hex_value.split("'")[0])
    hex_value = hex_value.split("h")[1]
    # print(hex_value, length)
    binary_value = bin(int(hex_value, 16))[2:]
    return binary_value.zfill(length)

class VotingAutoencoderNeqModel(nn.Module): # TODO: Rename to Averaging
    """
    In the voting ensemble method, we train N models independently and average
    their outputs in the end. In our autoencoder use case, we train N encoders
    independently, average their outputs, and pass this to the decoder. This is
    done to maintain the low data rate the encoder's compressed output provides.
    """
    def __init__(
        self, 
        config, 
        input_length=64, 
        output_length=16,
        num_models=4,
        fixed_sparsity_mask=False,
        shared_input_layer=False,
        shared_input_bitwidth=6,
        shared_output_layer=False,
        shared_output_bitwidth=None,
        shared_output_fanin=1,
    ):
        super(VotingAutoencoderNeqModel, self).__init__()
        self.shape = (1, 8, 8)  # PyTorch defaults to (C, H, W)
        self.val_sum = None
        # TODO: Fix num neurons?
        self.num_neurons = [input_length] + config["hidden_layer"] + [output_length]
        self.num_models = num_models
        self.input_length = input_length
        self.output_length = output_length
        self.shared_input_layer = shared_input_layer
        self.shared_input_bitwidth = shared_input_bitwidth
        self.shared_output_layer = shared_output_layer
        self.shared_output_bitwidth = shared_output_bitwidth
        self.shared_output_fanin = shared_output_fanin

        if fixed_sparsity_mask:
            print("All models set with the same sparsity mask")
            self.encoder_ensemble = nn.ModuleList()
            encoder = EncoderNeqModel(
                config, input_length=input_length, output_length=output_length
            )
            self.encoder_ensemble.append(encoder)
            encoder_param = list(encoder.parameters())[1] # For testing only
            for _ in range(1, num_models):
                encoder_copy = EncoderNeqModel(
                    config, 
                    input_length=input_length, 
                    output_length=output_length,
                    shared_output_bitwidth=shared_output_bitwidth,
                )
                encoder_copy.load_state_dict(encoder.state_dict())
                encoder_copy.reset_parameters() # Reinitialize linear parameters
                encoder_param_copy = list(encoder_copy.parameters())[1]
                for i, (name, param) in enumerate(encoder_copy.named_parameters()):
                    if "mask" in name:
                        _, encoder_mask_param = list(encoder.named_parameters())[i]
                        assert torch.equal(param, encoder_mask_param)
                assert not torch.equal(encoder_param, encoder_param_copy)
                self.encoder_ensemble.append(encoder_copy)
        else:
            self.encoder_ensemble = nn.ModuleList([
                EncoderNeqModel(
                    config, 
                    input_length=input_length, 
                    output_length=output_length,
                    shared_output_bitwidth=shared_output_bitwidth,
                ) 
                for _ in range(num_models)
            ])
        if self.shared_input_layer:
            # Create a shared input quantizer that feeds into each ensemble
            # member, who each have their own input quantizer
            bn_in = nn.BatchNorm1d(self.input_length)
            self.input_quant = QuantBrevitasActivation(
                QuantHardTanh(
                    bit_width=self.shared_input_bitwidth,
                    max_val=1.0,
                    narrow_range=False,
                    quant_type=QuantType.INT,
                    scaling_impl_type=ScalingImplType.PARAMETER,
                ),
                pre_transforms=[nn.Flatten(), bn_in],
            )
            mask = RandomFixedSparsityMask2D(
                self.input_length,
                self.input_length * num_models,
                fan_in=1,
                uniform_input_connectivity=True,
            )
            self.input_quant_layer = SparseLinearNeq_mask(
                self.input_length,
                self.input_length * num_models,
                input_quant=self.input_quant,
                output_quant=None, 
                apply_output_quant=False,
                sparse_linear_kws={"mask": mask},
            )
            self.encoder_ensemble.insert(0, self.input_quant_layer)
        if self.shared_output_layer:
            feature_size = self.output_length * num_models
            bn = nn.BatchNorm1d(feature_size)
            output_quant = QuantBrevitasActivation(
                QuantHardTanh(
                    bit_width=config["output_bitwidth"], 
                    max_val=1.33, 
                    narrow_range=False, 
                    quant_type=QuantType.INT, 
                    scaling_impl_type=ScalingImplType.PARAMETER
                ), 
                pre_transforms=[bn], 
                post_transforms=[],
            )
            mask = RandomFixedSparsityMask2D(
                feature_size,
                feature_size,
                fan_in=self.shared_output_fanin,
                diagonal_mask=True,
            )
            self.output_quant_layer = SparseLinearNeq_mask(
                feature_size,
                feature_size,
                input_quant=None,
                output_quant=output_quant, 
                apply_input_quant=False,
                apply_output_quant=True,
                sparse_linear_kws={"mask": mask},
            )
            self.encoder_ensemble.append(self.output_quant_layer)
        self.decoder = Decoder(128)
        self.is_verilog_inference = False

    # Methods to measure model's physics performance
    def invert_arrange(self):
        """
        Invert the arrange mask
        """
        remap = []
        hashmap = {}  # cell : index mapping
        found_duplicate_charge = len(ARRANGE[ARRANGE_MASK == 1]) > len(
            torch.unique(ARRANGE[ARRANGE_MASK == 1])
        )
        for i in range(len(ARRANGE)):
            if ARRANGE_MASK[i] == 1:
                if found_duplicate_charge:
                    if CALQ_MASK[i] == 1:
                        hashmap[int(ARRANGE[i])] = i
                else:
                    hashmap[int(ARRANGE[i])] = i
        for i in range(len(torch.unique(ARRANGE))):
            remap.append(hashmap[i])
        return torch.tensor(remap)

    def map_to_calq(self, x):
        """
        Map the input/output of the autoencoder into CALQs orders
        """
        remap = self.invert_arrange()
        image_size = self.shape[0] * self.shape[1] * self.shape[2]
        reshaped_x = x.reshape(len(x), image_size)
        reshaped_x[:, ARRANGE_MASK == 0] = 0
        return reshaped_x[:, remap]

    def set_val_sum(self, val_sum):
        self.val_sum = val_sum

    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)
        
    def pytorch_forward(self, x):
        if self.shared_input_layer:
            x = self.encoder_ensemble[0](x) # input_quant_layer
            if self.shared_output_layer:
                outputs = self.encoder_ensemble[1](
                    x[:, 0 : self.input_length]
                )
                for i in range(1, self.num_models):
                    outputs = torch.cat(
                        (
                            outputs,
                            self.encoder_ensemble[i + 1](
                                x[:, i * self.input_length : (i + 1) * self.input_length]
                            ),
                        ),
                        dim=1,
                    )
            else:
                outputs = torch.stack(
                    [
                        self.encoder_ensemble[i + 1](
                            x[:, i * self.input_length : (i + 1) * self.input_length]
                        )
                        for i in range(0, self.num_models)
                    ],
                    dim=0,
                )
        else:
            outputs = [encoder(x) for encoder in self.encoder_ensemble]
        if self.shared_output_layer:
            outputs = self.encoder_ensemble[-1](outputs)
            # Sum every out_length elements to get the final output
            outputs = outputs.view(-1, self.num_models, self.output_length)
            outputs = outputs.sum(dim=1) / self.num_models # Need to divide for the decoder to work... or could include that in the decoder
        else:
            outputs = sum(outputs) / self.num_models
        if self.verilog_inference:
            return outputs * self.num_models
        return self.decoder(outputs)
    
    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        outputs = [encoder.verilog_forward(x) for encoder in self.encoder_ensemble]
        avg_outputs = sum(outputs) / self.num_models
        return self.decoder(avg_outputs)

    def verilog_forward(self, x):
        # for name,module in self.named_modules():
        #     if isinstance(module, SparseLinearNeq):
        #         print(name, module.apply_input_quant, module.apply_output_quant)
        # self.debug_verilog = True
        # Get integer output from the first layer
        input_quant = self.ensemble[0].input_quant
        output_quant = self.ensemble[-1].output_quant
        # print("input_quant_type", input_quant.get_quant_type())
        # print("input_quant_state_space", input_quant.get_bin_state_space())
        # print("output_quant_type", output_quant.get_quant_type())
        # print("output_quant_state_space", output_quant.get_bin_state_space())
        _, input_bitwidth = self.ensemble[0].input_quant.get_scale_factor_bits()
        output_bitwidth = calculate_bits(int(self.ensemble[-1].output_quant.get_scale_factor_bits()[1]), len(self.ensemble[1:-1]))
        output_quant_bitwidth = int(self.ensemble[-1].output_quant.get_scale_factor_bits()[1])
        input_bitwidth, output_bitwidth = int(input_bitwidth), int(output_bitwidth)
        total_input_bits = self.ensemble[0].in_features*input_bitwidth
        total_output_bits = self.ensemble[-1].out_features/len(self.ensemble[1:-1])*output_bitwidth
        num_layers = len(self.ensemble[1].module_list)
        input_quant.bin_output()
        self.ensemble[0].apply_input_quant = False
        y = torch.zeros(x.shape[0], int(self.ensemble[-1].out_features/len(self.ensemble[1:-1])))
        # import pdb; pdb.set_trace()
        x = input_quant(x)
        bin_offset = 2**(output_quant_bitwidth-1)*len(self.ensemble[1:-1])
        self.dut.io.rst = 0
        self.dut.io.clk = 0
        for i in range(x.shape[0]):
            x_i = x[i,:]
            y_i = self.pytorch_forward(x[i:i+1,:])[0]
            xv_i = list(map(lambda z: input_quant.get_bin_str(z), x_i))
            # import pdb; pdb.set_trace()
            # xv_i = list(map(lambda z: to_twos_complement(z,6), x_i))
            ys_i = list(map(lambda z: to_twos_complement(int(z)+bin_offset,output_bitwidth+1)[1:], y_i))
            xvc_i = reduce(lambda a,b: a+b, xv_i[::-1])
            ysc_i = reduce(lambda a,b: a+b, ys_i[::-1])
            # print("x_i =",x_i)
            # print("e0(xi) =", self.ensemble[0].lut_forward(x[i:i+1,:],debug=True))
            # print("xv_i =",xv_i)
            # print("xvc_i =",xvc_i,bits_to_ints(xvc_i,6))
            # print("ys_i bin_str =", list(map(lambda z: output_quant.get_bin_str(z), y_i)))
            # print("ys_i bin_str =", list(map(lambda z: to_twos_complement(int(output_quant.get_bin_str(z),2),4), y_i)))
            # print(y_i)
            # print(ys_i)
            # print(ysc_i)
            self.dut["M0"] = int(xvc_i, 2)
            for j in range(num_layers + 2 + 1 + math.ceil(math.log2(len(self.ensemble[1:-1])))):
                #print(self.dut.io.M5)
                res = self.dut[f"out"]
                result = f"{res:0{int(total_output_bits)}b}" # verilog output
                self.dut.io.clk = 1
                self.dut.io.clk = 0
                # print(res, result)
                # print(self.dut.internals)
                # print(self.dut.internals.logicnet_1_inst)
                # print(self.dut.internals.logicnet_2_inst)
                # print(self.dut.internals.logicnet_0_inst)
                m0 = hex_to_bin(str(self.dut.internals.logicnet_0_inst.M0w))
                input1 = hex_to_bin(str(self.dut.internals.logicnet_1_inst.M0w))
                input2 = hex_to_bin(str(self.dut.internals.logicnet_2_inst.M0w))
                output1 = hex_to_bin(str(self.dut.internals.M2_1))
                output2 = hex_to_bin(str(self.dut.internals.M2_2))
                # print("M0 =", m0, bits_to_ints(m0,6))
                # print("M0w_1 =", input1, bits_to_ints(input1,2))
                # print("M0w_2 =", input2, bits_to_ints(input2,2))
                # print("M2_1 =", output1, bits_to_ints(output1,4))
                # print("M2_2 =", output2, bits_to_ints(output2,4))
                # print(f"{self.dut['out_1']:0{int(total_output_bits)}b}",f"{self.dut[f'out_2']:0{int(total_output_bits)}b}")
            expected = f"{int(ysc_i,2):0{int(total_output_bits)}b}"
            result = f"{res:0{int(total_output_bits)}b}"
            # print(expected)
            # print(result)
            # import pdb; pdb.set_trace()
            assert(expected == result)
            res_split = [result[i:i+output_bitwidth] for i in range(0, len(result), output_bitwidth)][::-1]
            # print(result, res_split)
            yv_i = torch.Tensor(list(map(lambda z: int(z, 2)-bin_offset, res_split)))
            y[i,:] = yv_i
            # import pdb; pdb.set_trace()
            # Dump the I/O pairs
            if self.logfile is not None:
                with open(self.logfile, "a") as f:
                    f.write(f"{int(xvc_i,2):0{int(total_input_bits)}b}{int(ysc_i,2):0{int(total_output_bits)}b}\n")
        return self.decoder((y / self.num_models).to('cuda:0'))
    
    def verilog_inference(
        self,
        verilog_dir,
        top_module_filename,
        logfile=None,
        add_registers: bool = False,
    ):
        self.verilog_dir = os.path.realpath(verilog_dir)
        self.top_module_filename = top_module_filename
        self.dut = PyVerilator.build(f"{self.verilog_dir}/{self.top_module_filename}", verilog_path=[self.verilog_dir], build_dir=f"{self.verilog_dir}/verilator")

        # self.dut.start_vcd_trace('gtkwave.vcd')

        # start gtkwave to view the waveforms as they are made
        # self.dut.start_gtkwave()

        # add all the io and internal signals to gtkwave
        # self.dut.send_signals_to_gtkwave(self.dut.io)
        # self.dut.send_signals_to_gtkwave(self.dut.internals)


        self.is_verilog_inference = True
        self.logfile = logfile
        # if add_registers:
        #     self.latency = len(self.num_neurons)
    
    def pytorch_inference(self):
        self.is_verilog_inference = False


class VotingAutoencoderLUTModel(VotingAutoencoderNeqModel): # TODO: Rename to Averaging
    pass

# TODO: Make BaseEnsemble class?
class SnapshotAutoencoderNeqModel(nn.Module):
    """
    Snapshot ensemble of autoencoder models based on the method introduced in
    https://arxiv.org/pdf/1704.00109.pdf
    """
    def __init__(
        self, 
        config, 
        input_length=64, 
        output_length=16,
        num_models=4,
        single_model_mode=False,
    ):
        super(SnapshotAutoencoderNeqModel, self).__init__()
        self.shape = (1, 8, 8)  # PyTorch defaults to (C, H, W)
        self.val_sum = None
        # TODO: Fix num neurons to match ensemble size for verilog testing?
        self.num_neurons = [input_length] + config["hidden_layer"] + [output_length]
        self.num_models = num_models
        self.single_model_mode = single_model_mode

        # Snapshot ensemble builds the ensemble as it trains. We will save
        # snapshots of encoder to encoder_ensemble list to build the ensemble
        self.encoder = EncoderNeqModel(
            config, input_length=input_length, output_length=output_length
        )
        # Init model differently if training vs finetuning/evaluating
        if self.single_model_mode:
            print("Init in single_model_mode mode!")
            self.encoder_ensemble = nn.ModuleList()
        else:
            print("Init in ensemble mode!")
            # Build the ensemble (for evaluation or finetuning)
            self.encoder_ensemble = nn.ModuleList([
                EncoderNeqModel(
                    config, input_length=input_length, output_length=output_length
                ) 
                for _ in range(num_models)
            ])
        self.decoder = Decoder(128)
        self.is_verilog_inference = False

    # Methods to measure model's physics performance
    def invert_arrange(self):
        """
        Invert the arrange mask
        """
        remap = []
        hashmap = {}  # cell : index mapping
        found_duplicate_charge = len(ARRANGE[ARRANGE_MASK == 1]) > len(
            torch.unique(ARRANGE[ARRANGE_MASK == 1])
        )
        for i in range(len(ARRANGE)):
            if ARRANGE_MASK[i] == 1:
                if found_duplicate_charge:
                    if CALQ_MASK[i] == 1:
                        hashmap[int(ARRANGE[i])] = i
                else:
                    hashmap[int(ARRANGE[i])] = i
        for i in range(len(torch.unique(ARRANGE))):
            remap.append(hashmap[i])
        return torch.tensor(remap)
    
    def map_to_calq(self, x):
        """
        Map the input/output of the autoencoder into CALQs orders
        """
        remap = self.invert_arrange()
        image_size = self.shape[0] * self.shape[1] * self.shape[2]
        reshaped_x = x.reshape(len(x), image_size)
        reshaped_x[:, ARRANGE_MASK == 0] = 0
        return reshaped_x[:, remap]
    
    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)
    
    def pytorch_forward(self, x):
        if self.single_model_mode:
            return self.decoder(self.encoder(x))
        # Else evaluate on the full ensemble
        outputs = [encoder(x) for encoder in self.encoder_ensemble]
        avg_outputs = sum(outputs) / self.num_models
        return self.decoder(avg_outputs)
    
    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        outputs = [encoder.verilog_forward(x) for encoder in self.encoder_ensemble]
        avg_outputs = sum(outputs) / self.num_models
        return self.decoder(avg_outputs)
    
    def verilog_inference(self, verilog_dir, top_module_filename, logfile=None, add_registers: bool = False):
        pass


class FGEAutoencoderNeqModel(SnapshotAutoencoderNeqModel):
    """
    Fast Geometric Ensemble of autoencoder models based on the method introduced
    in Garipov et al., "Loss Surfaces, Mode Connectivity, and Fast Ensembling of
    DNNs", NeurIPS'18
    """

class BaggingAutoencoderNeqModel(SnapshotAutoencoderNeqModel):
    """
    Bagging, i.e., training data for each member model is sampled with
    replacement
    """


class AdaBoostAutoencoderNeqModel(nn.Module):
    """
    AdaBoost ensemble of autoencoder models based on AdaBoost.R2 from
    Drucker, “Improving Regressors using Boosting Techniques”, 1997.
    """
    def __init__(
        self, 
        config, 
        num_train_samples,
        input_length=64, 
        output_length=16,
        num_models=4,
        single_model_mode=False,
    ):
        super(AdaBoostAutoencoderNeqModel, self).__init__()
        self.shape = (1, 8, 8)  # PyTorch defaults to (C, H, W)
        self.val_sum = None
        # TODO: Fix num neurons to match ensemble size for verilog testing?
        self.num_neurons = (
            [input_length] + config["hidden_layer"] + [output_length]
        )
        self.num_models = num_models
        self.single_model_mode = single_model_mode
        self.num_train_samples = num_train_samples # N
        # Training sample weights
        self.weights = (
            torch.ones(self.num_train_samples) * 1 / self.num_train_samples
        )
        self.model_weights = []
        self.betas = []
        # Snapshot ensemble builds the ensemble as it trains. We will save
        # snapshots of encoder to encoder_ensemble list to build the ensemble
        self.encoder = EncoderNeqModel(
            config, input_length=input_length, output_length=output_length
        )
        # Init model differently if training vs finetuning/evaluating
        if self.single_model_mode:
            print("Init in single_model_mode mode!")
            self.encoder_ensemble = nn.ModuleList()
        else:
            print("Init in ensemble mode!")
            # Build the ensemble (for evaluation or finetuning)
            self.encoder_ensemble = nn.ModuleList([
                EncoderNeqModel(
                    config, 
                    input_length=input_length, 
                    output_length=output_length,
                ) 
                for _ in range(num_models)
            ])
        self.decoder = Decoder(128)
        self.is_verilog_inference = False

    def update_betas(self, model_err):
        # Calculate beta
        beta = model_err / (1 - model_err)
        self.betas.append(beta)
        return beta
    
    def update_sample_weights(self, beta, observation_errors):
        # Reweight sample weights
        z = torch.sum(self.weights * beta ** (1 - observation_errors))
        self.weights = self.weights * beta ** (1 - observation_errors) / z

    def update_model_weights(self):
        self.model_weights = torch.log(1 / torch.Tensor(self.betas))
        return self.model_weights

    # Methods to measure model's physics performance
    def invert_arrange(self):
        """
        Invert the arrange mask
        """
        remap = []
        hashmap = {}  # cell : index mapping
        found_duplicate_charge = len(ARRANGE[ARRANGE_MASK == 1]) > len(
            torch.unique(ARRANGE[ARRANGE_MASK == 1])
        )
        for i in range(len(ARRANGE)):
            if ARRANGE_MASK[i] == 1:
                if found_duplicate_charge:
                    if CALQ_MASK[i] == 1:
                        hashmap[int(ARRANGE[i])] = i
                else:
                    hashmap[int(ARRANGE[i])] = i
        for i in range(len(torch.unique(ARRANGE))):
            remap.append(hashmap[i])
        return torch.tensor(remap)
    
    def map_to_calq(self, x):
        """
        Map the input/output of the autoencoder into CALQs orders
        """
        remap = self.invert_arrange()
        image_size = self.shape[0] * self.shape[1] * self.shape[2]
        reshaped_x = x.reshape(len(x), image_size)
        reshaped_x[:, ARRANGE_MASK == 0] = 0
        return reshaped_x[:, remap]
    
    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)
    
    def pytorch_forward(self, x):
        if self.single_model_mode:
            return self.decoder(self.encoder(x))
        # Else evaluate on the full ensemble
        # For now use weighted average using model weights because unclear
        # how to use weighted median for encoded vectors...
        outputs = [
            encoder(x) * self.model_weights[i] 
            for i, encoder in enumerate(self.encoder_ensemble)
        ]
        avg_outputs = sum(outputs) / sum(self.model_weights)
        return self.decoder(avg_outputs)
    
    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        outputs = [encoder.verilog_forward(x) for encoder in self.encoder_ensemble]
        outputs = outputs * self.model_weights
        avg_outputs = sum(outputs) / sum(self.model_weights)
        return self.decoder(avg_outputs)
    
    def verilog_inference(self, verilog_dir, top_module_filename, logfile=None, add_registers: bool = False):
        pass

    
