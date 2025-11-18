"""
GloVe (Global Vectors for Word Representation) implementation
based on "GloVe: Global Vectors for Word Representation"
https://nlp.stanford.edu/pubs/glove.pdf
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Union, Set
import logging
from tqdm import tqdm
import math
import pickle

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

class CoOccurrenceMatrix:
    """Efficient cooccurrence matrix builder for GloVe"""
    
    def __init__(
        self,
        texts: List[List[str]],
        vocab: Dict[str, int],
        window_size: int = 10,
        min_count: int = 5,
        symmetric: bool = True
    ):
        """
        Initialize and build the co-occurrence matrix
        
        Args:
            texts: List of tokenized texts
            vocab: Word to index mapping
            window_size: Context window size
            min_count: Minimum count to include a word in the vocabulary
            symmetric: Whether to make the co-occurrence matrix symmetric
        """
        self.texts = texts
        self.vocab = vocab
        self.window_size = window_size
        self.min_count = min_count
        self.symmetric = symmetric
        
        # Initialize co-occurrence matrix as sparse dictionary
        self.cooccur = defaultdict(float)
        
        # Build matrix
        self._build_matrix()
    
    def _build_matrix(self):
        """Build co-occurrence matrix from texts"""
        logging.info("Building co-occurrence matrix...")
        
        # Function to add co-occurrence count with decay
        def add_cooccurrence(word_idx, context_idx, distance):
            # Apply distance decay weight
            if self.symmetric:
                # For symmetric matrices (most common for GloVe)
                weight = 1.0 / distance
                self.cooccur[(word_idx, context_idx)] += weight
                self.cooccur[(context_idx, word_idx)] += weight
            else:
                # For asymmetric matrices
                weight = 1.0 / distance
                self.cooccur[(word_idx, context_idx)] += weight
        
        for text in tqdm(self.texts, desc="Building co-occurrence matrix"):
            # Convert text to indices, filtering words not in vocabulary
            indices = [self.vocab[word] for word in text if word in self.vocab]
            
            if len(indices) < 2:
                continue
                
            for center_pos, center_idx in enumerate(indices):
                # Consider window of words around the center word
                for context_pos in range(max(0, center_pos - self.window_size), 
                                         min(len(indices), center_pos + self.window_size + 1)):
                    # Skip the center word
                    if context_pos == center_pos:
                        continue
                        
                    context_idx = indices[context_pos]
                    distance = abs(context_pos - center_pos)
                    
                    # Add to co-occurrence with decay weight
                    add_cooccurrence(center_idx, context_idx, distance)
        
        # Convert to list of (i, j, count) for efficient DataLoader usage
        self.cooccur_triplets = [(i, j, count) for (i, j), count in self.cooccur.items()]
        
        logging.info(f"Co-occurrence matrix built with {len(self.cooccur_triplets)} non-zero entries")
    
    def save(self, file_path: str):
        """Save the co-occurrence matrix to a file"""
        with open(file_path, 'wb') as f:
            pickle.dump({
                'cooccur_triplets': self.cooccur_triplets,
                'vocab': self.vocab,
                'window_size': self.window_size,
                'symmetric': self.symmetric
            }, f)
        
        logging.info(f"Co-occurrence matrix saved to {file_path}")
    
    @classmethod
    def load(cls, file_path: str):
        """Load a pre-computed co-occurrence matrix"""
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            
        # Create an instance
        matrix = cls.__new__(cls)
        
        # Set attributes
        matrix.cooccur_triplets = data['cooccur_triplets']
        matrix.vocab = data['vocab']
        matrix.window_size = data['window_size']
        matrix.symmetric = data['symmetric']
        
        return matrix


class GloVeDataset(Dataset):
    """Dataset for GloVe training"""
    
    def __init__(self, cooccurrence_matrix: CoOccurrenceMatrix, x_max: float = 100.0, alpha: float = 0.75):
        """
        Initialize GloVe dataset
        
        Args:
            cooccurrence_matrix: Pre-built co-occurrence matrix
            x_max: Maximum co-occurrence value for weighting
            alpha: Exponent for weighting function
        """
        self.cooccur_triplets = cooccurrence_matrix.cooccur_triplets
        self.x_max = x_max
        self.alpha = alpha
    
    def __len__(self):
        return len(self.cooccur_triplets)
    
    def __getitem__(self, idx):
        i, j, count = self.cooccur_triplets[idx]
        
        # Compute GloVe weighting factor
        if count < self.x_max:
            weight = (count / self.x_max) ** self.alpha
        else:
            weight = 1.0
            
        return (
            torch.tensor(i, dtype=torch.long),
            torch.tensor(j, dtype=torch.long),
            torch.tensor(count, dtype=torch.float32),
            torch.tensor(weight, dtype=torch.float32)
        )


class GloVeModel(nn.Module):
    """GloVe model implementation"""
    
    def __init__(self, vocab_size: int, embedding_dim: int = 300):
        """
        Initialize GloVe model
        
        Args:
            vocab_size: Size of vocabulary
            embedding_dim: Dimension of embeddings
        """
        super().__init__()
        
        # Word embeddings
        self.w_embeddings = nn.Embedding(vocab_size, embedding_dim)
        
        # Context embeddings
        self.c_embeddings = nn.Embedding(vocab_size, embedding_dim)
        
        # Word biases
        self.w_biases = nn.Embedding(vocab_size, 1)
        
        # Context biases
        self.c_biases = nn.Embedding(vocab_size, 1)
        
        # Initialize parameters
        self._init_weights()
    
    def _init_weights(self):
        """Initialize embeddings with small random values"""
        initrange = 0.5 / self.w_embeddings.embedding_dim
        
        self.w_embeddings.weight.data.uniform_(-initrange, initrange)
        self.c_embeddings.weight.data.uniform_(-initrange, initrange)
        
        self.w_biases.weight.data.zero_()
        self.c_biases.weight.data.zero_()
    
    def forward(self, i, j, count, weight):
        """
        Forward pass computing GloVe loss
        
        Args:
            i: Central word indices
            j: Context word indices
            count: Co-occurrence counts
            weight: Weights for each pair
            
        Returns:
            Weighted loss value
        """
        # Get embeddings and biases
        w_embed = self.w_embeddings(i)  # [batch_size, embed_dim]
        c_embed = self.c_embeddings(j)  # [batch_size, embed_dim]
        
        w_bias = self.w_biases(i).squeeze()  # [batch_size]
        c_bias = self.c_biases(j).squeeze()  # [batch_size]
        
        # Compute dot product between word vectors
        dot_product = torch.sum(w_embed * c_embed, dim=1)  # [batch_size]
        
        # Add biases
        log_prediction = dot_product + w_bias + c_bias  # [batch_size]
        
        # Target is log of co-occurrence
        log_cooccurrence = torch.log(count)  # [batch_size]
        
        # Compute difference
        diff = log_prediction - log_cooccurrence  # [batch_size]
        
        # Compute weighted squared error
        loss = weight * torch.pow(diff, 2)  # [batch_size]
        
        # Return mean loss
        return loss.mean()
    
    def get_word_vectors(self):
        """Get word vectors by adding both embedding matrices"""
        return self.w_embeddings.weight.data + self.c_embeddings.weight.data


class GloVeTrainer:
    """Trainer for GloVe models"""
    
    def __init__(
        self,
        texts: Optional[List[List[str]]] = None,
        cooccurrence_matrix: Optional[CoOccurrenceMatrix] = None,
        embedding_dim: int = 300,
        window_size: int = 10,
        min_count: int = 5,
        x_max: float = 100.0,
        alpha: float = 0.75,
        epochs: int = 50,
        batch_size: int = 512,
        learning_rate: float = 0.05,
        lr_decay: float = 0.9
    ):
        """
        Initialize GloVe trainer
        
        Args:
            texts: List of tokenized texts (not needed if cooccurrence_matrix is provided)
            cooccurrence_matrix: Pre-built co-occurrence matrix
            embedding_dim: Dimension of word embeddings
            window_size: Context window size
            min_count: Minimum word frequency
            x_max: Maximum co-occurrence value for weighting
            alpha: Exponent for weighting function
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Initial learning rate
            lr_decay: Learning rate decay per epoch
        """
        self.embedding_dim = embedding_dim
        self.window_size = window_size
        self.min_count = min_count
        self.x_max = x_max
        self.alpha = alpha
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.lr_decay = lr_decay
        
        # Build vocabulary if texts are provided
        if texts is not None:
            self.vocab = self._build_vocab(texts)
            self.vocab_size = len(self.vocab)
            
            # Build co-occurrence matrix
            self.cooccurrence_matrix = CoOccurrenceMatrix(
                texts=texts,
                vocab=self.vocab,
                window_size=window_size,
                min_count=min_count
            )
        elif cooccurrence_matrix is not None:
            # Use provided matrix
            self.cooccurrence_matrix = cooccurrence_matrix
            self.vocab = cooccurrence_matrix.vocab
            self.vocab_size = len(self.vocab)
        else:
            raise ValueError("Either texts or cooccurrence_matrix must be provided")
        
        # Create dataset
        self.dataset = GloVeDataset(
            cooccurrence_matrix=self.cooccurrence_matrix,
            x_max=x_max,
            alpha=alpha
        )
        
        # Create dataloader
        self.dataloader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )
        
        # Create model
        self.model = GloVeModel(
            vocab_size=self.vocab_size,
            embedding_dim=embedding_dim
        )
        
        # Create optimizer
        self.optimizer = optim.Adagrad(self.model.parameters(), lr=learning_rate)
    
    def _build_vocab(self, texts: List[List[str]]) -> Dict[str, int]:
        """Build vocabulary from texts"""
        word_counts = Counter()
        for text in texts:
            word_counts.update(text)
        
        # Filter words by frequency
        vocab_words = [word for word, count in word_counts.items() 
                      if count >= self.min_count]
        
        # Create word to index mapping
        vocab = {word: i for i, word in enumerate(vocab_words)}
        
        logging.info(f"Vocabulary size: {len(vocab)}")
        return vocab
    
    def train(self):
        """Train the GloVe model"""
        logging.info("Training GloVe model")
        
        self.model.train()
        
        # Training loop
        total_steps = len(self.dataloader) * self.epochs
        progress_bar = tqdm(total=total_steps, desc="Training")
        
        current_lr = self.learning_rate
        
        for epoch in range(self.epochs):
            total_loss = 0
            
            # Adjust learning rate
            if epoch > 0:
                current_lr *= self.lr_decay
                for param_group in self.optimizer.param_groups:
                    param_group['lr'] = current_lr
            
            for batch in self.dataloader:
                self.optimizer.zero_grad()
                
                # Forward pass
                loss = self.model(*batch)
                
                # Backward pass
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                progress_bar.update(1)
            
            avg_loss = total_loss / len(self.dataloader)
            logging.info(f"Epoch {epoch+1}/{self.epochs}, Loss: {avg_loss:.4f}, LR: {current_lr:.6f}")
        
        progress_bar.close()
        logging.info("Training complete")
    
    def get_word_vectors(self) -> Dict[str, np.ndarray]:
        """Get word vectors as a dictionary mapping words to embeddings"""
        self.model.eval()
        vectors = self.model.get_word_vectors()
        
        idx_to_word = {idx: word for word, idx in self.vocab.items()}
        
        word_vectors = {}
        for idx, word in idx_to_word.items():
            word_vectors[word] = vectors[idx].cpu().numpy()
            
        return word_vectors
    
    def save_vectors(self, file_path: str):
        """Save word vectors to a file"""
        vectors = self.get_word_vectors()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{len(vectors)} {self.embedding_dim}\n")
            for word, vec in vectors.items():
                vec_str = ' '.join(map(str, vec))
                f.write(f"{word} {vec_str}\n")
        
        logging.info(f"Word vectors saved to {file_path}")
    
    def save_model(self, file_path: str):
        """Save model parameters"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'vocab': self.vocab,
            'embedding_dim': self.embedding_dim
        }, file_path)
        
        logging.info(f"Model saved to {file_path}")
    
    @classmethod
    def load_model(cls, file_path: str, cooccurrence_path: Optional[str] = None):
        """Load a pre-trained model"""
        checkpoint = torch.load(file_path)
        
        # Initialize an empty trainer
        trainer = cls.__new__(cls)
        
        # Set attributes from checkpoint
        trainer.vocab = checkpoint['vocab']
        trainer.vocab_size = len(trainer.vocab)
        trainer.embedding_dim = checkpoint['embedding_dim']
        
        # Create model and load weights
        trainer.model = GloVeModel(
            vocab_size=trainer.vocab_size,
            embedding_dim=trainer.embedding_dim
        )
        trainer.model.load_state_dict(checkpoint['model_state_dict'])
        
        # Load co-occurrence matrix if provided
        if cooccurrence_path:
            trainer.cooccurrence_matrix = CoOccurrenceMatrix.load(cooccurrence_path)
        
        return trainer


def train_glove(
    texts: List[List[str]],
    embedding_dim: int = 300,
    window_size: int = 10,
    min_count: int = 5,
    epochs: int = 50,
    batch_size: int = 512,
    learning_rate: float = 0.05,
    save_path: Optional[str] = None,
    save_cooccur_path: Optional[str] = None
) -> GloVeTrainer:
    """
    Train a GloVe model and return the trainer
    
    Args:
        texts: List of tokenized texts
        embedding_dim: Dimension of word embeddings
        window_size: Context window size
        min_count: Minimum word frequency
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Initial learning rate
        save_path: If provided, save the trained model to this path
        save_cooccur_path: If provided, save the co-occurrence matrix to this path
        
    Returns:
        Trained GloVeTrainer instance
    """
    trainer = GloVeTrainer(
        texts=texts,
        embedding_dim=embedding_dim,
        window_size=window_size,
        min_count=min_count,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    
    # Save co-occurrence matrix if requested
    if save_cooccur_path:
        trainer.cooccurrence_matrix.save(save_cooccur_path)
    
    # Train the model
    trainer.train()
    
    # Save model if requested
    if save_path:
        trainer.save_model(save_path)
    
    return trainer
