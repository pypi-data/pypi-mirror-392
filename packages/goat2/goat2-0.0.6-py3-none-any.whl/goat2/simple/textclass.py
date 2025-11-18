import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from collections import Counter
import re

class TextDataset(Dataset):
    def __init__(self, texts, labels, vocab=None, max_length=100):
        self.texts = texts
        self.labels = labels
        self.max_length = max_length
        
        # Build vocabulary if not provided
        if vocab is None:
            self.build_vocab()
        else:
            self.vocab = vocab
            
    def build_vocab(self):
        # Tokenize all texts
        all_tokens = []
        for text in self.texts:
            all_tokens.extend(self.tokenize(text))
            
        # Count token frequencies
        counter = Counter(all_tokens)
        vocab_tokens = ["<PAD>", "<UNK>"] + [token for token, _ in counter.most_common(5000)]
        
        # Create vocabulary mapping
        self.vocab = {token: idx for idx, token in enumerate(vocab_tokens)}
        
    def tokenize(self, text):
        # Simple tokenization
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.split()
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Tokenize and convert to indices
        tokens = self.tokenize(text)
        token_ids = [self.vocab.get(token, 1) for token in tokens]  # 1 is <UNK>
        
        # Truncate or pad to max_length
        if len(token_ids) > self.max_length:
            token_ids = token_ids[:self.max_length]
        else:
            token_ids = token_ids + [0] * (self.max_length - len(token_ids))  # 0 is <PAD>
            
        return torch.tensor(token_ids), torch.tensor(label)

class BiLSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim):
        super(BiLSTMClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, text):
        # text: [batch_size, seq_len]
        embedded = self.dropout(self.embedding(text))  # [batch_size, seq_len, emb_dim]
        
        # Pass through LSTM
        output, (hidden, _) = self.lstm(embedded)
        # hidden: [2, batch_size, hidden_dim]
        
        # Concat the final forward and backward hidden states
        hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        # hidden: [batch_size, hidden_dim*2]
        
        return self.fc(self.dropout(hidden))

def train(model, train_loader, epochs=5):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for texts, labels in train_loader:
            texts, labels = texts.to(device), labels.to(device)
            
            optimizer.zero_grad()
            predictions = model(texts)
            loss = criterion(predictions, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f'Epoch {epoch+1}, Loss: {total_loss/len(train_loader):.4f}')

def evaluate(model, test_loader):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()
    
    correct = 0
    total = 0
    
    with torch.no_grad():
        for texts, labels in test_loader:
            texts, labels = texts.to(device), labels.to(device)
            predictions = model(texts)
            _, predicted = torch.max(predictions, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = correct / total
    print(f'Test Accuracy: {accuracy * 100:.2f}%')
    return accuracy

def generate_data():
    # Generate sample text data for demonstration
    texts = [
        "this movie was great and entertaining",
        "really enjoyed the storyline",
        "terrible acting and boring plot",
        "waste of time and money",
        "best film I have seen this year",
        # Add more examples...
    ]
    labels = [1, 1, 0, 0, 1]  # 1: positive, 0: negative
    
    # Split into train/test
    train_texts = texts[:4]
    train_labels = labels[:4]
    test_texts = texts[4:]
    test_labels = labels[4:]
    
    return train_texts, train_labels, test_texts, test_labels

def main():
    # In a real scenario, you would load your dataset
    train_texts, train_labels, test_texts, test_labels = generate_data()
    
    # Create datasets
    train_dataset = TextDataset(train_texts, train_labels)
    test_dataset = TextDataset(test_texts, test_labels, vocab=train_dataset.vocab)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=2)
    
    # Initialize model
    vocab_size = len(train_dataset.vocab)
    embedding_dim = 100
    hidden_dim = 128
    output_dim = 2  # Binary classification
    
    model = BiLSTMClassifier(vocab_size, embedding_dim, hidden_dim, output_dim)
    
    # Train and evaluate
    train(model, train_loader, epochs=5)
    evaluate(model, test_loader)

if __name__ == '__main__':
    main()
