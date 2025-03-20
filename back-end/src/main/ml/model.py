import torch
import torch.nn as nn


class DarkMatter3DCNN(nn.Module):
    def __init__(self, input_shape=(50, 50, 50)):
        super().__init__()

        #Here we have two layers of Convolution and pooling. If we only had one we would miss out on
        #the big picture which is critical for dark matter. We would be able to detect clusters and groups
        #of galaxies but miss out on large scale structures.
        self.conv_layers = nn.Sequential(
            # Layer 1: Detect small-scale galaxy patterns
            nn.Conv3d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool3d(2),

            # Layer 2: Detect large-scale galaxy patterns
            nn.Conv3d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool3d(2),
            nn.Flatten()
        )

        # calculate flattened size after convolutions
        with torch.no_grad():
            dummy = torch.zeros(1, 1, *input_shape)
            flattened_size = self.conv_layers(dummy).shape[1]

        self.fc = nn.Sequential(
            nn.Linear(flattened_size, 128),
            nn.ReLU(),
            nn.Linear(128, input_shape[0] * input_shape[1] * input_shape[2])  # Predict voxel grid
        )

    def forward(self, x):
        x = self.conv_layers(x)
        return self.fc(x).view(-1, 1, 50, 50, 50)  # Reshape to 3D