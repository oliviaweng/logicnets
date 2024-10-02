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

import heapdict
import numpy as np
from functools import partial, reduce

import torch
from torch import Tensor
import torch.nn as nn
from torch.nn import init
import torch.nn.functional as F
from torch.nn.parameter import Parameter
from tqdm import tqdm
import math
import copy

from .init import random_restrict_fanin
from .util import fetch_mask_indices, generate_permutation_matrix
from .verilog import    generate_lut_verilog, \
                        generate_neuron_connection_verilog, \
                        layer_connection_verilog, \
                        generate_logicnets_verilog, \
                        generate_register_verilog
from .bench import      generate_lut_bench, \
                        generate_lut_input_string, \
                        sort_to_bench

# TODO: Create a container module which performs this function.
# Generate all truth tables for NEQs for a given nn.Module()
def generate_truth_tables(model: nn.Module, verbose: bool = False) -> None:
    training = model.training
    model.eval()
    for name, module in model.named_modules():
        if type(module) == SparseLinearNeq:
            if verbose:
                print(f"Calculating truth tables for {name}")
            module.calculate_truth_tables(model)
            if verbose:
                print(f"Truth tables generated for {len(module.neuron_truth_tables)} neurons")
    model.training = training

# TODO: Create a container module which performs this function.
def lut_inference(model: nn.Module) -> None:
    for name,module in model.named_modules():
        if isinstance(module, SparseLinearNeq):
            print(name, module.apply_input_quant, module.apply_output_quant)
    for name, module in model.named_modules():
        if type(module) == SparseLinearNeq:
            if name != "ensemble.0" and name != "encoder_ensemble.0":
                module.apply_input_quant = False
            module.lut_inference()

# TODO: Create a container module which performs this function.
def neq_inference(model: nn.Module) -> None:
    for name, module in model.named_modules():
        if type(module) == SparseLinearNeq:
            module.neq_inference()

# Not sure if it's optimal to do this recursively, but it shouldn't matter unless we have some giant ensemble size I hope
def nested_case_generator(
    output_bits: int,
    depth: int,
    i: int = 0,
    sum: int = 0
):
    output = f"case(i{i})\n"
    for val in range(2**output_bits):
        output += f"2'b{val:0{output_bits}b}:\n"
        if i < depth-1:
            output += nested_case_generator(output_bits, depth, i+1, sum+val)
        else:
            output += f"outr = 2'b{int((sum+val)/depth):0{output_bits}b};\n"
    output += "endcase\n"
    return output

def averaging_module_verilog(
    output_bits: int,
    num_models: int,
    output_dir: str,
    module_name: str = "averaging",
    lut: bool = True
):
    output_string = f"""\
module {module_name} (input clk,
                  input [{output_bits-1}:0] {",".join([f"i{i}" for i in range(num_models)])},
                  output reg [{output_bits-1}:0] out);
"""
    if lut:
        output_string += f"""\
(*rom_style = "distributed"*) reg [{output_bits-1}:0] outr;
"""
    else:
        output_string += f"""\
reg [{output_bits-1}:0] outr;
"""

    output_string += f"""\
always @ (posedge clk) begin
    out <= outr;
end

always @ (*) begin
"""
    output_string += nested_case_generator(output_bits, num_models)
    output_string += f"""\
end
endmodule
"""
    with open(f"{output_dir}/{module_name}.v", "w") as f:
        f.write(output_string)

def averaging_module_adder_tree(
    output_bits: int,
    averaged_bits: int,
    num_models: int,
    output_dir: str,
    module_name: str = "averaging",
    lut: bool = True
):
    output_string = f"""\
module {module_name} (input clk,
                  input [{output_bits-1}:0] {",".join([f"i{i}" for i in range(num_models)])},
                  output reg [{averaged_bits-1}:0] out);
"""

    cycles = math.ceil(math.log2(num_models))
    # output_string += "\n".join([f"reg [{averaged_bits-1}:0] out_{i};" for i in range(cycles)])
    block_code = f"""
always @ (posedge clk) begin
"""

    previous_signals = [f"i{i}" for i in range(num_models)]
    intermediate_signals = []
    for stage in range(cycles):
        curr_signals = []
        wire_num = 0
        it = iter(previous_signals)
        for a,b in zip(it,it):
            this_signal = f"out_{stage}_{wire_num}"
            block_code += f"\t{this_signal} <= {a} + {b};\n"
            curr_signals.append(this_signal)
            wire_num += 1
        previous_signals = curr_signals
        intermediate_signals += curr_signals
        
    output_string += f"""
reg [{averaged_bits-1}:0] {",".join(intermediate_signals[:-1])};
"""
    block_code = block_code.replace(curr_signals.pop(), "out")
    output_string += block_code

    output_string += f"""
end

endmodule
"""
    with open(f"{output_dir}/{module_name}.v", "w") as f:
        print(output_string)
        f.write(output_string)


