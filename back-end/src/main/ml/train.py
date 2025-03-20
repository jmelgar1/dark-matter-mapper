import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

from src.main.ml.model import DarkMatter3DCNN

class SyntheticDataset(Dataset):
    #we are going to use fake dark matter map data just to test for now
    def __init__(self, n_samples=100):
        self.n_samples = n_samples
        self.voxel_size = 50

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        #create random galaxy distribution, poisson because galaxies follow a poisson distribution (random with rules)
        galaxies = np.random.poisson(lam=0.1, size=(self.voxel_size, self.voxel_size, self.voxel_size))

        #faking dark metter correlation, dark matter uses a gaussian distribution
        dark_matter = galaxies + np.random.normal(scale=0.05, size=galaxies.shape)
        return (
            torch.tensor(galaxies).unsqueeze(0).float(),
            torch.tensor(dark_matter).unsqueeze(0).float(),
        )

def train():
    model = DarkMatter3DCNN()
    dataset = SyntheticDataset()
    loader = DataLoader(dataset, batch_size=4, shuffle=True)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(10):
        for galaxies, targets in loader:
            optimizer.zero_grad() #reset the gradients
            outputs = model(galaxies) #forward pass
            loss = criterion(outputs, targets) #compute the loss
            loss.backward() #backpropagate gradients
            optimizer.step() #update the weights
        print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")

    torch.save(model.state_dict(), "weights.pth")


if __name__ == "__main__":
    train()