import math
import torch
from torch import nn
from transformers import T5ForConditionalGeneration
from encoder_pretraining.vqvae_model.vqvae import VQVAE
from transformers.modeling_outputs import BaseModelOutput


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

device = get_device()

## vqvae model
ckpt = torch.load("encoder_pretraining/checkpoints/best.pt", map_location=torch.device(device))
vqvae_model = VQVAE(
    h_dim=ckpt['args']['h_dim'],
    res_h_dim=ckpt['args']['res_h_dim'],
    n_res_layers=ckpt['args']['n_res_layers'],
    n_embeddings=ckpt['args']['n_embeddings'],
    embedding_dim=ckpt['args']['embedding_dim'],
    beta=ckpt['args']['beta'],
).to(device)

vqvae_model.load_state_dict(ckpt["model_state_dict"])

## T5 model
t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")

## This is from https://github.com/Exorust/TorchLeet/blob/main/v3/modern-architectures/2d-positional-embeddings/2d-positional-embeddings_SOLN.ipynb
def create_2d_sinusoidal_embeddings(height: int, width: int, d_model: int) -> torch.Tensor:
    """
    Create 2D sinusoidal positional embeddings.

    Args:
        height:  number of rows in the patch grid
        width:   number of columns in the patch grid
        d_model: total embedding dimension (must be even)

    Returns:
        Tensor of shape (height * width, d_model)
    """
    assert d_model % 2 == 0, "d_model must be even"
    d_half = d_model // 2

    # Step 1: Frequency divisor term
    div_term = torch.exp(torch.arange(0, d_half, 2, dtype=torch.float) * -(math.log(10000.0) / d_half))

    # Step 2: Row positional embeddings
    row_pos = torch.arange(height, dtype=torch.float).unsqueeze(1)  # (height, 1)
    pe_row = torch.zeros(height, d_half)
    pe_row[:, 0::2] = torch.sin(row_pos * div_term)
    pe_row[:, 1::2] = torch.cos(row_pos * div_term)

    # Step 3: Column positional embeddings
    col_pos = torch.arange(width, dtype=torch.float).unsqueeze(1)  # (width, 1)
    pe_col = torch.zeros(width, d_half)
    pe_col[:, 0::2] = torch.sin(col_pos * div_term)
    pe_col[:, 1::2] = torch.cos(col_pos * div_term)

    # Step 4: Combine row and column embeddings via outer product broadcast
    # pe_row: (height, d_half) -> (height, 1, d_half)
    # pe_col: (width, d_half)  -> (1, width, d_half)
    pe_row = pe_row.unsqueeze(1).expand(height, width, d_half)
    pe_col = pe_col.unsqueeze(0).expand(height, width, d_half)

    # Concatenate along embedding dim: (height, width, d_model)
    pe = torch.cat([pe_row, pe_col], dim=-1)

    # Reshape to (height * width, d_model)
    return pe.reshape(height * width, d_model)


class VQVAE_T5(torch.nn.Module):
    def __init__(self, vqvae_model, t5_model):
        super(VQVAE_T5, self).__init__()
        self.vqvae_model = vqvae_model
        self.t5_model = t5_model
        self.d_model = t5_model.config.d_model
        self.image_proj = nn.Linear(vqvae_model.vector_quantization.e_dim, self.d_model)

    def forward(self, x, labels=None):
        z_q, indices, embedding_loss, perplexity = self.vqvae_model.encode_to_tokens(x)
        B, C, H, W = z_q.shape
        ## I need to reshape the z_q to (B, H*W, C) to match the input shape expected by T5 model. 
        ## The T5 model expects input of shape (batch_size, sequence_length, embedding_dim). Here, H*W is the sequence length and C is the embedding dimension.
        z_q = z_q.permute(0, 2, 3, 1).reshape(B, H * W, C) 
        z_q = self.image_proj(z_q) 

        pe = create_2d_sinusoidal_embeddings(H, W, self.d_model).to(z_q.device)
        z_q = z_q + pe.unsqueeze(0)

        encoder_outputs = BaseModelOutput(last_hidden_state=z_q)
        
        t5_output = self.t5_model(encoder_outputs=encoder_outputs, labels=labels)
        
        return embedding_loss, perplexity, t5_output