"""
Word2Vec implementation supporting both Skip-gram and CBOW architectures
based on "Efficient Estimation of Word Representations in Vector Space"
https://arxiv.org/abs/1301.3781
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from collections import Counter, deque
from typing import List, Dict, Tuple, Optional, Union, Iterator, Callable
import logging
import random
from tqdm import tqdm

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

class Word2VecDataset(Dataset):
    """Dataset for generating training samples for Word2Vec"""
    
    def __init__(
        self,
        texts: List[List[str]],
        word_to_idx: Dict[str, int],
        window_size: int = 5,
        mode: str = 'skipgram',
        ns_exponent: float = 0.75,
        negative_samples: int = 5,
        min_count: int = 5,
        subsampling_threshold: float = 1e-5
    ):
        """
        Initialize Word2Vec dataset
        
        Args:
            texts: List of tokenized sentences (list of list of tokens)
            word_to_idx: Mapping from words to indices
            window_size: Context window size
            mode: Training mode ('skipgram' or 'cbow')
            ns_exponent: Exponent for negative sampling distribution
            negative_samples: Number of negative samples per positive sample
            min_count: Minimum frequency for a word to be included
            subsampling_threshold: Threshold for subsampling frequent words
        """
        self.texts = texts
        self.word_to_idx = word_to_idx
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        self.vocab_size = len(word_to_idx)
        self.window_size = window_size
        self.mode = mode.lower()
        self.negative_samples = negative_samples
        
        # Prepare data
        self.data = []
        self._prepare_training_data()
        
        # Prepare negative sampling distribution
        word_counts = Counter()
        for text in texts:
            word_counts.update([w for w in text if w in self.word_to_idx])
            
        self.word_counts = {self.word_to_idx[word]: count for word, count in word_counts.items() 
                            if count >= min_count}
        
        # Prepare subsampling
        self.total_words = sum(self.word_counts.values())
        self.discard_probs = {}
        for word_idx, count in self.word_counts.items():
            frequency = count / self.total_words
            # Formula from original Word2Vec paper
            self.discard_probs[word_idx] = 1.0 - np.sqrt(subsampling_threshold / frequency)
        
        # Prepare negative sampling distribution
        ns_counts = {idx: count ** ns_exponent for idx, count in self.word_counts.items()}
        total = sum(ns_counts.values())
        self.ns_prob = {idx: count / total for idx, count in ns_counts.items()}
        self.ns_dist = list(self.ns_prob.keys())
        self.ns_weights = list(self.ns_prob.values())
    
    def _prepare_training_data(self):
        """Process raw texts into training pairs"""
        for text in self.texts:
            indices = [self.word_to_idx[word] for word in text if word in self.word_to_idx]
            if len(indices) < 2:
                continue
                
            # Apply subsampling
            if hasattr(self, 'discard_probs'):
                indices = [idx for idx in indices if 
                          idx not in self.discard_probs or 
                          random.random() > self.discard_probs[idx]]
            
            for i, idx in enumerate(indices):
                # Define context window boundaries
                start = max(0, i - self.window_size)
                end = min(len(indices), i + self.window_size + 1)
                
                # Get context words
                context_indices = [indices[j] for j in range(start, end) if j != i]
                
                if not context_indices:
                    continue
                    
                if self.mode == 'skipgram':
                    # For skip-gram, each context word becomes a sample
                    for context_idx in context_indices:
                        self.data.append((idx, context_idx))
                else:  # CBOW
                    # For CBOW, all context words together form one sample
                    self.data.append((context_indices, idx))
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = self.data[idx]
        
        if self.mode == 'skipgram':
            target_idx, context_idx = sample
            # Generate negative samples
            neg_samples = self._get_negative_samples(context_idx)
            return target_idx, context_idx, neg_samples
        else:  # CBOW
            context_indices, target_idx = sample
            # For CBOW we'll average the context vectors
            context_indices = torch.tensor(context_indices, dtype=torch.long)
            # Generate negative samples
            neg_samples = self._get_negative_samples(target_idx)
            return context_indices, target_idx, neg_samples
    
    def _get_negative_samples(self, positive_idx):
        """Generate negative samples, making sure to exclude the positive sample"""
        samples = []
        while len(samples) < self.negative_samples:
            sample = np.random.choice(self.ns_dist, p=self.ns_weights)
            if sample != positive_idx and sample not in samples:
                samples.append(sample)
        return torch.tensor(samples, dtype=torch.long)


class Word2Vec(nn.Module):
    """Word2Vec model supporting both Skip-gram and CBOW architectures"""
    
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 300,
        mode: str = 'skipgram',
        padding_idx: Optional[int] = None,
        sparse: bool = False
    ):
        """
        Initialize Word2Vec model
        
        Args:
            vocab_size: Size of vocabulary
            embedding_dim: Dimension of word embeddings
            mode: Model architecture ('skipgram' or 'cbow')
            padding_idx: If specified, padded embeddings will remain zeroed
            sparse: If True, gradients for embeddings will be sparse
        """
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.mode = mode.lower()
        
        # Input embeddings (target words in skip-gram, context in CBOW)
        self.in_embeddings = nn.Embedding(
            vocab_size, embedding_dim, padding_idx=padding_idx, sparse=sparse
        )
        
        # Output embeddings (context words in skip-gram, target in CBOW)
        self.out_embeddings = nn.Embedding(
            vocab_size, embedding_dim, padding_idx=padding_idx, sparse=sparse
        )
        
        # Initialize embeddings
        self._init_weights()
    
    def _init_weights(self):
        """Initialize embeddings using uniform distribution as in the paper"""
        initrange = 0.5 / self.embedding_dim
        self.in_embeddings.weight.data.uniform_(-initrange, initrange)
        self.out_embeddings.weight.data.uniform_(-initrange, initrange)
    
    def forward_skipgram(self, target_idx, context_idx, neg_samples):
        """Forward pass for Skip-gram architecture"""
        # Get embeddings for target word
        target_emb = self.in_embeddings(target_idx)  # [batch_size, embed_dim]
        
        # Get embeddings for positive context word
        context_emb = self.out_embeddings(context_idx)  # [batch_size, embed_dim]
        
        # Get embeddings for negative samples
        neg_emb = self.out_embeddings(neg_samples)  # [batch_size, neg_samples, embed_dim]
        
        # Compute positive score
        pos_score = torch.sum(target_emb * context_emb, dim=1)  # [batch_size]
        pos_score = F.logsigmoid(pos_score)  # [batch_size]
        
        # Compute negative score
        neg_score = torch.bmm(
            neg_emb, target_emb.unsqueeze(2)
        ).squeeze()  # [batch_size, neg_samples]
        neg_score = F.logsigmoid(-neg_score).sum(1)  # [batch_size]
        
        # Loss: maximize positive and minimize negative scores
        loss = -(pos_score + neg_score).mean()
        
        return loss
    
    def forward_cbow(self, context_indices, target_idx, neg_samples):
        """Forward pass for CBOW architecture"""
        # Get embeddings for context words and average them
        context_emb = self.in_embeddings(context_indices)  # [batch_size, context_size, embed_dim]
        context_emb = torch.mean(context_emb, dim=1)  # [batch_size, embed_dim]
        
        # Get embeddings for positive target word
        target_emb = self.out_embeddings(target_idx)  # [batch_size, embed_dim]
        
        # Get embeddings for negative samples
        neg_emb = self.out_embeddings(neg_samples)  # [batch_size, neg_samples, embed_dim]
        
        # Compute positive score
        pos_score = torch.sum(context_emb * target_emb, dim=1)  # [batch_size]
        pos_score = F.logsigmoid(pos_score)  # [batch_size]
        
        # Compute negative score
        neg_score = torch.bmm(
            neg_emb, context_emb.unsqueeze(2)
        ).squeeze()  # [batch_size, neg_samples]
        neg_score = F.logsigmoid(-neg_score).sum(1)  # [batch_size]
        
        # Loss: maximize positive and minimize negative scores
        loss = -(pos_score + neg_score).mean()
        
        return loss
    
    def forward(self, *args):
        """Forward pass selecting the appropriate architecture"""
        if self.mode == 'skipgram':
            return self.forward_skipgram(*args)
        else:  # CBOW
            return self.forward_cbow(*args)
    
    def get_word_vectors(self):
        """Return trained word vectors"""
        return self.in_embeddings.weight.data


class Word2VecTrainer:
    """Trainer for Word2Vec models"""
    
    def __init__(
        self,
        texts: List[List[str]],
        embedding_dim: int = 300,
        window_size: int = 5,
        mode: str = 'skipgram',
        min_count: int = 5,
        negative_samples: int = 5,
        ns_exponent: float = 0.75,
        subsampling_threshold: float = 1e-5,
        epochs: int = 5,
        batch_size: int = 32,
        learning_rate: float = 0.025,
        min_learning_rate: float = 0.0001,
        padding_idx: Optional[int] = None,
        sparse: bool = False
    ):
        """
        Initialize Word2Vec trainer
        
        Args:
            texts: List of tokenized texts
            embedding_dim: Dimension of word embeddings
            window_size: Context window size
            mode: Model architecture ('skipgram' or 'cbow')
            min_count: Minimum word frequency to include in vocabulary
            negative_samples: Number of negative samples per positive sample
            ns_exponent: Exponent for negative sampling distribution
            subsampling_threshold: Threshold for subsampling frequent words
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Initial learning rate
            min_learning_rate: Minimum learning rate
            padding_idx: If specified, padded embeddings will remain zeroed
            sparse: If True, gradients for embeddings will be sparse
        """
        self.texts = texts
        self.embedding_dim = embedding_dim
        self.window_size = window_size
        self.mode = mode.lower()
        self.min_count = min_count
        self.negative_samples = negative_samples
        self.ns_exponent = ns_exponent
        self.subsampling_threshold = subsampling_threshold
        self.epochs = epochs
        self.batch_size = batch_size
        self.initial_lr = learning_rate
        self.min_lr = min_learning_rate
        self.padding_idx = padding_idx
        self.sparse = sparse
        
        # Build vocabulary
        self.word_to_idx = self._build_vocab()
        self.vocab_size = len(self.word_to_idx)
        
        # Create dataset
        self.dataset = Word2VecDataset(
            texts=texts,
            word_to_idx=self.word_to_idx,
            window_size=window_size,
            mode=mode,
            ns_exponent=ns_exponent,
            negative_samples=negative_samples,
            min_count=min_count,
            subsampling_threshold=subsampling_threshold
        )
        
        # Create model
        self.model = Word2Vec(
            vocab_size=self.vocab_size,
            embedding_dim=embedding_dim,
            mode=mode,
            padding_idx=padding_idx,
            sparse=sparse
        )
        
        # Create optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Create dataloader
        self.dataloader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )
    
    def _build_vocab(self) -> Dict[str, int]:
        """Build vocabulary from texts"""
        counter = Counter()
        for text in self.texts:
            counter.update(text)
        
        # Filter words by minimum count
        words = [word for word, count in counter.items() if count >= self.min_count]
        
        # Create word to index mapping
        word_to_idx = {word: i for i, word in enumerate(words)}
        
        logging.info(f"Vocabulary size: {len(word_to_idx)}")
        return word_to_idx
    
    def train(self):
        """Train the Word2Vec model"""
        logging.info(f"Training Word2Vec ({self.mode}) model")
        
        self.model.train()
        
        # Training loop
        total_steps = len(self.dataloader) * self.epochs
        progress_bar = tqdm(total=total_steps, desc="Training")
        
        for epoch in range(self.epochs):
            total_loss = 0
            
            # Adjust learning rate
            lr = max(self.min_lr, self.initial_lr * (1.0 - epoch / self.epochs))
            for param_group in self.optimizer.param_groups:
                param_group['lr'] = lr
            
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
            logging.info(f"Epoch {epoch+1}/{self.epochs}, Loss: {avg_loss:.4f}, LR: {lr:.6f}")
        
        progress_bar.close()
        logging.info("Training complete")
    
    def get_word_vectors(self) -> Dict[str, torch.Tensor]:
        """Get word vectors as a dictionary mapping words to embeddings"""
        self.model.eval()
        vectors = self.model.get_word_vectors()
        
        word_vectors = {}
        for word, idx in self.word_to_idx.items():
            word_vectors[word] = vectors[idx].cpu().numpy()
            
        return word_vectors
    
    def save_vectors(self, file_path: str):
        """Save word vectors in word2vec format"""
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
            'word_to_idx': self.word_to_idx,
            'embedding_dim': self.embedding_dim,
            'mode': self.mode
        }, file_path)
        
        logging.info(f"Model saved to {file_path}")
    
    @classmethod
    def load_model(cls, file_path: str):
        """Load a pre-trained model"""
        checkpoint = torch.load(file_path)
        
        # Initialize an empty trainer
        trainer = cls.__new__(cls)
        
        # Set attributes from checkpoint
        trainer.word_to_idx = checkpoint['word_to_idx']
        trainer.vocab_size = len(trainer.word_to_idx)
        trainer.embedding_dim = checkpoint['embedding_dim']
        trainer.mode = checkpoint['mode']
        
        # Create model and load weights
        trainer.model = Word2Vec(
            vocab_size=trainer.vocab_size,
            embedding_dim=trainer.embedding_dim,
            mode=trainer.mode
        )
        trainer.model.load_state_dict(checkpoint['model_state_dict'])
        
        return trainer


def train_word2vec(
    texts: List[List[str]],
    embedding_dim: int = 300,
    window_size: int = 5,
    mode: str = 'skipgram',
    min_count: int = 5,
    negative_samples: int = 5,
    epochs: int = 5,
    batch_size: int = 32,
    learning_rate: float = 0.025,
    save_path: Optional[str] = None
) -> Word2VecTrainer:
    """
    Train a Word2Vec model and return the trainer
    
    Args:
        texts: List of tokenized texts
        embedding_dim: Dimension of word embeddings
        window_size: Context window size
        mode: Model architecture ('skipgram' or 'cbow')
        min_count: Minimum word frequency to include in vocabulary
        negative_samples: Number of negative samples per positive sample
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Initial learning rate
        save_path: If provided, save the trained model to this path
        
    Returns:
        Trained Word2VecTrainer instance
    """
    trainer = Word2VecTrainer(
        texts=texts,
        embedding_dim=embedding_dim,
        window_size=window_size,
        mode=mode,
        min_count=min_count,
        negative_samples=negative_samples,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    
    trainer.train()
    
    if save_path:
        trainer.save_model(save_path)
    
    return trainer
