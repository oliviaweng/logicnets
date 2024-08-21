import torch
import torch.nn as nn

from brevitas.core.quant import QuantType
from brevitas.nn import QuantIdentity
from logicnets.quant import QuantBrevitasActivation

from pyverilator import PyVerilator
from os.path import realpath
from functools import reduce


from models import JetSubstructureNeqModel


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
        self.same_output_scale = model_config["same_output_scale"]
        self.ensemble = nn.ModuleList(
            [JetSubstructureNeqModel(model_config) for _ in range(num_models)]
        )
        self.is_verilog_inference = False
        if quantize_avg: # For packing averaging into a LUT
            self.avg_quant = QuantBrevitasActivation(
                QuantIdentity(
                    bit_width=model_config["output_bitwidth"],
                    quant_type=QuantType.INT,
                )
            )
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



    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)

    def pytorch_forward(self, x):
        outputs = torch.stack([model(x) for model in self.ensemble], dim=0)
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

    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)

    def pytorch_forward(self, x):
        if self.single_model_mode:
            outputs = self.model(x)
            return outputs
        outputs = torch.stack([model(x) for model in self.ensemble], dim=0)
        outputs = outputs.mean(dim=0)
        if self.quantize_avg:
            outputs = self.avg_quant(outputs)
        return outputs

    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        outputs = [model.verilog_forward(x) for model in self.ensemble]
        return sum(outputs) / self.num_models

    def verilog_inference(
        self,
        verilog_dir,
        top_module_filename,
        logfile=None,
        add_registers: bool = False,
    ):
        pass

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
        # self.alphas = torch.tensor([])  # Accuracy measures for each model
        self.register_buffer("alphas", torch.tensor([]))
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
        outputs = sum(
            [
                alpha * self.adaboost_labels[torch.argmax(model(x), dim=1)]
                for alpha, model in zip(self.alphas, self.ensemble)
            ]
        )
        outputs = outputs / sum(self.alphas)
        return outputs
