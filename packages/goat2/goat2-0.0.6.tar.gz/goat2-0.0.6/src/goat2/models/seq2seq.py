"""
Sequence-to-Sequence model with BiLSTM encoder and attention mechanism
for tasks like machine translation, text summarization, etc.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from typing import Tuple, List, Dict, Optional, Union

class Encoder(nn.Module):
    """Bidirectional LSTM encoder for sequence-to-sequence tasks."""
    
    def __init__(
        self, 
        input_dim: int, 
        emb_dim: int, 
        hidden_dim: int, 
        n_layers: int, 
        dropout: float
    ):
        """
        Initialize the encoder.
        
        Args:
            input_dim: Size of the input vocabulary
            emb_dim: Dimension of embeddings
            hidden_dim: Dimension of hidden states
            n_layers: Number of LSTM layers
            dropout: Dropout probability
        """
        super().__init__()
        
        self.embedding = nn.Embedding(input_dim, emb_dim)
        self.rnn = nn.LSTM(
            emb_dim, 
            hidden_dim, 
            num_layers=n_layers, 
            bidirectional=True, 
            dropout=dropout if n_layers > 1 else 0
        )
        self.dropout = nn.Dropout(dropout)
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        
    def forward(
        self, 
        src: torch.Tensor, 
        src_lengths: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass of the encoder.
        
        Args:
            src: Source sequence [seq_len, batch_size]
            src_lengths: Length of each sequence in the batch (for packing)
            
        Returns:
            encoder_outputs: All hidden states [seq_len, batch_size, hidden_dim * 2]
            (hidden, cell): Final hidden and cell states 
                           [n_layers * 2, batch_size, hidden_dim]
        """
        # Embed tokens
        embedded = self.dropout(self.embedding(src))
        
        # Use packed sequences for variable length inputs
        if src_lengths is not None:
            packed_embedded = nn.utils.rnn.pack_padded_sequence(
                embedded, src_lengths.cpu(), enforce_sorted=False
            )
            packed_outputs, (hidden, cell) = self.rnn(packed_embedded)
            encoder_outputs, _ = nn.utils.rnn.pad_packed_sequence(packed_outputs)
        else:
            encoder_outputs, (hidden, cell) = self.rnn(embedded)
        
        # Combine the forward and backward final hidden states
        hidden_forward = hidden[::2]
        hidden_backward = hidden[1::2]
        hidden = torch.cat([hidden_forward, hidden_backward], dim=2)
        
        # Same for cell state
        cell_forward = cell[::2]
        cell_backward = cell[1::2]
        cell = torch.cat([cell_forward, cell_backward], dim=2)
        
        return encoder_outputs, (hidden, cell)


