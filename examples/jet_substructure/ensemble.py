import torch
import torch.nn as nn

from models import JetSubstructureNeqModel

class AveragingJetNeqModel(nn.Module):
    """
    With the averaging ensemble method, we train N models independently and average
    their outputs in the end.
    """
    def __init__(self, model_config, num_models):
        super(AveragingJetNeqModel, self).__init__()
        self.model_config = model_config
        self.num_models = num_models
        self.ensemble = nn.ModuleList([JetSubstructureNeqModel(model_config) for _ in range(num_models)])
        self.is_verilog_inference = False

    def forward(self, x):
        if self.is_verilog_inference:
            return self.verilog_forward(x)
        return self.pytorch_forward(x)

    def pytorch_forward(self, x):
        outputs = torch.stack([model(x) for model in self.ensemble], dim=0)
        return outputs.mean(dim=0)
    
    # TODO: Implement verilog_forward() and verilog_inference()
    def verilog_forward(self, x):
        outputs = [model.verilog_forward(x) for model in self.ensemble]
        return sum(outputs) / self.num_models
    
    def verilog_inference(self, verilog_dir, top_module_filename, logfile=None, add_registers: bool = False):
        pass
    
    def pytorch_inference(self):
        self.is_verilog_inference = False