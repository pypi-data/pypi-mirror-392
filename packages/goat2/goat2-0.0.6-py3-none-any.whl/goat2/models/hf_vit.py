from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from typing import Dict, List, Optional, Union
import os
from PIL import Image

# Dictionary of common Vision Transformer models with parameter counts (millions)
MODEL_PARAMS = {
    "google/vit-base-patch16-224": 86,
    "google/vit-large-patch16-224": 307,
    "google/vit-huge-patch14-224": 632,
    "facebook/deit-tiny-patch16-224": 5,
    "facebook/deit-small-patch16-224": 22,
    "facebook/deit-base-patch16-224": 86,
    "microsoft/beit-base-patch16-224": 86,
    "microsoft/beit-large-patch16-224": 304,
    "facebook/deit-base-distilled-patch16-224": 87,
    "WinKawaks/vit-small-patch16-224": 22,
}

def load_vit(
    model_name: str = "google/vit-base-patch16-224",
    num_classes: Optional[int] = None,
    device: Optional[str] = None
) -> tuple:
    """
    Load a Vision Transformer model with specified parameters.
    
    Args:
        model_name: HuggingFace model identifier
        num_classes: Number of output classes (if None, uses model's default)
        device: Computing device (auto-detected if None)
        
    Returns:
        Tuple of (model, processor)
    """
    # Determine device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load processor and model
    processor = AutoImageProcessor.from_pretrained(model_name, use_fast=True)
    model = AutoModelForImageClassification.from_pretrained(
        model_name,
        num_labels=num_classes,
        ignore_mismatched_sizes=True
    ).to(device)
    
    return model, processor

def get_model_info(model_name: Optional[str] = None) -> Union[Dict[str, float], float]:
    """
    Get parameter count information for Vision Transformer models.
    
    Args:
        model_name: Specific model to get information about. If None, returns all models.
        
    Returns:
        Dictionary of all models with parameter counts, or a single count for the specified model.
    """
    if model_name is None:
        return MODEL_PARAMS
    
    if model_name in MODEL_PARAMS:
        return MODEL_PARAMS[model_name]
    
    return f"Model {model_name} not found in the parameter dictionary."

