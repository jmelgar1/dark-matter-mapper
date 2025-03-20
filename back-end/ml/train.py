import torch

from ml.model import DarkMatter3DCNN

model = DarkMatter3DCNN()
torch.save(model.state_dict(), "placeholder_weights.pth")