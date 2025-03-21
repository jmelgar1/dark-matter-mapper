import torch.nn as nn


class DarkMatter3DCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Conv3d(1, 32, 3, padding=1),
            nn.BatchNorm3d(32),
            nn.LeakyReLU(0.1),
            nn.MaxPool3d(2),  # 25x25x25

            nn.Conv3d(32, 64, 3, padding=1),
            nn.BatchNorm3d(64),
            nn.LeakyReLU(0.1),
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose3d(64, 32, 3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm3d(32),
            nn.LeakyReLU(0.1),

            # added an additional layer to reach 50x50x50
            nn.Conv3d(32, 32, 3, padding=1),
            nn.BatchNorm3d(32),
            nn.LeakyReLU(0.1),

            nn.Conv3d(32, 1, 3, padding=1),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        if x.shape[-3:] != (50, 50, 50):
            raise ValueError(f"Invalid output shape: {x.shape}")
        return x