"""
Training and evaluation utilities for PyTorch models.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import _LRScheduler
import numpy as np
import time
import logging
from typing import Dict, List, Optional, Union, Callable, Tuple, Any
from tqdm import tqdm
import copy
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def train(
    model: nn.Module,
    train_loader: DataLoader,
    criterion: Callable,
    optimizer: torch.optim.Optimizer,
    epochs: int = 10,
    val_loader: Optional[DataLoader] = None,
    validate_every: int = 1,
    schedulers: Optional[List[Dict[str, Any]]] = None,
    device: Optional[Union[str, torch.device]] = None,
    early_stopping: Optional[Dict[str, Any]] = None,
    checkpoint_dir: Optional[str] = None,
    callbacks: Optional[List[Callable]] = None,
    gradient_clip_val: Optional[float] = None,
    verbose: bool = True,
    metrics: Optional[Dict[str, Callable]] = None
) -> Dict[str, List[float]]:
    """
    Train a PyTorch model with configurable options.
    
    Args:
        model: PyTorch model to train
        train_loader: DataLoader for training data
        criterion: Loss function
        optimizer: Optimizer for parameter updates
        epochs: Number of training epochs
        val_loader: Optional DataLoader for validation data
        validate_every: Run validation every N epochs (if val_loader provided)
        schedulers: List of scheduler configurations, each containing:
                   - 'scheduler': The scheduler instance
                   - 'monitor': Metric to monitor ('loss' or 'val_loss')
                   - 'interval': 'epoch' or 'step'
                   - 'frequency': How often to call scheduler
                   - 'mode': 'min' or 'max' for monitored metrics
        device: Device to use for training ('cuda', 'cpu', or torch.device)
        early_stopping: Dict with early stopping parameters:
                       - 'patience': Number of epochs to wait
                       - 'min_delta': Minimum change to qualify as improvement
                       - 'monitor': Metric to monitor ('loss' or 'val_loss')
                       - 'mode': 'min' or 'max'
        checkpoint_dir: Directory to save checkpoints
        callbacks: List of callbacks to call after each epoch
        gradient_clip_val: Value to clip gradients at
        verbose: Whether to show progress bars
        metrics: Dictionary of metric functions to compute during training
        
    Returns:
        Dictionary containing training history with losses and metrics
    """
    # Set device if not specified
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    elif isinstance(device, str):
        device = torch.device(device)
    
    logger.info(f"Training on {device}")
    model.to(device)
    
    # Initialize history to track metrics
    history = {
        'train_loss': [],
    }
    
    if metrics:
        for metric_name in metrics:
            history[f'train_{metric_name}'] = []
            
            if val_loader is not None:
                history[f'val_{metric_name}'] = []
    
    if val_loader is not None:
        history['val_loss'] = []
    
    # Initialize early stopping if configured
    if early_stopping:
        best_metric = float('inf') if early_stopping.get('mode', 'min') == 'min' else float('-inf')
        patience_counter = 0
        best_model_state = None
    
    # Training loop
    for epoch in range(epochs):
        # Set model to training mode
        model.train()
        
        # Tracking metrics
        running_loss = 0.0
        metric_values = {metric_name: 0.0 for metric_name in metrics} if metrics else {}
        samples_seen = 0
        
        # Progress bar
        train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]", 
                          disable=not verbose)
        
        # Iterate over batches
        for batch_idx, batch in enumerate(train_pbar):
            # Handle different batch formats
            if isinstance(batch, (tuple, list)) and len(batch) >= 2:
                # Assume (inputs, targets) or (inputs, targets, ...)
                inputs, targets = batch[0], batch[1]
            elif isinstance(batch, dict):
                # Assume dictionary with 'input' and 'target' keys
                inputs, targets = batch.get('input', batch.get('inputs')), batch.get('target', batch.get('targets'))
            else:
                raise ValueError(f"Unsupported batch format: {type(batch)}")
            
            # Move data to device
            if isinstance(inputs, (list, tuple)):
                inputs = [x.to(device) if isinstance(x, torch.Tensor) else x for x in inputs]
            else:
                inputs = inputs.to(device)
                
            if isinstance(targets, (list, tuple)):
                targets = [y.to(device) if isinstance(y, torch.Tensor) else y for y in targets]
            else:
                targets = targets.to(device)
            
            # Zero gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(inputs)
            
            # Compute loss
            loss = criterion(outputs, targets)
            
            # Backward pass and optimize
            loss.backward()
            
            # Apply gradient clipping if specified
            if gradient_clip_val is not None:
                torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_val)
                
            optimizer.step()
            
            # Update metrics
            batch_size = targets.shape[0] if hasattr(targets, 'shape') else len(targets)
            running_loss += loss.item() * batch_size
            samples_seen += batch_size
            
            # Update learning rate if using step-based schedulers
            if schedulers:
                for scheduler_config in schedulers:
                    if scheduler_config.get('interval') == 'step':
                        frequency = scheduler_config.get('frequency', 1)
                        if (batch_idx + 1) % frequency == 0:
                            scheduler_config['scheduler'].step()
            
            # Compute custom metrics
            if metrics:
                with torch.no_grad():
                    for metric_name, metric_fn in metrics.items():
                        metric_values[metric_name] += metric_fn(outputs, targets) * batch_size
            
            # Update progress bar
            train_pbar.set_postfix({
                'loss': running_loss / samples_seen,
                **{name: values / samples_seen for name, values in metric_values.items()}
            })
        
        # Calculate epoch-level metrics
        epoch_loss = running_loss / samples_seen
        history['train_loss'].append(epoch_loss)
        
        if metrics:
            for metric_name in metrics:
                epoch_metric = metric_values[metric_name] / samples_seen
                history[f'train_{metric_name}'].append(epoch_metric)
        
        # Log training metrics
        log_msg = f"Epoch {epoch+1}/{epochs} - train_loss: {epoch_loss:.4f}"
        if metrics:
            log_msg += " - " + " - ".join([
                f"train_{name}: {values / samples_seen:.4f}" 
                for name, values in metric_values.items()
            ])
        logger.info(log_msg)
        
        # Validation phase
        if val_loader is not None and (epoch + 1) % validate_every == 0:
            val_metrics = evaluate(
                model=model,
                data_loader=val_loader,
                criterion=criterion,
                device=device,
                metrics=metrics,
                verbose=verbose,
                prefix="val"
            )
            
            # Log validation metrics
            val_loss = val_metrics['val_loss']
            history['val_loss'].append(val_loss)
            
            log_msg = f"Epoch {epoch+1}/{epochs} - val_loss: {val_loss:.4f}"
            
            if metrics:
                for metric_name in metrics:
                    val_metric = val_metrics[f'val_{metric_name}']
                    if f'val_{metric_name}' not in history:
                        history[f'val_{metric_name}'] = []
                    history[f'val_{metric_name}'].append(val_metric)
                    log_msg += f" - val_{metric_name}: {val_metric:.4f}"
                    
            logger.info(log_msg)
            
            # Early stopping check
            if early_stopping:
                monitor_metric = val_loss if early_stopping.get('monitor', 'val_loss') == 'val_loss' else val_metrics.get(
                    early_stopping.get('monitor'), val_loss)
                
                improvement = False
                
                if early_stopping.get('mode', 'min') == 'min':
                    if monitor_metric <= best_metric - early_stopping.get('min_delta', 0.0):
                        best_metric = monitor_metric
                        improvement = True
                else:
                    if monitor_metric >= best_metric + early_stopping.get('min_delta', 0.0):
                        best_metric = monitor_metric
                        improvement = True
                
                if improvement:
                    patience_counter = 0
                    best_model_state = copy.deepcopy(model.state_dict())
                    
                    # Save checkpoint if directory is specified
                    if checkpoint_dir:
                        os.makedirs(checkpoint_dir, exist_ok=True)
                        torch.save({
                            'epoch': epoch,
                            'model_state_dict': model.state_dict(),
                            'optimizer_state_dict': optimizer.state_dict(),
                            'loss': val_loss,
                            'metrics': val_metrics
                        }, os.path.join(checkpoint_dir, f'best_model.pth'))
                else:
                    patience_counter += 1
                    if patience_counter >= early_stopping.get('patience', 10):
                        logger.info(f"Early stopping triggered after {epoch+1} epochs")
                        # Restore best model
                        if best_model_state is not None:
                            model.load_state_dict(best_model_state)
                        break
        
        # Update learning rate for epoch-based schedulers
        if schedulers:
            for scheduler_config in schedulers:
                if scheduler_config.get('interval', 'epoch') == 'epoch':
                    # Get monitored metric for schedulers that need it
                    if 'monitor' in scheduler_config:
                        if scheduler_config['monitor'] == 'val_loss' and val_loader is not None:
                            monitored_value = history['val_loss'][-1]
                        else:
                            monitored_value = history['train_loss'][-1]
                        
                        # Pass monitored value to scheduler if it supports it
                        scheduler = scheduler_config['scheduler']
                        if hasattr(scheduler, 'step') and 'metrics' in scheduler.step.__code__.co_varnames:
                            scheduler.step(monitored_value)
                        else:
                            scheduler.step()
                    else:
                        scheduler_config['scheduler'].step()
        
        # Execute callbacks if provided
        if callbacks:
            for callback in callbacks:
                callback(model=model, epoch=epoch, history=history)
    
    # Restore best model if early stopping was used
    if early_stopping and best_model_state is not None:
        model.load_state_dict(best_model_state)
        logger.info("Restored best model from early stopping")
        
    return history


def evaluate(
    model: nn.Module,
    data_loader: DataLoader,
    criterion: Callable,
    device: Optional[Union[str, torch.device]] = None,
    num_samples: Optional[int] = None,
    metrics: Optional[Dict[str, Callable]] = None,
    verbose: bool = True,
    prefix: str = "eval"
) -> Dict[str, float]:
    """
    Evaluate a PyTorch model on a dataset.
    
    Args:
        model: PyTorch model to evaluate
        data_loader: DataLoader for evaluation data
        criterion: Loss function
        device: Device to use for evaluation
        num_samples: Maximum number of samples to evaluate (if None, use all)
        metrics: Dictionary of metric functions to compute
        verbose: Whether to show progress bar
        prefix: Prefix for metric names in the output dictionary
        
    Returns:
        Dictionary containing evaluation metrics
    """
    # Set device if not specified
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    elif isinstance(device, str):
        device = torch.device(device)
    
    model.to(device)
    model.eval()
    
    running_loss = 0.0
    metric_values = {metric_name: 0.0 for metric_name in metrics} if metrics else {}
    samples_seen = 0
    
    # Determine how many batches to process
    total_batches = len(data_loader)
    if num_samples is not None:
        # Estimate number of batches based on batch size
        batch_size = data_loader.batch_size or 1
        max_batches = (num_samples + batch_size - 1) // batch_size  # Ceiling division
        total_batches = min(total_batches, max_batches)
    
    # Progress bar
    eval_pbar = tqdm(enumerate(data_loader), total=total_batches, 
                    desc=f"Evaluation [{prefix}]", disable=not verbose)
    
    with torch.no_grad():
        for batch_idx, batch in eval_pbar:
            if num_samples is not None and samples_seen >= num_samples:
                break
                
            # Handle different batch formats
            if isinstance(batch, (tuple, list)) and len(batch) >= 2:
                inputs, targets = batch[0], batch[1]
            elif isinstance(batch, dict):
                inputs, targets = batch.get('input', batch.get('inputs')), batch.get('target', batch.get('targets'))
            else:
                raise ValueError(f"Unsupported batch format: {type(batch)}")
            
            # Move data to device
            if isinstance(inputs, (list, tuple)):
                inputs = [x.to(device) if isinstance(x, torch.Tensor) else x for x in inputs]
            else:
                inputs = inputs.to(device)
                
            if isinstance(targets, (list, tuple)):
                targets = [y.to(device) if isinstance(y, torch.Tensor) else y for y in targets]
            else:
                targets = targets.to(device)
            
            # Forward pass
            outputs = model(inputs)
            
            # Compute loss
            loss = criterion(outputs, targets)
            
            # Update metrics
            batch_size = targets.shape[0] if hasattr(targets, 'shape') else len(targets)
            running_loss += loss.item() * batch_size
            samples_seen += batch_size
            
            # Compute custom metrics
            if metrics:
                for metric_name, metric_fn in metrics.items():
                    metric_values[metric_name] += metric_fn(outputs, targets) * batch_size
            
            # Update progress bar
            eval_pbar.set_postfix({
                'loss': running_loss / samples_seen,
                **{name: values / samples_seen for name, values in metric_values.items()}
            })
    
    # Calculate final metrics
    avg_loss = running_loss / samples_seen
    
    # Prepare return dictionary
    results = {f"{prefix}_loss": avg_loss}
    
    if metrics:
        for metric_name, value in metric_values.items():
            results[f"{prefix}_{metric_name}"] = value / samples_seen
    
    # Log evaluation summary
    log_msg = f"Evaluation completed - {prefix}_loss: {avg_loss:.4f}"
    if metrics:
        log_msg += " - " + " - ".join([
            f"{prefix}_{name}: {values / samples_seen:.4f}" 
            for name, values in metric_values.items()
        ])
    logger.info(log_msg)
    
    return results


def accuracy(outputs: torch.Tensor, targets: torch.Tensor) -> float:
    """Calculate accuracy for classification tasks."""
    _, predicted = torch.max(outputs.data, 1)
    correct = (predicted == targets).sum().item()
    return correct / targets.size(0)


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    filename: str,
    metrics: Optional[Dict[str, float]] = None,
    scheduler: Optional[_LRScheduler] = None
) -> None:
    """
    Save training checkpoint.
    
    Args:
        model: PyTorch model
        optimizer: Optimizer
        epoch: Current epoch
        filename: Path to save checkpoint
        metrics: Optional metrics to save
        scheduler: Optional learning rate scheduler
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }
    
    if metrics:
        checkpoint['metrics'] = metrics
        
    if scheduler:
        checkpoint['scheduler_state_dict'] = scheduler.state_dict()
    
    torch.save(checkpoint, filename)
    logger.info(f"Checkpoint saved to {filename}")


def load_checkpoint(
    filename: str,
    model: nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[_LRScheduler] = None,
    device: Optional[Union[str, torch.device]] = None
) -> Dict[str, Any]:
    """
    Load training checkpoint.
    
    Args:
        filename: Path to checkpoint file
        model: PyTorch model
        optimizer: Optional optimizer to restore state
        scheduler: Optional scheduler to restore state
        device: Device to load the model onto
        
    Returns:
        Dictionary containing checkpoint information
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    elif isinstance(device, str):
        device = torch.device(device)
    
    checkpoint = torch.load(filename, map_location=device)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    
    if optimizer and 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
    if scheduler and 'scheduler_state_dict' in checkpoint:
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    
    logger.info(f"Loaded checkpoint from {filename} (epoch {checkpoint.get('epoch', 'unknown')})")
    
    return checkpoint
