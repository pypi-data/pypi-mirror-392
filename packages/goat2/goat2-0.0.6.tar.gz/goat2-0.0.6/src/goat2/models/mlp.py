"""
Multi-Layer Perceptron implementation for classification and regression tasks.

This module provides a flexible MLP implementation with configurable architecture
and a trainer class to simplify training, evaluation, and inference.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from typing import List, Dict, Optional, Union, Tuple
import logging
from tqdm import tqdm

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


class MLP(nn.Module):
    """
    Multi-Layer Perceptron with configurable architecture and features.
    
    Supports both classification and regression tasks with various activation
    functions, dropout, batch normalization, and customizable layer sizes.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        output_dim: int,
        activation: str = 'relu',
        dropout: float = 0.0,
        batch_norm: bool = False,
        output_activation: Optional[str] = None,
        bias: bool = True
    ) -> None:
        """
        Initialize the MLP model.
        
        Args:
            input_dim: Dimension of input features
            hidden_dims: List of hidden layer dimensions
            output_dim: Dimension of output (1 for regression, num_classes for classification)
            activation: Activation function ('relu', 'leaky_relu', 'tanh', 'sigmoid', 'elu')
            dropout: Dropout probability (0.0 means no dropout)
            batch_norm: Whether to use batch normalization
            output_activation: Activation for output layer (None, 'sigmoid', 'softmax', 'tanh')
            bias: Whether to include bias terms in linear layers
        """
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        self.activation_name = activation
        self.output_activation_name = output_activation
        self.dropout_prob = dropout
        self.use_batch_norm = batch_norm
        
        # Set up activation function
        self.activation = self._get_activation(activation)
        
        # Build layers
        layers = []
        prev_dim = input_dim
        
        for i, hidden_dim in enumerate(hidden_dims):
            # Add linear layer
            layers.append(nn.Linear(prev_dim, hidden_dim, bias=bias))
            
            # Add batch normalization if requested
            if batch_norm:
                layers.append(nn.BatchNorm1d(hidden_dim))
                
            # Add activation
            layers.append(self.activation)
            
            # Add dropout if requested
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
                
            prev_dim = hidden_dim
        
        # Add output layer
        self.hidden_layers = nn.Sequential(*layers)
        self.output_layer = nn.Linear(prev_dim, output_dim, bias=bias)
        
        # Initialize weights
        self._init_weights()
        
    def _get_activation(self, activation_name: str) -> nn.Module:
        """Get activation function module from name."""
        activation_name = activation_name.lower()
        
        if activation_name == 'relu':
            return nn.ReLU(inplace=True)
        elif activation_name == 'leaky_relu':
            return nn.LeakyReLU(inplace=True)
        elif activation_name == 'tanh':
            return nn.Tanh()
        elif activation_name == 'sigmoid':
            return nn.Sigmoid()
        elif activation_name == 'elu':
            return nn.ELU(inplace=True)
        else:
            raise ValueError(f"Unsupported activation function: {activation_name}")
    
    def _init_weights(self) -> None:
        """Initialize model weights for better performance."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                # Use Kaiming/He initialization for ReLU-based networks
                if self.activation_name.endswith('relu'):
                    nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')
                else:
                    nn.init.xavier_uniform_(m.weight)
                
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the MLP.
        
        Args:
            x: Input tensor [batch_size, input_dim]
            
        Returns:
            Output tensor [batch_size, output_dim]
        """
        # Pass through hidden layers
        x = self.hidden_layers(x)
        
        # Pass through output layer
        x = self.output_layer(x)
        
        # Apply output activation if specified
        if self.output_activation_name:
            if self.output_activation_name == 'sigmoid':
                x = torch.sigmoid(x)
            elif self.output_activation_name == 'softmax':
                x = F.softmax(x, dim=1)
            elif self.output_activation_name == 'tanh':
                x = torch.tanh(x)
                
        return x
    
    def predict(self, x: Union[torch.Tensor, np.ndarray]) -> np.ndarray:
        """
        Make predictions on input data.
        
        Args:
            x: Input data (torch.Tensor or numpy array)
            
        Returns:
            Numpy array of predictions
        """
        self.eval()
        with torch.no_grad():
            if isinstance(x, np.ndarray):
                x = torch.FloatTensor(x)
            
            if self.output_activation_name == 'softmax':
                # For classification, return class with highest probability
                out = self.forward(x)
                _, predicted = torch.max(out, 1)
                return predicted.cpu().numpy()
            else:
                # For regression or binary classification
                return self.forward(x).cpu().numpy()


