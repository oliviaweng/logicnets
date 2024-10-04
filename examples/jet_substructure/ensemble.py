import torch
import torch.nn as nn

from functools import reduce
from os.path import realpath

from pyverilator import PyVerilator
from tqdm import tqdm
import math
from brevitas.core.quant import QuantType
from brevitas.nn import QuantHardTanh
from brevitas.core.scaling import ScalingImplType
from logicnets.quant import QuantBrevitasActivation
from logicnets.nn import (
    ScalarBiasScale, 
    RandomFixedSparsityMask2D,
    SparseLinearNeq_mask,
)

from models import JetSubstructureNeqModel

def to_twos_complement(val, bits):
    # print(val)
    retval =bin(int(val) & 2**bits-1)[2:] 
    # print(retval)
    return retval.zfill(bits)
    # return bin(int(val) & 2**bits-1)[2:]
def hex_to_bin(hex_value):
    length = int(hex_value.split("'")[0])
    hex_value = hex_value.split("h")[1]
    # print(hex_value, length)
    binary_value = bin(int(hex_value, 16))[2:]
    return binary_value.zfill(length)

class AveragingJetNeqModel(nn.Module):
    """
    With the averaging ensemble method, we train N models and average their
    outputs in the end.
    """
    def __init__(self, model_config, num_models):
        super(AveragingJetNeqModel, self).__init__()
        self.model_config = model_config
        self.num_models = num_models
        self.shared_input_layer = model_config["shared_input_layer"]
        self.shared_output_layer = model_config["shared_output_layer"]
        self.input_length = model_config["input_length"]
        self.output_length = model_config["output_length"]
        shared_output_bitwidth = None
        if self.shared_output_layer:
            shared_output_bitwidth = model_config["shared_output_bitwidth"]
        
        self.ensemble = nn.ModuleList(
            [
                JetSubstructureNeqModel(
                    model_config,
                    shared_output_bitwidth=shared_output_bitwidth,
                ) 
                for _ in range(num_models)
            ]
        )
        self.is_verilog_inference = False

        if self.shared_input_layer:
            bn_in = nn.BatchNorm1d(self.input_length)
            input_bias = ScalarBiasScale(scale=False, bias_init=-0.25)
            self.input_quant = QuantBrevitasActivation(
                QuantHardTanh(
                    bit_width=model_config["shared_input_bitwidth"],
                    max_val=1.0,
                    narrow_range=False,
                    quant_type=QuantType.INT,
                    scaling_impl_type=ScalingImplType.PARAMETER,
                ),
                pre_transforms=[bn_in, input_bias],
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
            self.ensemble.insert(0, self.input_quant_layer)
        if self.shared_output_layer:
            feature_size = self.output_length * num_models
            bn = nn.BatchNorm1d(feature_size)
            output_quant = QuantBrevitasActivation(
                QuantHardTanh(
                    bit_width=model_config["output_bitwidth"], 
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
                fan_in=model_config["shared_output_fanin"],
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
            self.ensemble.append(self.output_quant_layer)

    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)
    
    def pytorch_forward(self, x):
        if self.shared_input_layer:
            x = self.ensemble[0](x) # input_quant_layer
            if self.shared_output_layer:
                outputs = self.ensemble[1](
                    x[:, 0 : self.input_length]
                )
                for i in range(1, self.num_models):
                    outputs = torch.cat(
                        (
                            outputs,
                            self.ensemble[i + 1](
                                x[:, i * self.input_length : (i + 1) * self.input_length]
                            ),
                        ),
                        dim=1,
                    )
            else:
                outputs = torch.stack(
                    [
                        self.ensemble[i + 1](
                            x[:, i * self.input_length : (i + 1) * self.input_length]
                        )
                        for i in range(0, self.num_models)
                    ],
                    dim=0,
                )
        else:
            outputs = torch.stack([model(x) for model in self.ensemble], dim=0)
        outputs = outputs.cuda()
        if self.shared_output_layer:
            outputs = self.ensemble[-1](outputs)
            # Sum every out_length elements to get the final output
            outputs = outputs.view(-1, self.num_models, self.output_length)
            outputs = outputs.sum(dim=1) 
        else:
            outputs = outputs.mean(dim=0)
        return outputs
    
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
        x = input_quant(x)
        self.dut.io.rst = 0
        self.dut.io.clk = 0
        for i in tqdm(range(x.shape[0])):
            x_i = x[i,:]
            y_i = self.pytorch_forward(x[i:i+1,:].float())[0]
            xv_i = list(map(lambda z: input_quant.get_bin_str(z), x_i))
            # xv_i = list(map(lambda z: to_twos_complement(z,6), x_i))
            ys_i = list(map(lambda z: to_twos_complement(z+(2**(output_quant_bitwidth-1))*len(self.ensemble[1:-1]),output_bitwidth+1)[1:], y_i))
            # ys_i = list(map(lambda z: output_quant.get_bin_str(z), y_i))
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
            adder_latency = math.ceil(math.log2(len(self.ensemble[1:-1])))
            for j in range(num_layers + 2 + 1 + adder_latency):
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
                # m0 = hex_to_bin(str(self.dut.internals.logicnet_0_inst.M0w))
                # input1 = hex_to_bin(str(self.dut.internals.logicnet_1_inst.M0w))
                # input2 = hex_to_bin(str(self.dut.internals.logicnet_2_inst.M0w))
                # output1 = hex_to_bin(str(self.dut.internals.M2_1))
                # output2 = hex_to_bin(str(self.dut.internals.M2_2))
                # print("M0 =", m0, bits_to_ints(m0,6))
                # print("M0w_1 =", input1, bits_to_ints(input1,2))
                # print("M0w_2 =", input2, bits_to_ints(input2,2))
                # print("M2_1 =", output1, bits_to_ints(output1,4))
                # print("M2_2 =", output2, bits_to_ints(output2,4))
                # print(f"{self.dut['out_1']:0{int(total_output_bits)}b}",f"{self.dut[f'out_2']:0{int(total_output_bits)}b}")
            expected = f"{int(ysc_i,2):0{int(total_output_bits)}b}"
            result = f"{res:0{int(total_output_bits)}b}"
            breakpoint()
            # print(expected)
            # print(result)
            assert(expected == result)
            res_split = [result[i:i+output_bitwidth] for i in range(0, len(result), output_bitwidth)][::-1]
            # print(result, res_split)
            yv_i = torch.Tensor(list(map(lambda z: int(z, 2), res_split)))
            y[i,:] = yv_i
            # Dump the I/O pairs
            if self.logfile is not None:
                with open(self.logfile, "a") as f:
                    f.write(f"{int(xvc_i,2):0{int(total_input_bits)}b}{int(ysc_i,2):0{int(total_output_bits)}b}\n")
        return y
    
    def verilog_inference(
        self, 
        verilog_dir, 
        top_module_filename, 
        logfile: bool = False, 
        add_registers: bool = False
    ):
        self.verilog_dir = realpath(verilog_dir)
        self.top_module_filename = top_module_filename
        self.dut = PyVerilator.build(f"{self.verilog_dir}/{self.top_module_filename}", verilog_path=[self.verilog_dir], build_dir=f"{self.verilog_dir}/verilator")
        self.is_verilog_inference = True
        self.logfile = logfile
        # if add_registers:
        #     self.latency = len(self.num_neurons)

    def pytorch_inference(self):
        self.is_verilog_inference = False

class AveragingJetLUTModel(AveragingJetNeqModel):
    pass