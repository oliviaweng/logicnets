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
        self.ensemble = nn.ModuleList([JetSubstructureNeqModel(model_config) for _ in range(num_models)])
        self.is_verilog_inference = False
        self.avg_quant = QuantBrevitasActivation(
            QuantIdentity(
                # TODO: Might need to adjust output bitwidth (+/- 1) after mean operation
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
        return sum(outputs) / self.num_models
    
    def verilog_inference(self, verilog_dir, top_module_filename, logfile=None, add_registers: bool = False):
        pass
    
    def pytorch_inference(self):
        self.is_verilog_inference = False

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
        single_model_mode=False
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
            self.ensemble = nn.ModuleList([
                model_class(model_config) for _ in range(num_models)
            ])
        self.avg_quant = QuantBrevitasActivation(
            QuantIdentity(
                # TODO: Might need to adjust output bitwidth (+/- 1) after mean operation
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
    
    def verilog_inference(self, verilog_dir, top_module_filename, logfile=None, add_registers: bool = False):
        pass
    
    def pytorch_inference(self):
        self.is_verilog_inference = False


class BaggingJetNeqModel(BaseEnsembleClassifier):
    """
    Bagging, i.e., training data for each member model is sampled with
    replacement
    """
    def __init__(
        self, 
        model_config, 
        num_models, 
        quantize_avg=False,
        single_model_mode=False
    ):
        self.model_class = JetSubstructureNeqModel
        super(BaggingJetNeqModel, self).__init__(
            self.model_class, model_config, num_models, quantize_avg, single_model_mode,
        )