class Attention(nn.Module):
    """Attention mechanism for focusing on relevant parts of the input sequence."""
    
    def __init__(
        self, 
        enc_hidden_dim: int, 
        dec_hidden_dim: int,
        attn_dim: int
    ):
        """
        Initialize the attention mechanism.
        
        Args:
            enc_hidden_dim: Dimension of encoder hidden states
            dec_hidden_dim: Dimension of decoder hidden states
            attn_dim: Dimension of attention weights
        """
        super().__init__()
        
        self.attn = nn.Linear((enc_hidden_dim * 2) + dec_hidden_dim, attn_dim)
        self.v = nn.Linear(attn_dim, 1, bias=False)
        
    def forward(
        self, 
        hidden: torch.Tensor, 
        encoder_outputs: torch.Tensor, 
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass of the attention mechanism.
        
        Args:
            hidden: Current decoder hidden state [batch_size, dec_hidden_dim]
            encoder_outputs: All encoder hidden states [src_len, batch_size, enc_hidden_dim * 2]
            mask: Mask to avoid attending to padding tokens [batch_size, src_len]
            
        Returns:
            attention: Attention weights [batch_size, src_len]
        """
        src_len = encoder_outputs.shape[0]
        batch_size = encoder_outputs.shape[1]
        
        # Repeat the hidden state src_len times
        hidden = hidden.unsqueeze(1).repeat(1, src_len, 1)
        
        # Transpose encoder outputs to align with hidden
        encoder_outputs = encoder_outputs.permute(1, 0, 2)
        
        # Concatenate hidden state and encoder outputs
        energy = torch.tanh(
            self.attn(torch.cat((hidden, encoder_outputs), dim=2))
        )
        
        # Get attention score for each position
        attention = self.v(energy).squeeze(2)
        
        # Mask out padding positions
        if mask is not None:
            attention = attention.masked_fill(mask == 0, -1e10)
        
        # Softmax to get attention weights
        attention = F.softmax(attention, dim=1)
        
        return attention


class Decoder(nn.Module):
    """LSTM decoder with attention for sequence-to-sequence tasks."""
    
    def __init__(
        self, 
        output_dim: int, 
        emb_dim: int, 
        enc_hidden_dim: int,
        dec_hidden_dim: int, 
        attn_dim: int,
        n_layers: int, 
        dropout: float
    ):
        """
        Initialize the decoder.
        
        Args:
            output_dim: Size of the output vocabulary
            emb_dim: Dimension of embeddings
            enc_hidden_dim: Dimension of encoder hidden states
            dec_hidden_dim: Dimension of decoder hidden states
            attn_dim: Dimension of attention weights
            n_layers: Number of LSTM layers
            dropout: Dropout probability
        """
        super().__init__()
        
        self.output_dim = output_dim
        self.attention = Attention(enc_hidden_dim, dec_hidden_dim, attn_dim)
        
        self.embedding = nn.Embedding(output_dim, emb_dim)
        self.rnn = nn.LSTM(
            emb_dim + (enc_hidden_dim * 2), 
            dec_hidden_dim, 
            num_layers=n_layers, 
            dropout=dropout if n_layers > 1 else 0
        )
        self.fc_out = nn.Linear((enc_hidden_dim * 2) + dec_hidden_dim + emb_dim, output_dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(
        self, 
        input: torch.Tensor, 
        hidden: Tuple[torch.Tensor, torch.Tensor], 
        encoder_outputs: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        """
        Forward pass of the decoder for a single time step.
        
        Args:
            input: Current input token [batch_size]
            hidden: Current hidden and cell states ([layers, batch_size, dec_hidden_dim], [...])
            encoder_outputs: All encoder hidden states [src_len, batch_size, enc_hidden_dim * 2]
            mask: Mask to avoid attending to padding tokens [batch_size, src_len]
            
        Returns:
            prediction: Prediction for current time step [batch_size, output_dim]
            hidden: Updated hidden and cell states
            attention: Attention weights [batch_size, src_len]
        """
        input = input.unsqueeze(0)
        
        # Embed token
        embedded = self.dropout(self.embedding(input))
        
        # Calculate attention weights
        attn_weights = self.attention(hidden[0][-1], encoder_outputs, mask)
        
        # Reshape attention weights and encoder outputs for bmm
        attn_weights = attn_weights.unsqueeze(1)
        encoder_outputs = encoder_outputs.permute(1, 0, 2)
        
        # Calculate context vector using attention weights
        context = torch.bmm(attn_weights, encoder_outputs)
        context = context.permute(1, 0, 2)
        
        # Concatenate embedding and context vector as input to RNN
        rnn_input = torch.cat((embedded, context), dim=2)
        
        # Pass through RNN
        output, hidden = self.rnn(rnn_input, hidden)
        
        # Reshape for concatenation
        output = output.squeeze(0)
        embedded = embedded.squeeze(0)
        context = context.squeeze(0)
        
        # Make prediction
        prediction = self.fc_out(torch.cat((output, context, embedded), dim=1))
        
        return prediction, hidden, attn_weights.squeeze(1)


class Seq2Seq(nn.Module):
    """Sequence-to-sequence model with attention for various NLP tasks."""
    
    def __init__(
        self, 
        encoder: Encoder, 
        decoder: Decoder, 
        device: torch.device,
        pad_idx: int,
        sos_idx: int,
        eos_idx: int
    ):
        """
        Initialize the sequence-to-sequence model.
        
        Args:
            encoder: Encoder module
            decoder: Decoder module
            device: Device to use (cuda/cpu)
            pad_idx: Padding token index
            sos_idx: Start of sequence token index
            eos_idx: End of sequence token index
        """
        super().__init__()
        
        self.encoder = encoder
        self.decoder = decoder
        self.device = device
        self.pad_idx = pad_idx
        self.sos_idx = sos_idx
        self.eos_idx = eos_idx
        
    def create_mask(self, src: torch.Tensor) -> torch.Tensor:
        """
        Create a mask for the source sequence padding tokens.
        
        Args:
            src: Source sequence [seq_len, batch_size]
            
        Returns:
            mask: Binary mask (1 for token, 0 for pad) [batch_size, seq_len]
        """
        # Create mask where 1 means token and 0 means padding
        mask = (src != self.pad_idx).permute(1, 0)
        return mask
        
    def forward(
        self, 
        src: torch.Tensor, 
        src_lengths: Optional[torch.Tensor], 
        trg: torch.Tensor, 
        teacher_forcing_ratio: float = 0.5
    ) -> torch.Tensor:
        """
        Forward pass of the sequence-to-sequence model.
        
        Args:
            src: Source sequence [seq_len, batch_size]
            src_lengths: Length of each source sequence (for packing)
            trg: Target sequence [seq_len, batch_size]
            teacher_forcing_ratio: Probability of using teacher forcing
            
        Returns:
            outputs: Predictions for each token in target sequence [seq_len, batch_size, output_dim]
        """
        batch_size = trg.shape[1]
        trg_len = trg.shape[0]
        trg_vocab_size = self.decoder.output_dim
        
        # Create tensor to store decoder outputs
        outputs = torch.zeros(trg_len, batch_size, trg_vocab_size).to(self.device)
        
        # Create source mask
        mask = self.create_mask(src)
        
        # Encode the source sequence
        encoder_outputs, hidden = self.encoder(src, src_lengths)
        
        # First input to the decoder is the <sos> token
        input = trg[0, :]
        
        # For each position in the target sequence
        for t in range(1, trg_len):
            # Pass through decoder
            output, hidden, _ = self.decoder(input, hidden, encoder_outputs, mask)
            
            # Store prediction
            outputs[t] = output
            
            # Determine next input: teacher forcing or highest probability
            teacher_force = random.random() < teacher_forcing_ratio
            
            # Get the highest predicted token
            top1 = output.argmax(1)
            
            # Use teacher forcing or own prediction
            input = trg[t] if teacher_force else top1
            
        return outputs
    
    def translate(
        self, 
        src: torch.Tensor, 
        src_lengths: Optional[torch.Tensor] = None, 
        max_len: int = 50
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Generate translations for the source sequence.
        
        Args:
            src: Source sequence [seq_len, batch_size]
            src_lengths: Length of each sequence (for packing)
            max_len: Maximum length of the generated sequence
            
        Returns:
            translations: Generated sequences [max_len, batch_size]
            attention: Attention weights for each position [max_len, batch_size, src_len]
        """
        batch_size = src.shape[1]
        
        # Create source mask
        mask = self.create_mask(src)
        
        # Encode the source sequence
        encoder_outputs, hidden = self.encoder(src, src_lengths)
        
        # First input to the decoder is the <sos> token
        input = torch.full((batch_size,), self.sos_idx, dtype=torch.long).to(self.device)
        
        # Tensors to store translation and attention
        translations = torch.zeros(max_len, batch_size, dtype=torch.long).to(self.device)
        translations[0] = input
        attention_weights = torch.zeros(max_len, batch_size, src.shape[0]).to(self.device)
        
        # For each position in the output sequence
        for t in range(1, max_len):
            # Pass through decoder
            output, hidden, attn = self.decoder(input, hidden, encoder_outputs, mask)
            
            # Store attention weights
            attention_weights[t] = attn
            
            # Get the most likely next token
            pred_token = output.argmax(1)
            
            # Store prediction
            translations[t] = pred_token
            
            # Check if all sequences have reached <eos>
            if (pred_token == self.eos_idx).all():
                break
                
            # Next input is the predicted token
            input = pred_token
            
        return translations, attention_weights


def train_seq2seq(
    model: Seq2Seq,
    iterator: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    clip: float = 1.0,
    teacher_forcing_ratio: float = 0.5
) -> float:
    """
    Train the sequence-to-sequence model for one epoch.
    
    Args:
        model: Seq2Seq model
        iterator: DataLoader with training data
        optimizer: Optimizer for updating weights
        criterion: Loss function
        clip: Gradient clipping value
        teacher_forcing_ratio: Probability of using teacher forcing
        
    Returns:
        epoch_loss: Average loss for the epoch
    """
    model.train()
    epoch_loss = 0
    
    for batch in iterator:
        src, src_lengths = batch.src
        trg = batch.trg
        
        optimizer.zero_grad()
        
        # Forward pass
        output = model(src, src_lengths, trg, teacher_forcing_ratio)
        
        # Get loss, ignoring the <sos> token
        output_dim = output.shape[-1]
        output = output[1:].view(-1, output_dim)
        trg = trg[1:].view(-1)
        
        loss = criterion(output, trg)
        
        # Backward pass
        loss.backward()
        
        # Clip gradients
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
        
        # Update weights
        optimizer.step()
        
        epoch_loss += loss.item()
        
    return epoch_loss / len(iterator)


def evaluate_seq2seq(
    model: Seq2Seq,
    iterator: torch.utils.data.DataLoader,
    criterion: nn.Module
) -> float:
    """
    Evaluate the sequence-to-sequence model.
    
    Args:
        model: Seq2Seq model
        iterator: DataLoader with evaluation data
        criterion: Loss function
        
    Returns:
        epoch_loss: Average loss for the evaluation
    """
    model.eval()
    epoch_loss = 0
    
    with torch.no_grad():
        for batch in iterator:
            src, src_lengths = batch.src
            trg = batch.trg
            
            # Forward pass with 0 teacher forcing
            output = model(src, src_lengths, trg, 0)
            
            # Get loss, ignoring the <sos> token
            output_dim = output.shape[-1]
            output = output[1:].view(-1, output_dim)
            trg = trg[1:].view(-1)
            
            loss = criterion(output, trg)
            epoch_loss += loss.item()
    
    return epoch_loss / len(iterator)


# Example usage
def example_usage():
    """Example of how to use the Seq2Seq model for machine translation without torchtext."""
    import torch
    from torch.utils.data import Dataset, DataLoader
    import spacy
    import pandas as pd
    import numpy as np
    from collections import Counter
    
    # Set up spaCy tokenizers
    try:
        spacy_de = spacy.load('de_core_news_sm')
        spacy_en = spacy.load('en_core_web_sm')
    except OSError:
        print("Spacy models need to be downloaded first via:")
        print("python -m spacy download de_core_news_sm")
        print("python -m spacy download en_core_web_sm")
        return
    
    def tokenize_de(text):
        return [tok.text for tok in spacy_de.tokenizer(text)]
        
    def tokenize_en(text):
        return [tok.text for tok in spacy_en.tokenizer(text)]
        
    class Vocabulary:
        """Simple vocabulary class to replace torchtext.Field functionality."""
        def __init__(self, freq_threshold=2):
            self.itos = {0: '<pad>', 1: '<sos>', 2: '<eos>', 3: '<unk>'}
            self.stoi = {'<pad>': 0, '<sos>': 1, '<eos>': 2, '<unk>': 3}
            self.freq_threshold = freq_threshold
            
        def __len__(self):
            return len(self.itos)
            
        def build_vocabulary(self, sentence_list):
            frequencies = Counter()
            idx = 4
            
            for sentence in sentence_list:
                for word in sentence:
                    frequencies[word] += 1
                    
            for word, count in frequencies.items():
                if count >= self.freq_threshold:
                    self.stoi[word] = idx
                    self.itos[idx] = word
                    idx += 1
    
    class TranslationDataset(Dataset):
        """Custom dataset for translation data."""
        def __init__(self, src_texts, trg_texts, src_vocab, trg_vocab):
            self.src_texts = src_texts
            self.trg_texts = trg_texts
            self.src_vocab = src_vocab
            self.trg_vocab = trg_vocab
            
        def __len__(self):
            return len(self.src_texts)
            
        def __getitem__(self, index):
            src_text = self.src_texts[index]
            trg_text = self.trg_texts[index]
            
            # Convert tokens to indices
            src_indices = [self.src_vocab.stoi.get(token, self.src_vocab.stoi['<unk>']) 
                           for token in src_text]
            trg_indices = [self.trg_vocab.stoi.get(token, self.trg_vocab.stoi['<unk>']) 
                           for token in trg_text]
            
            # Add <sos> and <eos> tokens
            src_indices = [self.src_vocab.stoi['<sos>']] + src_indices + [self.src_vocab.stoi['<eos>']]
            trg_indices = [self.trg_vocab.stoi['<sos>']] + trg_indices + [self.trg_vocab.stoi['<eos>']]
            
            return {
                'src': src_indices,
                'trg': trg_indices,
                'src_len': len(src_indices)
            }
    
    def collate_fn(batch):
        """Custom collate function for variable length sequences."""
        # Sort batch by source sequence length in descending order
        batch = sorted(batch, key=lambda x: x['src_len'], reverse=True)
        
        # Get lengths
        src_lengths = torch.tensor([item['src_len'] for item in batch])
        
        # Pad sequences
        max_src_len = max(item['src_len'] for item in batch)
        max_trg_len = max(len(item['trg']) for item in batch)
        
        # Create padded tensors
        padded_src = torch.full((max_src_len, len(batch)), src_vocab.stoi['<pad>'], dtype=torch.long)
        padded_trg = torch.full((max_trg_len, len(batch)), trg_vocab.stoi['<pad>'], dtype=torch.long)
        
        # Fill in the data
        for i, item in enumerate(batch):
            src = torch.tensor(item['src'])
            trg = torch.tensor(item['trg'])
            
            padded_src[:src.size(0), i] = src
            padded_trg[:trg.size(0), i] = trg
            
        return padded_src, src_lengths, padded_trg
    
    # Load and preprocess data
    # Replace with your actual data loading code
    try:
        # This is a simplified example - replace with your actual data
        df_train = pd.read_csv('path/to/data/train.csv')
        df_valid = pd.read_csv('path/to/data/valid.csv')
        df_test = pd.read_csv('path/to/data/test.csv')
    except FileNotFoundError:
        print("Example data files not found. Creating dummy data for demonstration.")
        # Create dummy data for demonstration
        src_examples = [
            "Ein kleines Mädchen steht vor einem Gebäude.",
            "Der Mann geht zur Arbeit.",
            "Ich liebe Programmierung."
        ]
        trg_examples = [
            "A little girl stands in front of a building.",
            "The man goes to work.",
            "I love programming."
        ]
        
        # Create dataframes with dummy data
        df_train = pd.DataFrame({'src': src_examples, 'trg': trg_examples})
        df_valid = df_train.copy()  # Use same data for demo
        df_test = df_train.copy()  # Use same data for demo
    
    # Tokenize data
    train_src_tokenized = [tokenize_de(text) for text in df_train['src']]
    train_trg_tokenized = [tokenize_en(text) for text in df_train['trg']]
    valid_src_tokenized = [tokenize_de(text) for text in df_valid['src']]
    valid_trg_tokenized = [tokenize_en(text) for text in df_valid['trg']]
    test_src_tokenized = [tokenize_de(text) for text in df_test['src']]
    test_trg_tokenized = [tokenize_en(text) for text in df_test['trg']]
    
    # Build vocabularies
    src_vocab = Vocabulary()
    trg_vocab = Vocabulary()
    src_vocab.build_vocabulary(train_src_tokenized)
    trg_vocab.build_vocabulary(train_trg_tokenized)
    
    # Create datasets
    train_dataset = TranslationDataset(train_src_tokenized, train_trg_tokenized, src_vocab, trg_vocab)
    valid_dataset = TranslationDataset(valid_src_tokenized, valid_trg_tokenized, src_vocab, trg_vocab)
    test_dataset = TranslationDataset(test_src_tokenized, test_trg_tokenized, src_vocab, trg_vocab)
    
    # Create data loaders
    BATCH_SIZE = 64
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    train_iterator = DataLoader(
        train_dataset, 
        batch_size=BATCH_SIZE, 
        collate_fn=collate_fn, 
        shuffle=True
    )
    valid_iterator = DataLoader(
        valid_dataset, 
        batch_size=BATCH_SIZE, 
        collate_fn=collate_fn
    )
    test_iterator = DataLoader(
        test_dataset, 
        batch_size=BATCH_SIZE, 
        collate_fn=collate_fn
    )
    
    # Define model hyperparameters
    INPUT_DIM = len(src_vocab)
    OUTPUT_DIM = len(trg_vocab)
    ENC_EMB_DIM = 256
    DEC_EMB_DIM = 256
    ENC_HIDDEN_DIM = 512
    DEC_HIDDEN_DIM = 512
    ATTN_DIM = 64
    ENC_LAYERS = 2
    DEC_LAYERS = 2
    ENC_DROPOUT = 0.5
    DEC_DROPOUT = 0.5
    PAD_IDX = src_vocab.stoi['<pad>']
    SOS_IDX = trg_vocab.stoi['<sos>']
    EOS_IDX = trg_vocab.stoi['<eos>']
    
    # Create model components
    encoder = Encoder(INPUT_DIM, ENC_EMB_DIM, ENC_HIDDEN_DIM, ENC_LAYERS, ENC_DROPOUT)
    decoder = Decoder(OUTPUT_DIM, DEC_EMB_DIM, ENC_HIDDEN_DIM, DEC_HIDDEN_DIM, ATTN_DIM, DEC_LAYERS, DEC_DROPOUT)
    model = Seq2Seq(encoder, decoder, device, PAD_IDX, SOS_IDX, EOS_IDX).to(device)
    
    # Initialize weights
    def init_weights(m):
        for name, param in m.named_parameters():
            if 'weight' in name:
                nn.init.normal_(param.data, mean=0, std=0.01)
            else:
                nn.init.constant_(param.data, 0)
    
    model.apply(init_weights)
    
    # Define optimizer and loss
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss(ignore_index=PAD_IDX)
    
    # Train model
    N_EPOCHS = 10
    CLIP = 1.0
    
    best_valid_loss = float('inf')
    
    for epoch in range(N_EPOCHS):
        train_loss = train_seq2seq(model, train_iterator, optimizer, criterion, CLIP)
        valid_loss = evaluate_seq2seq(model, valid_iterator, criterion)
        
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            torch.save(model.state_dict(), 'seq2seq-model.pt')
        
        print(f'Epoch: {epoch+1}')
        print(f'\tTrain Loss: {train_loss:.3f}')
        print(f'\tValid Loss: {valid_loss:.3f}')
    
    # Example function to translate a sentence
    def translate_sentence(sentence, src_vocab, trg_vocab, model, device, max_len=50):
        model.eval()
        
        # Tokenize the source sentence if it's a string
        if isinstance(sentence, str):
            tokens = tokenize_de(sentence)
        else:
            tokens = sentence
            
        # Convert to indices
        src_indices = [src_vocab.stoi.get(token, src_vocab.stoi['<unk>']) for token in tokens]
        
        # Add <sos> and <eos> tokens
        src_indices = [src_vocab.stoi['<sos>']] + src_indices + [src_vocab.stoi['<eos>']]
        
        # Convert to tensor
        src_tensor = torch.LongTensor(src_indices).unsqueeze(1).to(device)
        src_lengths = torch.LongTensor([len(src_indices)]).to(device)
        
        # Generate translation
        with torch.no_grad():
            translations, attention = model.translate(src_tensor, src_lengths, max_len)
        
        # Convert indices to tokens
        trg_tokens = [trg_vocab.itos[idx] for idx in translations[:, 0]]
        
        # Remove <sos> and find position of <eos>
        try:
            eos_pos = trg_tokens.index(trg_vocab.itos[EOS_IDX])
            trg_tokens = trg_tokens[1:eos_pos]
        except ValueError:
            trg_tokens = trg_tokens[1:]
            
        return trg_tokens, attention
    
    # Test with an example sentence
    test_sentence = "Ein kleines Mädchen steht vor einem Gebäude."
    translation, attention = translate_sentence(test_sentence, src_vocab, trg_vocab, model, device)
    print(f'Source: {test_sentence}')
    print(f'Translation: {" ".join(translation)}')


if __name__ == "__main__":
    # Uncomment to run the example
    # example_usage()
    pass
