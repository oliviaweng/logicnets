import torch
import torch.nn as nn

from brevitas.core.quant import QuantType
from brevitas.nn import QuantIdentity
from logicnets.quant import QuantBrevitasActivation


from models import JetSubstructureNeqModel

class AveragingJetNeqModel(nn.Module):
    """
    With the averaging ensemble method, we train N models independently and average
    their outputs in the end.
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