def _validate_model(model, val_loader, device, max_samples=None):
    """
    Helper function for validation during training
    
    Args:
        model: Model to validate
        val_loader: Validation DataLoader
        device: Computing device
        max_samples: Maximum number of samples to validate on (None = all samples)
    """
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0
    
    sample_count = 0
    with torch.no_grad():
        for batch in val_loader:
            # Get images and labels
            images = batch['pixel_values'].to(device) if 'pixel_values' in batch else batch[0].to(device)
            labels = batch['labels'].to(device) if 'labels' in batch else batch[1].to(device)
            
            # Forward pass
            outputs = model(images, labels=labels)
            val_loss += outputs.loss.item()
            
            # Calculate accuracy if logits are available
            if hasattr(outputs, 'logits'):
                _, predicted = torch.max(outputs.logits, 1)
                batch_size = labels.size(0)
                total += batch_size
                correct += (predicted == labels).sum().item()
            
            # Count samples and break if we've reached max_samples
            sample_count += batch_size
            if max_samples is not None and sample_count >= max_samples:
                break
    
    # Calculate average loss and accuracy
    batch_count = len(val_loader) if max_samples is None else ((sample_count-1) // batch_size + 1)
    avg_loss = val_loss / batch_count if batch_count > 0 else 0
    accuracy = 100 * correct / total if total > 0 else 0
    
    return avg_loss, accuracy

def train_vit(
    model,
    train_loader: DataLoader,
    val_loader: Optional[DataLoader] = None,
    num_epochs: int = 3,
    learning_rate: float = 1e-4,
    patience: int = 5,
    checkpoint_dir: Optional[str] = None,
    device: Optional[str] = None,
    validation_freq: int = 0,  # 0 means evaluate only at end of epochs
    max_val_samples: Optional[int] = None  # Number of samples to use for validation
) -> Dict:
    """
    Train a Vision Transformer model with early stopping and checkpointing.
    
    Args:
        model: The model to train
        train_loader: DataLoader containing training data
        val_loader: DataLoader containing validation data
        num_epochs: Maximum number of training epochs
        learning_rate: Learning rate for optimization
        patience: Number of checks with no improvement after which to stop
        checkpoint_dir: Directory to save model checkpoints
        device: Computing device (auto-detected if None)
        validation_freq: How often to check validation (in steps, 0 = only at epoch end)
        max_val_samples: Maximum samples to use for validation (None = all samples)
        
    Returns:
        Dictionary with training metrics
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Setup model and optimizer
    model.to(device)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    
    # Initialize metrics
    results = {
        "train_loss_history": [],
        "val_loss_history": [] if val_loader else None
    }
    
    # Early stopping and checkpoint variables
    best_val_loss = float('inf')
    no_improve_count = 0
    # Set validation frequency if not specified
    if validation_freq == 0 and val_loader:
        validation_freq = len(train_loader)  # Once per epoch
    elif validation_freq == 0:
        validation_freq = float('inf')  # Never check within epochs
    
    # Create checkpoint directory
    if checkpoint_dir and not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    
    # Track global step for logging
    global_step = 0
    stop_training = False
    
    for epoch in range(num_epochs):
        if stop_training:
            break
            
        running_loss = 0.0
        correct = 0
        total = 0
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")
        for batch_idx, batch in enumerate(progress_bar):
            # Get images and labels
            images = batch['pixel_values'].to(device) if 'pixel_values' in batch else batch[0].to(device)
            labels = batch['labels'].to(device) if 'labels' in batch else batch[1].to(device)
            
            # Forward and backward pass
            optimizer.zero_grad()
            outputs = model(images, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            # Track metrics
            running_loss += loss.item()
            global_step += 1
            
            # Calculate accuracy if logits are available
            if hasattr(outputs, 'logits'):
                _, predicted = torch.max(outputs.logits, 1)
                batch_size = labels.size(0)
                total += batch_size
                correct += (predicted == labels).sum().item()
                
                # Update progress bar
                progress_bar.set_postfix({
                    'loss': running_loss / (batch_idx + 1),
                    'acc': 100 * correct / total if total > 0 else 0
                })
            
            # Validate within epoch if configured
            if val_loader and global_step % validation_freq == 0:
                val_loss, val_acc = _validate_model(model, val_loader, device, max_val_samples)
                results["val_loss_history"].append(val_loss)
                
                print(f"Step {global_step}: Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
                
                # Check for improvement
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    no_improve_count = 0
                    
                    # Save best model checkpoint
                    if checkpoint_dir:
                        checkpoint_path = os.path.join(checkpoint_dir, "best_model.pt")
                        torch.save({
                            'epoch': epoch,
                            'global_step': global_step,
                            'model_state_dict': model.state_dict(),
                            'optimizer_state_dict': optimizer.state_dict(),
                            'val_loss': val_loss,
                        }, checkpoint_path)
                        print(f"Saved new best model with val_loss: {val_loss:.4f}")
                else:
                    no_improve_count += 1
                
                # Early stopping check
                if no_improve_count >= patience:
                    print(f"Early stopping triggered after {global_step} steps")
                    stop_training = True
                    break
                
                # Set model back to training mode
                model.train()
        
        # Record epoch training metrics
        epoch_train_loss = running_loss / len(train_loader)
        epoch_train_acc = 100 * correct / total if total > 0 else 0
        results["train_loss_history"].append(epoch_train_loss)
        
        print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {epoch_train_loss:.4f}, Train Acc: {epoch_train_acc:.2f}%")
        
        # Full validation at end of epoch if not done in last step
        if val_loader and not stop_training and global_step % validation_freq != 0:
            val_loss, val_acc = _validate_model(model, val_loader, device, max_val_samples)
            if results["val_loss_history"] is None:
                results["val_loss_history"] = []
            results["val_loss_history"].append(val_loss)
            
            print(f"Epoch {epoch+1}: Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
            
            # Check for improvement
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                no_improve_count = 0
                
                # Save best model checkpoint
                if checkpoint_dir:
                    checkpoint_path = os.path.join(checkpoint_dir, "best_model.pt")
                    torch.save({
                        'epoch': epoch,
                        'global_step': global_step,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'val_loss': val_loss,
                    }, checkpoint_path)
                    print(f"Saved new best model with val_loss: {val_loss:.4f}")
            else:
                no_improve_count += 1
            
            # Early stopping check
            if no_improve_count >= patience:
                print(f"Early stopping triggered after {epoch+1} epochs")
                break
    
    # Load best model if available
    if checkpoint_dir and os.path.exists(os.path.join(checkpoint_dir, "best_model.pt")):
        checkpoint = torch.load(os.path.join(checkpoint_dir, "best_model.pt"))
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Loaded best model with validation loss: {checkpoint['val_loss']:.4f}")
    
    return results

def eval_vit(
    model,
    test_loader: DataLoader,
    device: Optional[str] = None,
    max_samples: Optional[int] = None,
    checkpoint_dir: Optional[str] = None
) -> Dict:
    """
    Evaluate a Vision Transformer model on a test dataset.
    
    Args:
        model: The model to evaluate
        test_loader: DataLoader containing test data
        device: Computing device (auto-detected if None)
        max_samples: Maximum number of samples to evaluate on (None = all samples)
        checkpoint_dir: Directory to load model checkpoint from (if None, uses model as-is)
        
    Returns:
        Dictionary with evaluation metrics
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model.to(device)
    
    # Load checkpoint if provided
    if checkpoint_dir and os.path.exists(os.path.join(checkpoint_dir, "best_model.pt")):
        checkpoint = torch.load(os.path.join(checkpoint_dir, "best_model.pt"), map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Loaded best model from {checkpoint_dir} with validation loss: {checkpoint['val_loss']:.4f}")
    
    model.eval()
    
    results = {
        "correct": 0,
        "total": 0,
        "loss": 0.0,
        "class_accuracy": {}
    }
    
    sample_count = 0
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Evaluating"):
            # Get images and labels
            images = batch['pixel_values'].to(device) if 'pixel_values' in batch else batch[0].to(device)
            labels = batch['labels'].to(device) if 'labels' in batch else batch[1].to(device)
            
            # Forward pass
            outputs = model(images, labels=labels)
            results["loss"] += outputs.loss.item()
            
            # Get predictions
            _, predicted = torch.max(outputs.logits, 1)
            
            # Update metrics
            batch_size = labels.size(0)
            results["total"] += batch_size
            correct = (predicted == labels).sum().item()
            results["correct"] += correct
            
            # Track per-class accuracy
            for i in range(batch_size):
                true_label = labels[i].item()
                pred_label = predicted[i].item()
                
                label_str = str(true_label)
                if label_str not in results["class_accuracy"]:
                    results["class_accuracy"][label_str] = {"correct": 0, "total": 0}
                
                results["class_accuracy"][label_str]["total"] += 1
                if true_label == pred_label:
                    results["class_accuracy"][label_str]["correct"] += 1
            
            # Count samples and break if we've reached max_samples
            sample_count += batch_size
            if max_samples is not None and sample_count >= max_samples:
                break
    
    # Calculate overall metrics
    batch_count = len(test_loader) if max_samples is None else ((sample_count-1) // batch_size + 1)
    results["accuracy"] = results["correct"] / results["total"] if results["total"] > 0 else 0
    results["avg_loss"] = results["loss"] / batch_count if batch_count > 0 else 0
    
    # Calculate per-class accuracy
    for cls in results["class_accuracy"]:
        cls_metrics = results["class_accuracy"][cls]
        if cls_metrics["total"] > 0:
            cls_metrics["accuracy"] = cls_metrics["correct"] / cls_metrics["total"]
        else:
            cls_metrics["accuracy"] = 0.0
    
    return results

# Example usage with dataloaders:
if __name__ == "__main__":
    num_classes = 10  # Example: number of classes in your dataset
    
    # Load model and processor
    model, processor = load_vit(
        model_name="google/vit-base-patch16-224",
        num_classes=num_classes
    )
    
    # Example: Create train, validation and test loaders (you would need to implement these)
    # train_loader = create_dataloader(...)
    # val_loader = create_dataloader(...)
    # test_loader = create_dataloader(...)
    
    # Train model with early stopping and checkpointing
    # train_results = train_vit(
    #     model, 
    #     train_loader,
    #     val_loader=val_loader,
    #     num_epochs=10,
    #     patience=5,
    #     checkpoint_dir="./checkpoints",
    #     validation_freq=5,  # Check validation every 100 steps,
    #     max_val_samples=1000  # Use only 1000 samples for validation
    # )
    
    # Evaluate model
    # eval_results = eval_vit(model, test_loader, checkpoint_dir="./checkpoints")
    # print(f"Test Accuracy: {eval_results['accuracy']:.2%} ({eval_results['correct']}/{eval_results['total']})")