class MLPTrainer:
    """Handler for training and using an MLP model."""
    
    def __init__(
        self,
        model: MLP,
        criterion: Optional[nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        learning_rate: float = 0.001,
        device: Optional[torch.device] = None,
        task: str = 'classification'
    ) -> None:
        """
        Initialize the MLP trainer.
        
        Args:
            model: MLP model to train
            criterion: Loss function (if None, will be set based on task)
            optimizer: Optimizer (if None, Adam will be used)
            learning_rate: Learning rate for optimizer (if optimizer is None)
            device: Device to use for training (will use CUDA if available if None)
            task: Task type ('classification' or 'regression')
        """
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        self.model = model.to(self.device)
        self.task = task.lower()
        
        # Set default criterion if not provided
        if criterion is None:
            if self.task == 'classification':
                if model.output_dim == 1 or model.output_activation_name == 'sigmoid':
                    # Binary classification
                    self.criterion = nn.BCEWithLogitsLoss() if model.output_activation_name is None else nn.BCELoss()
                else:
                    # Multi-class classification
                    self.criterion = nn.CrossEntropyLoss()
            else:
                # Regression
                self.criterion = nn.MSELoss()
        else:
            self.criterion = criterion
            
        # Set default optimizer if not provided
        if optimizer is None:
            self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        else:
            self.optimizer = optimizer
            
        # Initialize training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'metrics': {}
        }
    
    def eval(
        self, 
        data_loader: DataLoader,
        max_samples: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Evaluate the model on provided data.
        
        Args:
            data_loader: DataLoader containing evaluation data
            max_samples: Maximum number of samples to evaluate (None for all)
            
        Returns:
            Dictionary with evaluation metrics
        """
        self.model.eval()
        total_loss = 0
        all_targets = []
        all_outputs = []
        total_samples = 0
        
        with torch.no_grad():
            for batch in data_loader:
                # Get data
                if len(batch) == 2:
                    inputs, targets = batch
                else:
                    inputs, targets = batch[0], batch[1]
                    
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                # Check if we've reached max samples
                batch_size = inputs.size(0)
                if max_samples is not None and total_samples + batch_size > max_samples:
                    # Take only what we need to reach max_samples
                    inputs = inputs[:max_samples - total_samples]
                    targets = targets[:max_samples - total_samples]
                    
                # Forward pass
                outputs = self.model(inputs)
                
                # Handle target shape for BCE loss
                if isinstance(self.criterion, nn.BCEWithLogitsLoss) or isinstance(self.criterion, nn.BCELoss):
                    if targets.dim() == 1:
                        targets = targets.unsqueeze(1)
                    
                    if outputs.shape != targets.shape:
                        outputs = outputs.view(targets.shape)
                
                # Compute loss
                loss = self.criterion(outputs, targets)
                total_loss += loss.item() * inputs.size(0)
                
                # Store outputs and targets for metrics
                all_targets.append(targets.cpu())
                all_outputs.append(outputs.cpu())
                
                # Update total samples count
                total_samples += inputs.size(0)
                
                # Break if we've reached max samples
                if max_samples is not None and total_samples >= max_samples:
                    break
        
        # Calculate average loss
        avg_loss = total_loss / total_samples
        
        # Combine batches
        all_targets = torch.cat(all_targets, dim=0)
        all_outputs = torch.cat(all_outputs, dim=0)
        
        # Calculate metrics
        metrics = {'loss': avg_loss}
        
        if self.task == 'classification':
            # For binary classification
            if all_outputs.shape[1] == 1 or (len(all_outputs.shape) == 1):
                # Apply sigmoid if needed
                if not (self.model.output_activation_name == 'sigmoid'):
                    all_outputs = torch.sigmoid(all_outputs)
                
                # Binarize outputs with threshold of 0.5
                predicted = (all_outputs > 0.5).float()
                
                # Calculate accuracy
                metrics['accuracy'] = (predicted == all_targets).float().mean().item()
            
            # For multi-class classification
            else:
                # Get predicted class
                _, predicted = torch.max(all_outputs, 1)
                
                if all_targets.dim() > 1:
                    _, all_targets = torch.max(all_targets, 1)
                
                # Calculate accuracy
                metrics['accuracy'] = (predicted == all_targets).float().mean().item()
        
        # For regression tasks
        else:
            metrics['mse'] = F.mse_loss(all_outputs, all_targets).item()
            metrics['mae'] = F.l1_loss(all_outputs, all_targets).item()
        
        return metrics
    
    def train(
        self, 
        train_loader: DataLoader, 
        val_loader: Optional[DataLoader] = None,
        epochs: int = 100,
        patience: Optional[int] = 10,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
        save_path: Optional[str] = None,
        verbose: bool = True,
        val_max_samples: Optional[int] = None
    ) -> Dict[str, List[float]]:
        """
        Train the model for multiple epochs.
        
        Args:
            train_loader: DataLoader for training data
            val_loader: DataLoader for validation data (if None, no validation)
            epochs: Number of epochs to train
            patience: Number of epochs to wait before early stopping (if None, no early stopping)
            scheduler: Learning rate scheduler
            save_path: Path to save the best model
            verbose: Whether to print progress
            val_max_samples: Maximum number of samples to use for validation
            
        Returns:
            Training history dictionary
        """
        best_val_loss = float('inf')
        no_improve_count = 0
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0
            total_samples = 0
            
            for batch in train_loader:
                # Get data
                if len(batch) == 2:
                    inputs, targets = batch
                else:
                    inputs, targets = batch[0], batch[1]
                    
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                
                # Forward pass
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                
                # Handle target shape for BCE loss
                if isinstance(self.criterion, nn.BCEWithLogitsLoss) or isinstance(self.criterion, nn.BCELoss):
                    if targets.dim() == 1:
                        targets = targets.unsqueeze(1)
                    
                    if outputs.shape != targets.shape:
                        outputs = outputs.view(targets.shape)
                
                # Compute loss
                loss = self.criterion(outputs, targets)
                
                # Backward pass and optimize
                loss.backward()
                self.optimizer.step()
                
                train_loss += loss.item() * inputs.size(0)
                total_samples += inputs.size(0)
            
            # Calculate average loss
            train_loss /= total_samples
            self.history['train_loss'].append(train_loss)
            
            # Validate if validation data is provided
            if val_loader is not None:
                metrics = self.eval(val_loader, max_samples=val_max_samples)
                val_loss = metrics['loss']
                self.history['val_loss'].append(val_loss)
                
                # Store other metrics
                for metric, value in metrics.items():
                    if metric != 'loss':
                        if metric not in self.history['metrics']:
                            self.history['metrics'][metric] = []
                        self.history['metrics'][metric].append(value)
                        
                # Print progress
                if verbose:
                    metric_str = ', '.join([f"{k}: {v:.4f}" for k, v in metrics.items() if k != 'loss'])
                    logging.info(f"Epoch {epoch+1}/{epochs} - train_loss: {train_loss:.4f}, val_loss: {val_loss:.4f}, {metric_str}")
                
                # Check for improvement
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    no_improve_count = 0
                    
                    # Save best model
                    if save_path:
                        torch.save({
                            'model_state_dict': self.model.state_dict(),
                            'optimizer_state_dict': self.optimizer.state_dict(),
                        }, save_path)
                else:
                    no_improve_count += 1
                    
                # Early stopping
                if patience is not None and no_improve_count >= patience:
                    if verbose:
                        logging.info(f"Early stopping at epoch {epoch+1}")
                    break
            else:
                # Print progress without validation
                if verbose:
                    logging.info(f"Epoch {epoch+1}/{epochs} - train_loss: {train_loss:.4f}")
            
            # Update learning rate if scheduler is provided
            if scheduler is not None:
                if isinstance(scheduler, (optim.lr_scheduler.ReduceLROnPlateau)):
                    scheduler.step(val_loss if val_loader is not None else train_loss)
                else:
                    scheduler.step()
        
        # Load best model if saved
        if save_path and val_loader is not None:
            checkpoint = torch.load(save_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            
        return self.history
    
    def predict(
        self, 
        X: Union[torch.Tensor, np.ndarray]
    ) -> np.ndarray:
        """
        Make predictions using the trained model.
        
        Args:
            X: Input data
            
        Returns:
            Numpy array of predictions
        """
        return self.model.predict(X)


# Example usage
if __name__ == "__main__":
    # Example: Binary classification with a small synthetic dataset
    import numpy as np
    from torch.utils.data import TensorDataset, DataLoader
    
    # Generate synthetic data
    np.random.seed(42)
    X = np.random.randn(1000, 10)  # 1000 samples, 10 features
    y = (X[:, 0] * X[:, 1] > 0).astype(float)  # Binary target
    
    # Convert to PyTorch tensors
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.FloatTensor(y).unsqueeze(1)  # Shape [n_samples, 1] for binary classification
    
    # Create dataset and dataloader
    dataset = TensorDataset(X_tensor, y_tensor)
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Create model
    model = MLP(
        input_dim=10,
        hidden_dims=[32, 16],
        output_dim=1,  # Binary classification
        activation='relu',
        dropout=0.2,
        batch_norm=True,
        output_activation='sigmoid'  # Use sigmoid for binary classification
    )
    
    # Create trainer and train model
    trainer = MLPTrainer(
        model=model,
        task='classification',
        learning_rate=0.001
    )
    
    # Train model
    trainer.train(
        train_loader=train_loader,
        val_loader=test_loader,  # Using test set as validation for example
        epochs=10,
        patience=3,
        verbose=True,
        val_max_samples=100  # Limit validation to 100 samples
    )
    
    # Evaluate on full test set
    test_metrics = trainer.eval(test_loader)
    print(f"Test metrics: {test_metrics}")
    
    # Make predictions on new data
    X_new = np.random.randn(5, 10)
    predictions = trainer.predict(X_new)
    print(f"Predictions for 5 new samples:\n{predictions}")
