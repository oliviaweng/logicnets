import torch
import torch.nn as nn

from brevitas.core.quant import QuantType
from brevitas.nn import QuantIdentity
from logicnets.quant import QuantBrevitasActivation


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
        self.ensemble = nn.ModuleList(
            [JetSubstructureNeqModel(model_config) for _ in range(num_models)]
        )
        self.is_verilog_inference = False
        if quantize_avg:
            self.avg_quant = QuantBrevitasActivation(
                QuantIdentity(
                    bit_width=model_config["output_bitwidth"],
                    quant_type=QuantType.INT,
                )
            )

    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)

    def pytorch_forward(self, x):
        outputs = torch.stack([model(x) for model in self.ensemble], dim=0)
        outputs = outputs.mean(dim=0)
        if self.quantize_avg:
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
        # self.adaboost_labels = (
        #     torch.ones(num_classes, num_classes) * -1 / (num_classes - 1)
        # )
        # self.adaboost_labels[torch.eye(num_classes) == 1] = 1  # Set diagonal to 1
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
