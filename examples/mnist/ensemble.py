import torch
import torch.nn as nn

from brevitas.core.quant import QuantType
from brevitas.nn import QuantIdentity, QuantHardTanh
from brevitas.core.scaling import ScalingImplType
from logicnets.quant import QuantBrevitasActivation
from logicnets.nn import (
    ScalarBiasScale, 
    ScalarScaleBias,
    RandomFixedSparsityMask2D,
    SparseLinearNeq_mask,
)

from models import MnistNeqModel


class AveragingMnistNeqModel(nn.Module):
    """
    With the averaging ensemble method, we train N models and average their
    outputs in the end.
    """

    def __init__(self, model_config, num_models, quantize_avg=False):
        super(AveragingMnistNeqModel, self).__init__()
        self.model_config = model_config
        self.num_models = num_models
        self.quantize_avg = quantize_avg
        self.same_input_scale = model_config["same_input_scale"]
        self.input_post_trans_sbs = model_config["input_post_trans_sbs"] # ScalarBiasScale
        self.input_post_trans_ssb = model_config["input_post_trans_ssb"] # ScalarScaleBias
        self.same_output_scale = model_config["same_output_scale"]

        self.shared_input_layer = model_config["shared_input_layer"]
        self.shared_output_layer = model_config["shared_output_layer"]
        self.input_length = model_config["input_length"]
        self.output_length = model_config["output_length"]
        shared_output_bitwidth = None
        if self.shared_output_layer:
            shared_output_bitwidth = model_config["shared_output_bitwidth"]

        self.ensemble = nn.ModuleList(
            [
                MnistNeqModel(
                    model_config,
                    shared_output_bitwidth=shared_output_bitwidth,
                ) 
                for _ in range(num_models)
            ]
        )
        self.is_verilog_inference = False
        if self.same_input_scale:
            # Share input quantizer among ensemble members
            if self.input_post_trans_ssb:
                self.ensemble[0].module_list[0].input_post_transform = ScalarScaleBias(scale=True)
            elif self.input_post_trans_sbs:
                print("Setting input_post_transform to ScalarBiasScale")
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
        elif self.shared_input_layer:
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
        if self.same_output_scale:
            # FOR DEBUGGING: Print output quantizer for each ensemble member
            print("BEFORE: Output quantizer for each ensemble member:")
            for model in self.ensemble:
                print(f"\t{hex(id(model.module_list[-1].output_quant))}")
            # Set all ensemble member's output quantizer to be the same as the
            # first model's output quantizer
            for model in self.ensemble[1:]:
                model.module_list[-1].output_quant = self.ensemble[0].module_list[-1].output_quant
            # FOR DEBUGGING: Print output quantizer for each ensemble member
            print("AFTER: Output quantizer for each ensemble member:")
            for model in self.ensemble:
                print(f"\t{hex(id(model.module_list[-1].output_quant))}")
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
        if self.shared_output_layer:
            outputs = self.ensemble[-1](outputs)
            # Sum every out_length elements to get the final output
            outputs = outputs.view(-1, self.num_models, self.output_length)
            outputs = outputs.sum(dim=1) 
        else:
            outputs = outputs.mean(dim=0)
        return outputs

    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        outputs = [model.verilog_forward(x) for model in self.ensemble]
        return sum(outputs)  # / self.num_models # Do division in pretransform

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


class AveragingMnistLUTModel(AveragingMnistNeqModel):
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


class BaggingMnistNeqModel(BaseEnsembleClassifier):
    """
    Bagging, i.e., training data for each member model is sampled with
    replacement
    """

    def __init__(
        self, model_config, num_models, quantize_avg=False, single_model_mode=False
    ):
        self.model_class = MnistNeqModel
        super(BaggingMnistNeqModel, self).__init__(
            self.model_class,
            model_config,
            num_models,
            quantize_avg,
            single_model_mode,
        )

class BaggingMnistLUTModel(BaggingMnistNeqModel):
    pass


class AdaBoostMnistNeqModel(BaseEnsembleClassifier):
    """
    AdaBoost ensemble of JetSubstructureNeqModel models.
    """

    def __init__(
        self,
        model_config,
        num_models,
        num_train_samples,
        num_classes=10,
        quantize_avg=False,
        single_model_mode=False,
    ):
        self.model_class = MnistNeqModel
        super(AdaBoostMnistNeqModel, self).__init__(
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
        outputs = sum(
            [
                alpha * self.adaboost_labels[torch.argmax(model(x), dim=1)]
                for alpha, model in zip(self.alphas, self.ensemble)
            ]
        )
        outputs = outputs / sum(self.alphas)
        return outputs
    

class AdaBoostMnistLUTModel(AdaBoostMnistNeqModel):
    pass