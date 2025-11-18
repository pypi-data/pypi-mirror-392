"""
LSTM model for text classification tasks
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Tuple, Union, List

class TextLSTM(nn.Module):
    """
    LSTM model for text classification with configurable architecture.
    
    Features:
    - Embedding layer with optional pre-trained embeddings
    - Multi-layer bidirectional LSTM
    - Multiple pooling strategies
    - Configurable dropout for regularization
    - Dense layers with configurable sizes
    """
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 300,
        hidden_dim: int = 256,
        output_dim: int = 2,
        n_layers: int = 2,
        bidirectional: bool = True,
        dropout: float = 0.5,
        pad_idx: int = 1,
        pooling: str = 'max',
        embedding_weights: Optional[torch.Tensor] = None,
        fc_hidden_dim: Optional[int] = None
    ) -> None:
        """
        Initialize the TextLSTM model.
        
        Args:
            vocab_size: Size of the vocabulary
            embed_dim: Dimension of word embeddings
            hidden_dim: Hidden dimension of LSTM
            output_dim: Output dimension (number of classes)
            n_layers: Number of LSTM layers
            bidirectional: Whether to use bidirectional LSTM
            dropout: Dropout probability
            pad_idx: Padding index in vocabulary
            pooling: Pooling strategy ('max', 'mean', 'last', or 'attention')
            embedding_weights: Pre-trained embedding weights (optional)
            fc_hidden_dim: Hidden dimension of fully connected layer (if None, uses 2*hidden_dim)
        """
        super().__init__()
        
        # Save parameters
        self.bidirectional = bidirectional
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.pooling = pooling
        
        # Define layers
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        if embedding_weights is not None:
            self.embedding.weight = nn.Parameter(embedding_weights)
            
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers=n_layers,
            bidirectional=bidirectional,
            batch_first=True,
            dropout=dropout if n_layers > 1 else 0
        )
        
        self.dropout = nn.Dropout(dropout)
        
        # Determine input dimension for classifier
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        
        # Add attention layer if needed
        if pooling == 'attention':
            self.attention = nn.Linear(lstm_output_dim, 1)
        
        # Fully connected classifier layers
        if fc_hidden_dim is not None:
            self.fc = nn.Sequential(
                nn.Linear(lstm_output_dim, fc_hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(fc_hidden_dim, output_dim)
            )
        else:
            self.fc = nn.Linear(lstm_output_dim, output_dim)
            
        # Initialize parameters
        self._init_weights()
        
    def _init_weights(self) -> None:
        """Initialize model weights for better performance."""
        for name, param in self.named_parameters():
            if 'weight' in name and 'embedding' not in name:
                nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)
        
    def forward(
        self, 
        text: torch.Tensor, 
        text_lengths: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass of the model.
        
        Args:
            text: Input tensor of token indices [batch_size, seq_len]
            text_lengths: Actual lengths of sequences in batch (for packed sequence)
            
        Returns:
            Logits for each class [batch_size, output_dim]
        """
        # Get embeddings
        embedded = self.embedding(text)  # [batch_size, seq_len, embed_dim]
        
        # Pack sequences if lengths are provided
        if text_lengths is not None:
            packed_embedded = nn.utils.rnn.pack_padded_sequence(
                embedded, text_lengths.cpu(), batch_first=True, enforce_sorted=False
            )
            packed_output, (hidden, _) = self.lstm(packed_embedded)
            # Unpack the sequence
            output, _ = nn.utils.rnn.pad_packed_sequence(packed_output, batch_first=True)
        else:
            output, (hidden, _) = self.lstm(embedded)
        
        # Apply different pooling strategies
        if self.pooling == 'max':
            # Max pooling over time dimension
            pooled = torch.max(output, dim=1)[0]
        
        elif self.pooling == 'mean':
            # Mean pooling over time dimension
            if text_lengths is not None:
                # Create a mask for padding
                mask = torch.zeros_like(output, dtype=torch.bool)
                for i, length in enumerate(text_lengths):
                    mask[i, :length] = 1
                # Apply mask and calculate mean
                pooled = (output * mask.float()).sum(dim=1) / text_lengths.unsqueeze(1).float()
            else:
                pooled = torch.mean(output, dim=1)
        
        elif self.pooling == 'last':
            # Use last hidden state
            if self.bidirectional:
                # Concatenate the last hidden state from both directions
                # For bidirectional, hidden is [num_layers * 2, batch_size, hidden_dim]
                last_forward = hidden[-2, :, :]
                last_backward = hidden[-1, :, :]
                pooled = torch.cat((last_forward, last_backward), dim=1)
            else:
                # For unidirectional, hidden is [num_layers, batch_size, hidden_dim]
                pooled = hidden[-1, :, :]
        
        elif self.pooling == 'attention':
            # Attention pooling
            attention_weights = F.softmax(self.attention(output).squeeze(-1), dim=1)
            pooled = torch.bmm(attention_weights.unsqueeze(1), output).squeeze(1)
        
        else:
            raise ValueError(f"Unsupported pooling method: {self.pooling}")
        
        # Apply dropout and pass through fully connected layers
        pooled = self.dropout(pooled)
        return self.fc(pooled)
