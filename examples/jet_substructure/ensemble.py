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
)

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
        self.same_input_scale = model_config["same_input_scale"]
        self.input_post_trans_sbs = model_config["input_post_trans_sbs"] # ScalarBiasScale
        self.same_output_scale = model_config["same_output_scale"]
        self.same_output_scale_sum = model_config["same_output_scale_sum"]
        self.shared_input_quant = model_config["shared_input_quant"]
        self.shared_input_layer = model_config["shared_input_layer"]
        self.input_length = model_config["input_length"]
        # TODO: Add output_pre_transforms
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



    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)

    def pytorch_forward(self, x):
        if self.shared_input_quant and self.shared_input_layer:
            x = self.input_quant_layer(x)
            outputs = torch.stack(
                [
                    model(x[:, i * self.input_length : (i + 1) * self.input_length])
                    for i, model in enumerate(self.ensemble)
                ],
                dim=0,
            )
        else:
            if self.shared_input_quant:
                x = self.input_quant(x)
            outputs = torch.stack([model(x) for model in self.ensemble], dim=0)

        if self.same_output_scale_sum:
            outputs = outputs.sum(dim=0)
        else:
            outputs = outputs.mean(dim=0)
        if self.quantize_avg: # For packing averaging into a LUT
            outputs = self.avg_quant(outputs)
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
