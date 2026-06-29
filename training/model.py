import torch
from encoder_pretraining.vqvae_model.vqvae import VQVAE


ckpt = torch.load("encoder_pretraining/checkpoints/best.pt", map_location=torch.device("cuda"))
print(ckpt.keys())