def averaging_module_verilog_shared_output(
    output_bits: int,
    averaged_bits: int,
    num_models: int,
    output_dir: str,
    module_name: str = "averaging",
    lut: bool = True
):
    output_string = f"""\
module {module_name} (input clk,
                  input [{output_bits-1}:0] {",".join([f"i{i}" for i in range(num_models)])},
                  output reg [{averaged_bits-1}:0] out);
"""

    cycles = math.ceil(math.log2(num_models))
    # output_string += "\n".join([f"reg [{averaged_bits-1}:0] out_{i};" for i in range(cycles)])
    first_out_reg = "out" if cycles == 1 else "out_0"
    output_string += f"""
reg [{averaged_bits-1}:0] {",".join([f"out_{i}" for i in range(cycles)])};
always @ (posedge clk) begin
    out_0 <= {"+".join([f"i{i}" for i in range(num_models)])};
"""
    output_string += "\n".join([f"\t{'out' if i == cycles-1 else f'out_{i}'} <= out_{i-1};" for i in range(1,cycles)])
    output_string += f"""
end

// always @(*) begin
//     out = out_{cycles-1};
// end

endmodule
"""
    output_string = f"""
module {module_name} (input clk,
                  input [{output_bits-1}:0] {",".join([f"i{i}" for i in range(num_models)])},
                  output reg [{averaged_bits-1}:0] out);
always @ (posedge clk) begin
    out <= {"+".join([f"i{i}" for i in range(num_models)])};
end
endmodule
    """
    with open(f"{output_dir}/{module_name}.v", "w") as f:
        print(output_string)
        f.write(output_string)
    
def ensemble_top_to_verilog(
    ensemble: nn.ModuleList,
    module_name: str,
    output_dir: str
):
    total_input_bits = int(sum([lnet.module_list[0].input_quant.get_scale_factor_bits()[1] *lnet.module_list[0].in_features for lnet in ensemble]))
    #total_output_bits = int(max([lnet.module_list[-1].output_quant.get_scale_factor_bits()[1]*lnet.module_list[-1].out_features for lnet in ensemble]) + math.ceil(math.log2(len(ensemble))))
    total_output_bits = int(max([lnet.module_list[-1].output_quant.get_scale_factor_bits()[1]*lnet.module_list[-1].out_features for lnet in ensemble]))
    output_feat_size = int(ensemble[0].module_list[-1].output_quant.get_scale_factor_bits()[1])
    layers = len(ensemble[0].module_list)
    averaging_module_verilog(
        output_bits = output_feat_size,
        num_models = len(ensemble),
        output_dir = output_dir,
        lut = True
    )
    #total_output_bits = 32
    file_contents = f"""\
module {module_name} (input [{total_input_bits-1}:0] M0, input clk, input rst, output reg [{total_output_bits-1}:0] out);
"""
    
    for i, lnet in enumerate(ensemble):
        i_scale_factor, i_bits = lnet.module_list[0].input_quant.get_scale_factor_bits()
        o_scale_factor, o_bits = lnet.module_list[-1].output_quant.get_scale_factor_bits()
        input_bits = int(i_bits) * lnet.module_list[0].in_features
        output_bits = int(o_bits) * lnet.module_list[-1].out_features
        file_contents += f"""\

//shortreal SFo_{i} = {o_scale_factor};
wire [{input_bits-1}:0] M0w_{i};
wire [{output_bits-1}:0] M2_{i};
assign M0w_{i} = M0[{32*(i+1)-1}:{32*i}];
{module_name}_{i} {module_name}_{i}_inst (.M0(M0w_{i}), .clk(clk), .rst(rst), .M{layers}(M2_{i}));
"""

#     file_contents += f"""\
#
# always @(posedge clk) begin
#     M5 <= {"+".join([f"M2_{i}" for i,_ in enumerate(ensemble)])};
# end
#     """
#     file_contents += f"""
# //wire [{total_output_bits-1}:0] M{layers}_reg;
# //always @(*) begin
# //    out = M{layers}_reg;
# //end
# """
    for num,i in enumerate(range(0, total_output_bits, output_feat_size)):
        hi = i+output_feat_size-1
        lo = i
        file_contents += f"""\
averaging averaging_{num}_inst (
    .clk(clk),
    {", ".join([f".i{j}(M2_{j}[{hi}:{lo}])" for j in range(len(ensemble))])}, 
    .out(M{layers}_reg[{hi}:{lo}])
);
"""

    file_contents += """\

endmodule
"""
    with open(f"{output_dir}/{module_name}.v", "w") as f:
        f.write(file_contents)

