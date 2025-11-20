
import torch
import torch.nn as nn

class MizanLoss(nn.Module):
    def __init__(self, p=2.0, eps=1e-8):
        super().__init__()
        self.p = p
        self.eps = eps
    def forward(self, y_pred, y_true):
        diff = torch.abs(y_pred - y_true)
        num = diff ** self.p
        denom = torch.abs(y_pred)**self.p + torch.abs(y_true)**self.p + self.eps
        return (num / denom).mean()

class CombinedMSE_MizanLoss(nn.Module):
    def __init__(self, p=2.0, eps=1e-8, lambda_mizan=0.1):
        super().__init__()
        self.mse = nn.MSELoss()
        self.mizan = MizanLoss(p=p, eps=eps)
        self.lambda_mizan = lambda_mizan
    def forward(self, y_pred, y_true):
        mse_loss = self.mse(y_pred, y_true)
        mizan_loss = self.mizan(y_pred, y_true)
        return mse_loss + self.lambda_mizan * mizan_loss, mse_loss, mizan_loss
