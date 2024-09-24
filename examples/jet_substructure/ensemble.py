import torch
import torch.nn as nn

from brevitas.core.quant import QuantType
from brevitas.nn import QuantIdentity, QuantHardTanh
from brevitas.core.scaling import ScalingImplType
from logicnets.quant import QuantBrevitasActivation
from logicnets.nn import (
    ScalarBiasScale, 
    ScalarScaleBias, 
    DenseMask2D, 
    RandomFixedSparsityMask2D,
    SparseLinearNeq,
    calculate_bits,
)
import math
from pyverilator import PyVerilator
from os.path import realpath
from functools import reduce

from models import JetSubstructureNeqModel

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

class AveragingJetNeqModel(nn.Module):
    """
    With the averaging ensemble method, we train N models and average their
    outputs in the end.
    """

    def __init__(self, model_config, num_models, quantize_avg=False):
        super(AveragingJetNeqModel, self).__init__()
        self.model_config = model_config
        self.num_models = num_models
        self.quantize_avg = quantize_avg
        self.same_input_scale = model_config["same_input_scale"]
        self.input_post_trans_sbs = model_config["input_post_trans_sbs"] # ScalarBiasScale
        self.same_output_scale = model_config["same_output_scale"]
        self.same_output_scale_sum = model_config["same_output_scale_sum"]
        self.shared_input_quant = model_config["shared_input_quant"]
        self.shared_input_layer = model_config["shared_input_layer"]
        self.shared_output_layer = model_config["shared_output_layer"]
        self.input_length = model_config["input_length"]
        self.output_length = model_config["output_length"]
        self.debug_verilog = False

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
        if quantize_avg: # For packing averaging into a LUT
            self.avg_quant = QuantBrevitasActivation(
                QuantIdentity(
                    bit_width=model_config["output_bitwidth"],
                    quant_type=QuantType.INT,
                )
            )
        if self.same_input_scale:
            # Share input quantizer among ensemble members to have same input scaling factor
            if self.input_post_trans_sbs:
                self.ensemble[0].module_list[0].input_post_transform = ScalarBiasScale(scale=True)
            for model in self.ensemble[1:]:
                # Set all ensemble member's input quantizer to be the same as the
                # first model's input quantizer
                if self.input_post_trans_ssb:
                    model.module_list[0].input_post_transform = ScalarScaleBias(scale=True)
                elif self.input_post_trans_sbs:
                    model.module_list[0].input_post_transform = ScalarBiasScale(scale=True)
                model.module_list[0].input_quant = self.ensemble[0].module_list[0].input_quant
                # print("AFTER: input quantizer for each ensemble member:")
                # for model in self.ensemble:
                #     print(f"\t{hex(id(model.module_list[0].input_quant))}")
        elif self.shared_input_quant:
            # Create a shared input quantizer that feeds into each ensemble
            # member, who each have their own input quantizer
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
            if self.shared_input_layer:
                mask = RandomFixedSparsityMask2D(
                    self.input_length,
                    self.input_length * num_models,
                    fan_in=1,
                    uniform_input_connectivity=True,
                )
                self.input_quant_layer = SparseLinearNeq(
                    self.input_length,
                    self.input_length * num_models,
                    input_quant=self.input_quant,
                    output_quant=None, 
                    apply_output_quant=False,
                    sparse_linear_kws={"mask": mask},
                )
                self.ensemble.insert(0, self.input_quant_layer)
        if self.same_output_scale:
            # FOR DEBUGGING: Print output quantizer for each ensemble member
            # print("BEFORE: Output quantizer for each ensemble member:")
            # for model in self.ensemble:
            #     print(f"\t{hex(id(model.module_list[-1].output_quant))}")
            # Set all ensemble member's output quantizer to be the same as the
            # first model's output quantizer
            for model in self.ensemble[1:]:
                model.module_list[-1].output_quant = self.ensemble[0].module_list[-1].output_quant
            # FOR DEBUGGING: Print output quantizer for each ensemble member
            # print("AFTER: Output quantizer for each ensemble member:")
            # for model in self.ensemble:
            #     print(f"\t{hex(id(model.module_list[-1].output_quant))}")
        elif self.same_output_scale_sum:
            # TODO: Double check this line
            self.ensemble[0].module_list[-1].output_pre_transform = ScalarBiasScale(
                scale=True, scale_init=1/num_models
            )
            for model in self.ensemble[1:]:
                model.module_list[-1].output_pre_transform = ScalarBiasScale(
                    scale=True, scale_init=1/num_models
                )
                model.module_list[-1].output_quant = self.ensemble[0].module_list[-1].output_quant
        elif self.shared_output_layer:
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
            self.output_quant_layer = SparseLinearNeq(
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
        if self.shared_input_quant and self.shared_input_layer:
            x = self.ensemble[0](x) # input_quant_layer
            if self.debug_verilog:
                print(x)
            if self.shared_output_layer:
                outputs = self.ensemble[1](x[:, 0 : self.input_length])
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
            if self.shared_input_quant:
                x = self.input_quant(x)
            outputs = torch.stack([model(x) for model in self.ensemble], dim=0)

        if self.shared_output_layer:
            if self.debug_verilog:
                print(outputs)
                # print(outputs[0])
                # print(outputs[0,:5])
                # print(list(map(lambda z: self.ensemble[1].module_list[-1].output_quant.get_bin_str(z, True), outputs[0,:5])))
                # print(list(map(lambda z: self.ensemble[2].module_list[-1].output_quant.get_bin_str(z, True), outputs[0,5:])))
            outputs = self.ensemble[-1](outputs)
            # Sum every out_length elements to get the final output
            outputs = outputs.view(-1, self.num_models, self.output_length)
            outputs = outputs.sum(dim=1)
            if self.debug_verilog:
                print(outputs)
                print(list(map(lambda z: self.ensemble[-1].output_quant.get_bin_str(z), outputs[0,:])))
        elif self.same_output_scale_sum:
            outputs = outputs.sum(dim=0)
        else:
            outputs = outputs.mean(dim=0)
        if self.quantize_avg: # For packing averaging into a LUT
            outputs = self.avg_quant(outputs)
        return outputs

    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        # Get integer output from the first layer
        input_quants = [model.module_list[0].input_quant for model in self.ensemble]
        output_quants = [model.module_list[-1].output_quant for model in self.ensemble]
        input_bitwidths = [int(model.module_list[0].input_quant.get_scale_factor_bits()[1]) for model in self.ensemble]
        output_bitwidths = [int(model.module_list[-1].output_quant.get_scale_factor_bits()[1]) for model in self.ensemble]
        total_input_bits = [model.module_list[0].in_features*input_bitwidth for input_bitwidth,model in zip(input_bitwidths,self.ensemble)]
        total_output_bits = [model.module_list[-1].out_features*output_bitwidth for output_bitwidth,model in zip(output_bitwidths,self.ensemble)]
        # assumes all models have same # of layers
        num_layers = len(self.ensemble[0].module_list)
        for input_quant in input_quants:
            input_quant.bin_output()
        self.ensemble[0].module_list[0].apply_input_quant = False
        y = torch.zeros(x.shape[0], self.ensemble[0].module_list[-1].out_features)
        xs = [input_quant(x) for input_quant in input_quants]
        # for x in xs:
        #     print("asdf")
        #     print(x.shape)
        # print(x, x.shape)
        self.dut.io.rst = 0
        self.dut.io.clk = 0
        for i in range(x.shape[0]):
            x_is = [x[i,:] for x in xs]
            # y_is = [model.pytorch_forward(x[i:i+1,:])[0] for x,model in zip(xs, self.ensemble)]
            xv_is = [list(map(lambda z: input_quant.get_bin_str(z), x_i)) for x_i,input_quant in zip(x_is,input_quants)]
            # ys_i = list(map(lambda z: output_quants[0].get_bin_str(z), y_i))
            # print("xv_i:", xv_i, "ys_i:",ys_i)
            #print("xv_is:", xv_is)
            xvc_i = reduce(lambda a,b: b+a, [reduce(lambda a,b: a+b, xv_i[::-1]) for xv_i in xv_is])
            #print("xvc_i:", xvc_i)
            #print(len(xvc_i))
            # ysc_i = reduce(lambda a,b: a+b, ys_i[::-1])
            self.dut["M0"] = int(xvc_i, 2)
            for j in range(len(self.ensemble[0].module_list) +  2):
                #print(self.dut.io.M5)
                res = self.dut[f"out"]
                result = f"{res:0{int(total_output_bits[0])}b}"
                self.dut.io.clk = 1
                self.dut.io.clk = 0
                #print("res, result: ", res, result)
            # expected = f"{int(ysc_i,2):0{int(total_output_bits)}b}"
            result = f"{res:0{int(total_output_bits[0])}b}"
            # print("expected:", expected, "result:", result)
            # assert(expected == result)
            res_split = [result[i:i+output_bitwidths[0]] for i in range(0, len(result), output_bitwidths[0])][::-1]
            yv_i = torch.Tensor(list(map(lambda z: int(z, 2), res_split)))
            y[i,:] = yv_i
            # Dump the I/O pairs
            if self.logfile is not None:
                with open(self.logfile, "a") as f:
                    f.write(f"{int(xvc_i,2):0{int(sum(total_input_bits))}b}, {result}\n")
        return y

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
        for i in range(x.shape[0]):
            x_i = x[i,:]
            y_i = self.pytorch_forward(x[i:i+1,:])[0]
            xv_i = list(map(lambda z: input_quant.get_bin_str(z), x_i))
            # xv_i = list(map(lambda z: to_twos_complement(z,6), x_i))
            ys_i = list(map(lambda z: to_twos_complement(z+2*len(self.ensemble[1:-1]),output_bitwidth+1)[1:], y_i))
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
            for j in range(num_layers + 4):
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

    
    # def verilog_forward(self, x):
    #     outputs = [model.verilog_forward(x) for model in self.ensemble]
    #     return sum(outputs)  # / self.num_models # Do division in pretransform

    def verilog_inference(
        self,
        verilog_dir,
        top_module_filename,
        logfile=None,
        add_registers: bool = False,
    ):
        self.verilog_dir = realpath(verilog_dir)
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
        for name,module in self.named_modules():
            if isinstance(module, SparseLinearNeq):
                print(name, module.apply_input_quant, module.apply_output_quant)
        self.is_verilog_inference = False


class AveragingJetLUTModel(AveragingJetNeqModel):
    pass


class BaseEnsembleClassifier(nn.Module):
    """
    Base class for ensembling classifiers. This class can be subclassed to implement
    different ensemble methods that build the ensemble sequentially, training
    one model at a time.
    """

    def __init__(
        self,
        model_class,
        model_config,
        num_models,
        quantize_avg=False,
        single_model_mode=False,
    ):
        super(BaseEnsembleClassifier, self).__init__()
        self.model_class = model_class
        self.model_config = model_config
        self.num_models = num_models
        self.quantize_avg = quantize_avg
        self.shared_input_layer = model_config["shared_input_layer"]
        self.single_model_mode = single_model_mode
        self.model = model_class(model_config)
        if single_model_mode:
            print("Init in single_model_mode mode!")
            self.ensemble = nn.ModuleList()
        else:
            print("Init in ensemble mode!")
            self.ensemble = nn.ModuleList(
                [model_class(model_config) for _ in range(num_models)]
            )
        if quantize_avg:
            self.avg_quant = QuantBrevitasActivation(
                QuantIdentity(
                    bit_width=model_config["output_bitwidth"],
                    quant_type=QuantType.INT,
                )
            )
        self.is_verilog_inference = False

        if self.shared_input_layer:
            # Create a shared input quantizer that feeds into each ensemble
            # member, who each have their own input quantizer
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
            self.input_quant_layer = SparseLinearNeq(
                self.input_length,
                self.input_length * num_models,
                input_quant=self.input_quant,
                output_quant=None,
                apply_output_quant=False,
                sparse_linear_kws={"mask": mask},
            )

    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)

    def pytorch_forward(self, x):
        if self.single_model_mode:
            outputs = self.model(x)
            return outputs
        if self.shared_input_layer:
            x = self.input_quant_layer(x)
            outputs = torch.stack(
                [
                    model(x[:, i * self.input_length : (i + 1) * self.input_length])
                    for i, model in enumerate(self.ensemble)
                ],
                dim=0,
            )
        else: 
            outputs = torch.stack([model(x) for model in self.ensemble], dim=0)
        outputs = outputs.mean(dim=0)
        if self.quantize_avg:
            outputs = self.avg_quant(outputs)
        return outputs

    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        # Get integer output from the first layer
        input_quants = [model.module_list[0].input_quant for model in self.ensemble]
        output_quants = [model.module_list[-1].output_quant for model in self.ensemble]
        input_bitwidths = [int(model.module_list[0].input_quant.get_scale_factor_bits()[1]) for model in self.ensemble]
        output_bitwidths = [int(model.module_list[-1].output_quant.get_scale_factor_bits()[1]) for model in self.ensemble]
        total_input_bits = [model.module_list[0].in_features*input_bitwidth for input_bitwidth,model in zip(input_bitwidths,self.ensemble)]
        total_output_bits = [model.module_list[-1].out_features*output_bitwidth for output_bitwidth,model in zip(output_bitwidths,self.ensemble)]
        # assumes all models have same # of layers
        num_layers = len(self.ensemble[0].module_list)
        for input_quant in input_quants:
            input_quant.bin_output()
        self.ensemble[0].module_list[0].apply_input_quant = False
        y = torch.zeros(x.shape[0], self.ensemble[0].module_list[-1].out_features)
        xs = [input_quant(x) for input_quant in input_quants]
        # for x in xs:
        #     print("asdf")
        #     print(x.shape)
        # print(x, x.shape)
        self.dut.io.rst = 0
        self.dut.io.clk = 0
        for i in range(x.shape[0]):
            x_is = [x[i,:] for x in xs]
            # y_is = [model.pytorch_forward(x[i:i+1,:])[0] for x,model in zip(xs, self.ensemble)]
            xv_is = [list(map(lambda z: input_quant.get_bin_str(z), x_i)) for x_i,input_quant in zip(x_is,input_quants)]
            # ys_i = list(map(lambda z: output_quants[0].get_bin_str(z), y_i))
            # print("xv_i:", xv_i, "ys_i:",ys_i)
            #print("xv_is:", xv_is)
            xvc_i = reduce(lambda a,b: b+a, [reduce(lambda a,b: a+b, xv_i[::-1]) for xv_i in xv_is])
            #print("xvc_i:", xvc_i)
            #print(len(xvc_i))
            # ysc_i = reduce(lambda a,b: a+b, ys_i[::-1])
            self.dut["M0"] = int(xvc_i, 2)
            for j in range(len(self.ensemble[0].module_list) +  2):
                #print(self.dut.io.M5)
                res = self.dut[f"out"]
                result = f"{res:0{int(total_output_bits[0])}b}"
                self.dut.io.clk = 1
                self.dut.io.clk = 0
                #print("res, result: ", res, result)
            # expected = f"{int(ysc_i,2):0{int(total_output_bits)}b}"
            result = f"{res:0{int(total_output_bits[0])}b}"
            # print("expected:", expected, "result:", result)
            # assert(expected == result)
            res_split = [result[i:i+output_bitwidths[0]] for i in range(0, len(result), output_bitwidths[0])][::-1]
            yv_i = torch.Tensor(list(map(lambda z: int(z, 2), res_split)))
            y[i,:] = yv_i
            # Dump the I/O pairs
            if self.logfile is not None:
                with open(self.logfile, "a") as f:
                    f.write(f"{int(xvc_i,2):0{int(sum(total_input_bits))}b}, {result}\n")
        return y
    
    # def verilog_forward(self, x):
    #     outputs = [model.verilog_forward(x) for model in self.ensemble]
    #     return sum(outputs)  # / self.num_models # Do division in pretransform

    def verilog_inference(
        self,
        verilog_dir,
        top_module_filename,
        logfile=None,
        add_registers: bool = False,
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


class BaggingJetNeqModel(BaseEnsembleClassifier):
    """
    Bagging, i.e., training data for each member model is sampled with
    replacement
    """

    def __init__(
        self, model_config, num_models, quantize_avg=False, single_model_mode=False
    ):
        self.model_class = JetSubstructureNeqModel
        super(BaggingJetNeqModel, self).__init__(
            self.model_class,
            model_config,
            num_models,
            quantize_avg,
            single_model_mode,
        )


class AdaBoostJetNeqModel(BaseEnsembleClassifier):
    """
    AdaBoost ensemble of JetSubstructureNeqModel models.
    """

    def __init__(
        self,
        model_config,
        num_models,
        num_train_samples,
        num_classes=5,
        quantize_avg=False,
        single_model_mode=False,
    ):
        self.model_class = JetSubstructureNeqModel
        super(AdaBoostJetNeqModel, self).__init__(
            self.model_class,
            model_config,
            num_models,
            quantize_avg,
            single_model_mode,
        )
        self.num_train_samples = num_train_samples
        self.num_classes = num_classes
        # Training sample weights
        self.weights = torch.ones(num_train_samples) / num_train_samples
        if single_model_mode:
            self.register_buffer("alphas", torch.tensor([])) # Accuracy measures for each model
        else:
            self.register_buffer("alphas", torch.zeros(num_models))
            
        # AdaBoost multi-class "one-hot" encoding
        adaboost_labels = (
            torch.ones(num_classes, num_classes) * -1 / (num_classes - 1)
        )
        adaboost_labels[torch.eye(num_classes) == 1] = 1  # Set diagonal to 1
        self.register_buffer("adaboost_labels", adaboost_labels)

    def update_alphas(self, epsilon, cuda=False):
        # Calculate alpha (accuracy measure) for current model and append to alphas
        alpha = torch.log((1.0 - epsilon) / epsilon) + torch.log(
            torch.tensor(self.num_classes - 1.0)
        )
        alpha = torch.tensor([alpha])
        if cuda:
            alpha = alpha.cuda()
        self.alphas = torch.cat([self.alphas, alpha])
        return alpha

    def update_sample_weights(self, alpha, incorrect_train_indices):
        # Reweight sample weights (only the positive weights are updated)
        # Based on sklearn AdaBoost SAAME implementation:
        # https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html
        # Make sure alpha is on cpu
        alpha = alpha.detach().cpu()
        self.weights = torch.exp(
            torch.log(self.weights)
            + alpha * incorrect_train_indices * (self.weights > 0)
        )
        # Normalize weights
        self.weights = self.weights / self.weights.sum()

    def pytorch_forward(self, x):
        if self.single_model_mode:
            outputs = self.model(x)
            return outputs
        if self.shared_input_quant:
            if self.shared_input_layer:
                x = self.input_quant_layer(x)
            else:
                    x = self.input_quant(x)
            outputs = sum(
                [
                    alpha
                    * self.adaboost_labels[
                        torch.argmax(
                            model(x[:, i * self.input_length : (i + 1) * self.input_length]), dim=1
                        )
                    ]
                    for i, (alpha, model) in enumerate(zip(self.alphas, self.ensemble))
                ]
            )
        else:
            outputs = sum(
                [
                    alpha * self.adaboost_labels[torch.argmax(model(x), dim=1)]
                    for alpha, model in zip(self.alphas, self.ensemble)
                ]
            )
        outputs = outputs / sum(self.alphas)
        return outputs