def calculate_bits(num_output_bits, num_of_ensembles):
    max_value_single_number = (2 ** num_output_bits) - 1
    max_sum = num_of_ensembles * max_value_single_number
    required_bits = math.ceil(math.log2(max_sum + 1))
    return required_bits

def ensemble_top_to_verilog_shared_input(
    ensemble: nn.ModuleList,
    module_name: str,
    output_dir: str
):
    total_input_bits = int(ensemble[0].in_features * ensemble[0].input_quant.get_scale_factor_bits()[1])
    output_feat_size = int(ensemble[-2].module_list[-1].output_quant.get_scale_factor_bits()[1])
    total_output_bits = int(ensemble[-2].module_list[-1].out_features * output_feat_size)
    layers = len(ensemble[1].module_list)
    num_ensembles = len(ensemble[1:-1])
    shared_output_features = int(ensemble[-1].out_features / num_ensembles)
    shared_output_feat_size = int(ensemble[-1].output_quant.get_scale_factor_bits()[1])
    shared_output_bits = shared_output_feat_size * shared_output_features
    module_feat_size = int(calculate_bits(ensemble[-1].output_quant.get_scale_factor_bits()[1], num_ensembles))
    total_module_bits = int(shared_output_features * module_feat_size)
    averaging_module_verilog_shared_output(
        output_bits = shared_output_feat_size,
        averaged_bits = module_feat_size,
        num_models = num_ensembles,
        output_dir = output_dir,
        lut = True
    )
    file_contents = f"""\
module {module_name} (input [{total_input_bits-1}:0] M0, input clk, input rst, output [{total_module_bits-1}:0] out);
"""
    
    print([type(lnet) for lnet in ensemble])
    for i, lnet in enumerate(ensemble[1:-1],1):
        i_scale_factor, i_bits = lnet.module_list[0].input_quant.get_scale_factor_bits()
        o_scale_factor, o_bits = lnet.module_list[-1].output_quant.get_scale_factor_bits()
        input_bits = int(i_bits) * lnet.module_list[0].in_features
        output_bits = int(o_bits) * lnet.module_list[-1].out_features
        file_contents += f"""\

//shortreal SFo_{i} = {o_scale_factor};
wire [{input_bits-1}:0] M0w_{i};
wire [{output_bits-1}:0] M2_{i};
// assign M0w_{i} = M0[{32*(i+1)-1}:{32*i}];
{module_name}_{i} {module_name}_{i}_inst (.M0(M0w_{i}), .clk(clk), .rst(rst), .M{layers}(M2_{i}));
"""

    file_contents += f"""
logicnet_0 logicnet_0_inst (.M0(M0), .clk(clk), .rst(rst), .M1({{{", ".join([f"M0w_{i}" for i,_ in reversed(list(enumerate(ensemble[1:-1],1)))])}}}));
"""

    file_contents += "\n".join([f"wire[{shared_output_bits-1}:0] out_{i};" for i,_ in enumerate(ensemble[1:-1],1)])

    file_contents += f"""
logicnet_{len(ensemble)-1} logicnet_{len(ensemble)-1}_inst (.M0({{{", ".join([f"M2_{i}" for i,_ in reversed(list(enumerate(ensemble[1:-1],1)))])}}}), .clk(clk), .rst(rst), .M1({{{", ".join([f"out_{i}" for i,_ in reversed(list(enumerate(ensemble[1:-1],1)))])}}}));
"""
#     file_contents += f"""\
#
# always @(posedge clk) begin
#     M5 <= {"+".join([f"M2_{i}" for i,_ in enumerate(ensemble)])};
# end
#     """
#     file_contents += f"""
# wire [{total_output_bits-1}:0] M{layers}_reg;
# always @(*) begin
#     out = M{layers}_reg;
# end
# """
    for num,(i,j) in enumerate(zip(range(0, shared_output_bits, shared_output_feat_size), range(0, total_module_bits, module_feat_size))):
        hi_out = i+shared_output_feat_size-1
        lo_out = i
        hi_module = j+module_feat_size-1
        lo_module = j
        file_contents += f"""\
averaging averaging_{num}_inst (
    .clk(clk),
    {", ".join([f".i{k}(out_{k+1}[{hi_out}:{lo_out}])" for k in range(len(ensemble[1:-1]))])}, 
    .out(out[{hi_module}:{lo_module}])
);
"""

    file_contents += """\

endmodule
"""
    with open(f"{output_dir}/{module_name}.v", "w") as f:
        f.write(file_contents)

def ensemble_to_verilog_module(
    ensemble: nn.ModuleList, 
    module_name: str, # "logicnet"
    output_dir: str, 
    add_registers: bool = True, 
    generate_bench: bool = True
):
    print([(m.input_quant.get_quant_type(), m.output_quant.get_quant_type()) for m in ensemble[1].module_list])
    for i, lnet in tqdm(enumerate(ensemble)):
        print(i)
        if isinstance(lnet, SparseLinearNeq):
            # lnet_copy = copy.deepcopy(lnet)
            lnet_copy = lnet
            print(ensemble[1].module_list[0].input_quant.get_quant_type(),ensemble[1].module_list[-1].output_quant.get_quant_type())
            if not lnet_copy.output_quant:
                lnet_copy.output_quant = ensemble[1].module_list[0].input_quant
            if not lnet_copy.input_quant:
                lnet_copy.input_quant = ensemble[1].module_list[-1].output_quant
            print(lnet_copy.input_quant.get_quant_type(), lnet_copy.output_quant.get_quant_type())
            module_list_to_verilog_module(
                nn.ModuleList([lnet_copy]), 
                module_name, 
                output_dir, 
                ensemble_member_idx=i,
                generate_bench=generate_bench,
                add_registers=add_registers,
            )
            continue
        module_list_to_verilog_module(
            lnet.module_list, 
            module_name, 
            output_dir, 
            ensemble_member_idx=i,
            generate_bench=generate_bench,
            add_registers=add_registers,
        )
    ensemble_top_to_verilog_shared_input(
        ensemble=ensemble,
        module_name=module_name,
        output_dir=output_dir
    )
    ensemble[0].output_quant = None
    ensemble[-1].input_quant = None
    print(f"Top level entity stored at: {output_dir}/{module_name}.v ...")

# TODO: Should this go in with the other verilog functions?
# TODO: Support non-linear topologies
def module_list_to_verilog_module(
    module_list: nn.ModuleList, 
    module_name: str, 
    output_directory: str, 
    ensemble_member_idx: int = 0,
    add_registers: bool = True, 
    generate_bench: bool = True
):
    input_bitwidth = None
    output_bitwidth = None
    module_contents = ""
    for i in range(len(module_list)):
        m = module_list[i]
        if type(m) == SparseLinearNeq:
            module_prefix = f"ens{ensemble_member_idx}_layer{i}"
            module_input_bits, module_output_bits = m.gen_layer_verilog(module_prefix, output_directory, generate_bench=generate_bench)
            if i == 0:
                input_bitwidth = module_input_bits
            if i == len(module_list)-1:
                output_bitwidth = module_output_bits
            module_contents += layer_connection_verilog( module_prefix,
                                                        input_string=f"M{i}",
                                                        input_bits=module_input_bits,
                                                        output_string=f"M{i+1}",
                                                        output_bits=module_output_bits,
                                                        output_wire=i!=len(module_list)-1,
                                                        register=add_registers)
        else:
            raise Exception(f"Expect type(module) == SparseLinearNeq, {type(m)} found")
    module_list_verilog = generate_logicnets_verilog(
        module_name=f"{module_name}_{ensemble_member_idx}",
        input_name="M0",
        input_bits=input_bitwidth,
        output_name=f"M{len(module_list)}",
        output_bits=output_bitwidth,
        module_contents=module_contents
    )
    reg_verilog = generate_register_verilog()
    with open(f"{output_directory}/myreg.v", "w") as f:
        f.write(reg_verilog)
    with open(f"{output_directory}/{module_name}_{ensemble_member_idx}.v", "w") as f:
        f.write(module_list_verilog)

class SparseLinear(nn.Linear):
    def __init__(self, in_features: int, out_features: int, mask: nn.Module, bias: bool = True) -> None:
        super(SparseLinear, self).__init__(in_features=in_features, out_features=out_features, bias=bias)
        self.mask = mask

    def forward(self, input: Tensor) -> Tensor:
        return F.linear(input, self.weight*self.mask(), self.bias)

# TODO: Perhaps make this two classes, separating the LUT and NEQ code.
class SparseLinearNeq(nn.Module):
    def __init__(
        self, 
        in_features: int, 
        out_features: int, 
        input_quant, 
        output_quant, 
        sparse_linear_kws={}, 
        apply_input_quant=True, 
        apply_output_quant=True,
        output_pre_transform=None,
        input_post_transform=None,

    ) -> None:
        super(SparseLinearNeq, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.input_quant = input_quant
        self.fc = SparseLinear(in_features, out_features, **sparse_linear_kws)
        self.output_quant = output_quant
        self.is_lut_inference = False
        self.neuron_truth_tables = None
        self.apply_input_quant = apply_input_quant
        self.apply_output_quant = apply_output_quant
        self.output_pre_transform = output_pre_transform
        self.input_post_transform = input_post_transform

    def lut_cost(self):
        """
        Approximate how many 6:1 LUTs are needed to implement this layer using 
        LUTCost() as defined in LogicNets paper FPL'20:
            LUTCost(X, Y) = (Y / 3) * (2^(X - 4) - (-1)^X)
        where:
        * X: input fanin bits
        * Y: output bits 
        LUTCost() estimates how many LUTs are needed to implement 1 neuron, so 
        we then multiply LUTCost() by the number of neurons to get the total 
        number of LUTs needed.
        NOTE: This function (over)estimates how many 6:1 LUTs are needed to implement
        this layer b/c it assumes every neuron is connected to the next layer 
        since we do not have the next layer's sparsity information.
        """
        # Compute LUTCost of 1 neuron
        _, input_bitwidth = self.input_quant.get_scale_factor_bits()
        _, output_bitwidth = self.output_quant.get_scale_factor_bits()
        input_bitwidth, output_bitwidth = int(input_bitwidth), int(output_bitwidth)
        x = input_bitwidth * self.fc.mask.fan_in # neuron input fanin
        y = output_bitwidth 
        neuron_lut_cost = (y / 3) * ((2 ** (x - 4)) - ((-1) ** x))
        # Compute total LUTCost
        return self.out_features * neuron_lut_cost

    # TODO: Move the verilog string templates to elsewhere
    # TODO: Move this to another class
    # TODO: Update this code to support custom bitwidths per input/output
    def gen_layer_verilog(self, module_prefix, directory, generate_bench: bool = True):
        debug = False 
        if module_prefix == "ens0_layer0":
            debug = True
        _, input_bitwidth = self.input_quant.get_scale_factor_bits()
        _, output_bitwidth = self.output_quant.get_scale_factor_bits()
        input_bitwidth, output_bitwidth = int(input_bitwidth), int(output_bitwidth)
        total_input_bits = self.in_features*input_bitwidth
        total_output_bits = self.out_features*output_bitwidth
        layer_contents = f"module {module_prefix} (input [{total_input_bits-1}:0] M0, output [{total_output_bits-1}:0] M1);\n\n"
        output_offset = 0
        for index in range(self.out_features):
            module_name = f"{module_prefix}_N{index}"
            indices, _, _, _ = self.neuron_truth_tables[index]
            neuron_verilog = self.gen_neuron_verilog(index, module_name) # Generate the contents of the neuron verilog
            with open(f"{directory}/{module_name}.v", "w") as f:
                f.write(neuron_verilog)
            if generate_bench:
                neuron_bench = self.gen_neuron_bench(index, module_name) # Generate the contents of the neuron verilog
                with open(f"{directory}/{module_name}.bench", "w") as f:
                    f.write(neuron_bench)
            connection_string = generate_neuron_connection_verilog(indices, input_bitwidth) # Generate the string which connects the synapses to this neuron
            wire_name = f"{module_name}_wire"
            connection_line = f"wire [{len(indices)*input_bitwidth-1}:0] {wire_name} = {{{connection_string}}};\n"
            inst_line = f"{module_name} {module_name}_inst (.M0({wire_name}), .M1(M1[{output_offset+output_bitwidth-1}:{output_offset}]));\n\n"
            layer_contents += connection_line + inst_line
            output_offset += output_bitwidth
        layer_contents += "endmodule"
        with open(f"{directory}/{module_prefix}.v", "w") as f:
            f.write(layer_contents)
        return total_input_bits, total_output_bits

    # TODO: Move the verilog string templates to elsewhere
    # TODO: Move this to another class
    def gen_neuron_verilog(self, index, module_name):
        indices, input_perm_matrix, float_output_states, bin_output_states = self.neuron_truth_tables[index]
        _, input_bitwidth = self.input_quant.get_scale_factor_bits()
        _, output_bitwidth = self.output_quant.get_scale_factor_bits()
        cat_input_bitwidth = len(indices)*input_bitwidth
        lut_string = ""
        num_entries = input_perm_matrix.shape[0]
        for i in range(num_entries):
            entry_str = ""
            for idx in range(len(indices)):
                val = input_perm_matrix[i,idx]
                entry_str += self.input_quant.get_bin_str(val)
            res_str = self.output_quant.get_bin_str(bin_output_states[i])
            lut_string += f"\t\t\t{int(cat_input_bitwidth)}'b{entry_str}: M1r = {int(output_bitwidth)}'b{res_str};\n"
        return generate_lut_verilog(module_name, int(cat_input_bitwidth), int(output_bitwidth), lut_string)

    # TODO: Move the string templates to bench.py
    # TODO: Move this to another class
    def gen_neuron_bench(self, index, module_name):
        indices, input_perm_matrix, float_output_states, bin_output_states = self.neuron_truth_tables[index]
        _, input_bitwidth = self.input_quant.get_scale_factor_bits()
        _, output_bitwidth = self.output_quant.get_scale_factor_bits()
        cat_input_bitwidth = len(indices)*input_bitwidth
        lut_string = ""
        num_entries = input_perm_matrix.shape[0]
        # Sort the input_perm_matrix to match the bench format
        input_state_space_bin_str = list(map(lambda y: list(map(lambda z: self.input_quant.get_bin_str(z), y)), input_perm_matrix))
        sorted_bin_output_states = sort_to_bench(input_state_space_bin_str, bin_output_states)
        # Generate the LUT for each output
        for i in range(int(output_bitwidth)):
            lut_string += f"M1[{i}]       = LUT 0x"
            output_bin_str = reduce(lambda b,c: b+c, map(lambda a: self.output_quant.get_bin_str(a)[int(output_bitwidth)-1-i], sorted_bin_output_states))
            lut_hex_string = f"{int(output_bin_str,2):0{int(num_entries/4)}x} "
            lut_string += lut_hex_string
            lut_string += generate_lut_input_string(int(cat_input_bitwidth))
        return generate_lut_bench(int(cat_input_bitwidth), int(output_bitwidth), lut_string)

    def lut_inference(self):
        self.is_lut_inference = True
        if self.input_quant:
            self.input_quant.bin_output()
        if self.output_quant:
            self.output_quant.bin_output()

    def neq_inference(self):
        self.is_lut_inference = False
        if self.input_quant:
            self.input_quant.float_output()
        if self.output_quant:
            self.output_quant.float_output()

    # TODO: This function might be a useful utility outside of this class..
    def table_lookup(self, connected_input: Tensor, input_perm_matrix: Tensor, bin_output_states: Tensor) -> Tensor:
        fan_in_size = connected_input.shape[1]
        ci_bcast = connected_input.unsqueeze(2) # Reshape to B x Fan-in x 1
        pm_bcast = input_perm_matrix.t().unsqueeze(0) # Reshape to 1 x Fan-in x InputStates
        eq = (ci_bcast == pm_bcast).sum(dim=1) == fan_in_size # Create a boolean matrix which matches input vectors to possible input states
        matches = eq.sum(dim=1) # Count the number of perfect matches per input vector
        if not (matches == torch.ones_like(matches,dtype=matches.dtype)).all():
            raise Exception(f"One or more vectors in the input is not in the possible input state space")
        indices = torch.argmax(eq.type(torch.int64),dim=1)
        return bin_output_states[indices]

    def lut_forward(self, x: Tensor, debug=False) -> Tensor:

        if self.apply_input_quant:
            x = self.input_quant(x) # Use this to fetch the bin output of the input, if the input isn't already in binary format
        y = torch.zeros((x.shape[0],self.out_features))
        # Perform table lookup for each neuron output
        for i in range(self.out_features):
            indices, input_perm_matrix, float_output_states, bin_output_states = self.neuron_truth_tables[i]
            connected_input = x[:,indices]
            # print(connected_input[0,:])
            # print(x.shape, connected_input.shape, indices, input_perm_matrix, bin_output_states)
            # print(self.neuron_truth_tables[i].shape)
            y[:,i] = self.table_lookup(connected_input, input_perm_matrix, bin_output_states)
            if debug:
                print("i:",i)
                print("input_perm_matrix:",input_perm_matrix)
                print("bin_output_states:",bin_output_states)
                if self.output_quant:
                    print("bin_output_states:",list(map(lambda z: self.output_quant.get_bin_str(z), bin_output_states)))
                print("connected_input:",connected_input)
                if self.input_quant:
                    print("connected_input:",self.input_quant.get_bin_str(connected_input[0][0]))
                print("y:",y[:,i])
        return y

    def forward(self, x: Tensor, debug=False) -> Tensor:
        if self.is_lut_inference:
            x = self.lut_forward(x, debug)
            # print(x.shape)
        else:
            if self.apply_input_quant:
                x = self.input_quant(x)
            if self.input_post_transform:
                x = self.input_post_transform(x)
            x = self.fc(x)
            if self.output_pre_transform:
                x = self.output_pre_transform(x)
            if self.apply_output_quant:
                x = self.output_quant(x)
        return x

    # Consider using masked_select instead of fetching the indices
    def calculate_truth_tables(self, model: nn.Module):
        # print("in_features", self.in_features, "out_features", self.out_features)
        with torch.no_grad():
            mask = self.fc.mask()
            # Precalculate all of the input value permutations
            input_state_space = list() # TODO: is a list the right data-structure here?
            bin_state_space = list()
            if self.input_quant is None:
                input_quants = [model.ensemble[i].module_list[-1].output_quant for i in range(len(model.ensemble)) if not isinstance(model.ensemble[i], SparseLinearNeq)]
                in_features = [model.ensemble[i].module_list[-1].out_features for i in range(len(model.ensemble)) if not isinstance(model.ensemble[i], SparseLinearNeq)]
                assert(in_features.count(in_features[0]) == len(in_features))
                in_features = in_features[0]

            for m in range(self.in_features):
                if self.input_quant is not None:
                    neuron_state_space = self.input_quant.get_state_space() # TODO: this call should include the index of the element of interest
                    bin_space = self.input_quant.get_bin_state_space() # TODO: this call should include the index of the element of interest
                else:
                    neuron_state_space = input_quants[m//in_features].get_state_space() # TODO: this call should include the index of the element of interest
                    bin_space = input_quants[m//in_features].get_bin_state_space() # TODO: this call should include the index of the element of interest
                input_state_space.append(neuron_state_space)
                bin_state_space.append(bin_space)
            
            print(input_state_space[0].shape, len(input_state_space))

            neuron_truth_tables = list()
            for n in range(self.out_features):
                # Determine the fan-in as number of synapse connections
                input_mask = mask[n,:]
                fan_in = torch.sum(input_mask)
                indices = fetch_mask_indices(input_mask)
                # Retrieve the possible state space of the current neuron
                connected_state_space = [input_state_space[i] for i in indices]
                bin_connected_state_space = [bin_state_space[i] for i in indices]
                # Generate a matrix containing all possible input states
                input_permutation_matrix = generate_permutation_matrix(connected_state_space)
                bin_input_permutation_matrix = generate_permutation_matrix(bin_connected_state_space)
                num_permutations = input_permutation_matrix.shape[0]
                padded_perm_matrix = torch.zeros((num_permutations, self.in_features))
                padded_perm_matrix[:,indices] = input_permutation_matrix

                # print(input_permutation_matrix.shape)
                # print(self.forward(padded_perm_matrix)[:,n])
                
                output_quants = [self.output_quant]
                shared_input = False
                if self.output_quant == None:
                    # print(type(model))
                    # print([type(model.ensemble[i]) for i in range(len(model.ensemble))])
                    output_quants = [model.ensemble[i].module_list[0].input_quant for i in range(len(model.ensemble)) if not isinstance(model.ensemble[i], SparseLinearNeq)]
                    shared_input = True
                
                # print(len(output_quants))

                # TODO: Update this block to just run inference on the fc layer, once BN has been moved to output_quant
                apply_input_quant, apply_output_quant = self.apply_input_quant, self.apply_output_quant
                self.apply_input_quant, self.apply_output_quant = False, False
                is_bin_outputs = [output_quant.is_bin_output for output_quant in output_quants]
                for output_quant in output_quants:
                    output_quant.float_output()
                # print(padded_perm_matrix.shape)
                # print("forwarded", self.forward(padded_perm_matrix).shape)
                # print(output_quant.get_scale_factor_bits())
                input_feats = self.in_features
                ranges = [(input_feats*i,input_feats*(i+1)) for i in range(len(output_quants))]
                # print(ranges)
                if len(output_quants) == 1:
                    output_states = self.output_quant(self.forward(padded_perm_matrix))[:,n] # Calculate float for the current input
                else:
                    # print(ranges)
                    # print([self.forward(padded_perm_matrix)[:,a:b].shape for a,b in ranges])
                    input_feats = self.in_features
                    output_states = torch.cat([output_quant(self.forward(padded_perm_matrix)[:,input_feats*i:input_feats*(i+1)]) for i,output_quant in enumerate(output_quants)], dim=1)[:,n]
                for output_quant in output_quants:            
                    output_quant.bin_output()
                if len(output_quants) == 1:
                    bin_output_states = self.output_quant(self.forward(padded_perm_matrix))[:,n] # Calculate bin for the current input
                else:
                    input_feats = self.in_features
                    bin_output_states = torch.cat([output_quant(self.forward(padded_perm_matrix)[:,input_feats*i:input_feats*(i+1)]) for i,output_quant in enumerate(output_quants)], dim=1)[:,n]
                for output_quant, is_bin_output in zip(output_quants, is_bin_outputs):
                    output_quant.is_bin_output = is_bin_output
                self.apply_input_quant, self.apply_output_quant = apply_input_quant, apply_output_quant

                # Append the connectivity, input permutations and output permutations to the neuron truth tables 
                neuron_truth_tables.append((indices, bin_input_permutation_matrix, output_states, bin_output_states)) # Change this to be the binary output states
        self.neuron_truth_tables = neuron_truth_tables

class DenseMask2D(nn.Module):
    def __init__(self, in_features: int, out_features: int) -> None:
        super(DenseMask2D, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.mask = Parameter(torch.Tensor(out_features, in_features), requires_grad=False)
        self.reset_parameters()

    def reset_parameters(self) -> None:
        init.constant_(self.mask, 1.0)

    def forward(self):
        return self.mask

class RandomFixedSparsityMask2D(nn.Module):
    def __init__(
        self, 
        in_features: int, 
        out_features: int, 
        fan_in: int, 
        uniform_input_connectivity : bool = False,
        diagonal_mask: bool = False,
    ) -> None:
        super(RandomFixedSparsityMask2D, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.fan_in = fan_in
        self.mask = Parameter(torch.Tensor(out_features, in_features), requires_grad=False)
        self.uniform_input_connectivity = uniform_input_connectivity
        self.diagonal_mask = diagonal_mask
        self.reset_parameters()

    def reset_parameters(self) -> None:
        init.constant_(self.mask, 0.0)
        if self.uniform_input_connectivity:
            self.gen_uniform_input_mask()
        elif self.diagonal_mask:
            assert self.fan_in == 1, "Diagonal mask only supported for fan-in 1"
            for i in range(self.out_features):
                self.mask[i][i] = 1
        else:
            for i in range(self.out_features):
                x = torch.randperm(self.in_features)[:self.fan_in]
                self.mask[i][x] = 1
    
    def gen_uniform_input_mask(self) -> None:
        """
        Generate a random fixed sparsity mask, ensuring there's uniform
        representation of the input features
        """
        # Create the sparsity mask with all zeros (to be updated)
        # Also create a list to track which indices to turn into NZWs
        nzw_indices = torch.tensor([])
        total_nzws = self.fan_in * self.out_features
        rem_nzws = total_nzws
        baseline_usage = int(rem_nzws/self.in_features)

        for i in range(baseline_usage):
            nzw_indices = torch.cat([nzw_indices, torch.randperm(self.in_features)])
        
        rem_nzws = rem_nzws - nzw_indices.shape[0]
        input_i_usage_l = []
        input_i_usage_q = heapdict.heapdict()
        for i in range(self.in_features):
            input_i_usage_q[i] = baseline_usage
            input_i_usage_l.append(baseline_usage)
        # print(input_i_usage_l)
        # print(list(input_i_usage_q.items()))
        # print()
        while rem_nzws > 0:
            # print(input_i_usage_l)
            # print(list(input_i_usage_q.items()))
            if torch.all(torch.tensor(input_i_usage_l) == input_i_usage_l[0]):
                print("All indices used equally -> make a random choice")
                index = np.random.randint(0, self.in_features)
                nzw_indices = torch.concat([nzw_indices, torch.tensor([int(index)]) ])
                rem_nzws = rem_nzws - 1
                input_i_usage_q[index] = input_i_usage_q[index]+1
                input_i_usage_l[index] += 1
            else:
                index, count = input_i_usage_q.popitem()
                indices_w_same_usage = []
                for i, u in enumerate(input_i_usage_l):
                    if u == count:
                        indices_w_same_usage.append(i)
                if len(indices_w_same_usage) > 1:
                    # print("Multiple indices (but not all) used equally -> make a random choice")
                    new_index = np.random.choice(indices_w_same_usage, 1)[0]
                    input_i_usage_q[index] = count
                    nzw_indices = torch.concat([nzw_indices, torch.tensor([new_index])])
                    rem_nzws = rem_nzws - 1
                    input_i_usage_q[new_index] = input_i_usage_q[new_index]+1
                    input_i_usage_l[new_index] += 1
                else:
                    nzw_indices = torch.concat([nzw_indices, torch.tensor([index])])
                    rem_nzws = rem_nzws - 1
                    input_i_usage_q[index] = count+1
                    input_i_usage_l[index] += 1
        s_pointer = 0
        for ri in range(self.out_features):
            for _ in range(self.fan_in):
                ci = int(nzw_indices[s_pointer])
                self.mask[ri][ci] = 1
                s_pointer += 1

    def forward(self):
        return self.mask

class ScalarScaleBias(nn.Module):
    def __init__(self, scale=True, scale_init=1.0, bias=True, bias_init=0.0) -> None:
        super(ScalarScaleBias, self).__init__()
        if scale:
            self.weight = Parameter(torch.Tensor(1))
        else:
            self.register_parameter('weight', None)
        if bias:
            self.bias = Parameter(torch.Tensor(1))
        else:
            self.register_parameter('bias', None)
        self.weight_init = scale_init
        self.bias_init = bias_init
        self.reset_parameters()

    # Change the default initialisation for BatchNorm
    def reset_parameters(self) -> None:
        if self.weight is not None:
            init.constant_(self.weight, self.weight_init)
        if self.bias is not None:
            init.constant_(self.bias, self.bias_init)

    def forward(self, x):
        if self.weight is not None:
            x = x*self.weight
        if self.bias is not None:
            x = x + self.bias
        return x

class ScalarBiasScale(ScalarScaleBias):
    def forward(self, x):
        if self.bias is not None:
            x = x + self.bias
        if self.weight is not None:
            x = x*self.weight
        return x

