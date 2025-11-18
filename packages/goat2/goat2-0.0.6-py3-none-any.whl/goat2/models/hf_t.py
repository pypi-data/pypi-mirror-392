"""
HuggingFace Transformer models for text classification tasks.

This module provides utilities to load, fine-tune and evaluate pre-trained 
transformer models from HuggingFace for text classification tasks.
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from typing import Dict, List, Union, Optional, Tuple, Any, Callable
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EvalPrediction,
    IntervalStrategy
)
from datasets import Dataset as HFDataset
import logging
from tqdm import tqdm

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

# Dictionary mapping common model names to their HuggingFace identifiers
MODEL_MAPPINGS = {
    'bert': 'bert-base-uncased',
    'bert-large': 'bert-large-uncased',
    'roberta': 'roberta-base',
    'roberta-large': 'roberta-large',
    'distilbert': 'distilbert-base-uncased',
    'albert': 'albert-base-v2',
    'xlnet': 'xlnet-base-cased',
    'electra': 'google/electra-base-discriminator',
    'deberta': 'microsoft/deberta-base',
}

# Dictionary of transformer model parameter counts (in millions)
MODEL_PARAMS = {
    "bert-base-uncased": 110,
    "bert-large-uncased": 340,
    "roberta-base": 125,
    "roberta-large": 355,
    "distilbert-base-uncased": 66,
    "albert-base-v2": 12,
    "xlnet-base-cased": 110,
    "google/electra-base-discriminator": 110,
    "microsoft/deberta-base": 140,
    "microsoft/deberta-v3-large": 440,
    "facebook/bart-base": 140,
    "facebook/bart-large": 400,
    "t5-small": 60,
    "t5-base": 220,
    "t5-large": 770,
    "sshleifer/distilbart-cnn-12-6": 306,
    "cross-encoder/ms-marco-MiniLM-L-6-v2": 22,
    "sentence-transformers/all-mpnet-base-v2": 110,
    "distilroberta-base": 82,
    "microsoft/mpnet-base": 110
}

def get_model_info(model_name: Optional[str] = None) -> Union[Dict[str, float], float, str]:
    """
    Get parameter count information for transformer models.
    
    Args:
        model_name: Specific model to get information about. If None, returns all models.
        
    Returns:
        Dictionary of all models with parameter counts, or a single count for the specified model.
    """
    # If model_name is None, return the entire dictionary
    if model_name is None:
        return MODEL_PARAMS
    
    # Check if model_name is in our mapping
    if model_name in MODEL_MAPPINGS:
        model_name = MODEL_MAPPINGS[model_name]
    
    # Return parameter count if found
    if model_name in MODEL_PARAMS:
        return MODEL_PARAMS[model_name]
    
    return f"Model {model_name} not found in the parameter dictionary."

class TextClassificationDataset(Dataset):
    """Dataset for text classification with transformers"""

    def __init__(
        self, 
        texts: List[str], 
        labels: Optional[List[Union[int, float]]] = None,
        tokenizer: Any = None,
        max_length: int = 128,
    ):
        """
        Initialize dataset for transformer-based text classification.
        
        Args:
            texts: List of text strings
            labels: List of labels (optional, for inference without labels)
            tokenizer: HuggingFace tokenizer
            max_length: Maximum sequence length
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Remove batch dimension from encoding
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        
        # Add label if available
        if self.labels is not None:
            item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
            
        return item


def load_transformer_model(
    model_name: str, 
    num_labels: int = 2, 
    use_auth_token: bool = False,
    **model_kwargs
) -> Tuple[Any, Any]:
    """
    Load a pre-trained transformer model and tokenizer from HuggingFace.

    Args:
        model_name: Model name or path (use predefined shortcuts or HF model IDs)
        num_labels: Number of classification labels
        use_auth_token: Whether to use HF auth token for gated models
        **model_kwargs: Additional kwargs to pass to the model constructor

    Returns:
        Tuple of (tokenizer, model)
    """
    # Check if model_name is in our mapping
    if model_name in MODEL_MAPPINGS:
        model_name = MODEL_MAPPINGS[model_name]
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        use_auth_token=use_auth_token
    )
    
    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        use_auth_token=use_auth_token,
        **model_kwargs
    )
    
    return tokenizer, model


def prepare_dataset(
    texts: List[str],
    labels: Optional[List[Union[int, float]]] = None,
    tokenizer: Any = None,
    max_length: int = 128,
    batch_size: int = 16,
    shuffle: bool = True,
    return_dataloader: bool = False,
    hf_dataset: bool = False
) -> Union[TextClassificationDataset, HFDataset, DataLoader]:
    """
    Prepare dataset for transformer model training or inference.

    Args:
        texts: List of text strings
        labels: List of labels (optional)
        tokenizer: HuggingFace tokenizer
        max_length: Maximum sequence length
        batch_size: Batch size (only used if return_dataloader=True)
        shuffle: Whether to shuffle data (only used if return_dataloader=True)
        return_dataloader: Whether to return a DataLoader instead of a Dataset
        hf_dataset: Whether to return a HuggingFace Dataset instead of a PyTorch Dataset

    Returns:
        TextClassificationDataset, HuggingFace Dataset, or DataLoader
    """
    if hf_dataset:
        # Convert to HuggingFace Dataset format
        data_dict = {"text": texts}
        if labels is not None:
            data_dict["labels"] = labels
            
        dataset = HFDataset.from_dict(data_dict)
        
        # Tokenize the dataset
        if tokenizer is not None:
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"],
                    padding="max_length",
                    truncation=True,
                    max_length=max_length
                )
                
            dataset = dataset.map(tokenize_function, batched=True)
        
        if return_dataloader:
            raise ValueError("Cannot return DataLoader when using HuggingFace Dataset. Use Trainer instead.")
        
        return dataset
    else:
        # Convert to PyTorch Dataset
        dataset = TextClassificationDataset(
            texts=texts,
            labels=labels,
            tokenizer=tokenizer,
            max_length=max_length
        )
        
        if return_dataloader:
            return DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=shuffle
            )
            
        return dataset


def compute_metrics(eval_pred: EvalPrediction) -> Dict:
    """
    Compute metrics for evaluation.

    Args:
        eval_pred: EvalPrediction object containing predictions and labels

    Returns:
        Dictionary containing metrics
    """
    predictions = np.argmax(eval_pred.predictions, axis=1)
    labels = eval_pred.label_ids
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
    acc = accuracy_score(labels, predictions)
    
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


def finetune_transformer(
    model: Any,
    tokenizer: Any,
    train_texts: List[str],
    train_labels: List[Union[int, float]],
    val_texts: Optional[List[str]] = None,
    val_labels: Optional[List[Union[int, float]]] = None,
    output_dir: str = "./results",
    num_epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 5e-5,
    max_length: int = 128,
    weight_decay: float = 0.01,
    warmup_ratio: float = 0.1,
    evaluation_strategy: str = "epoch",
    save_strategy: str = "epoch",
    load_best_model: bool = True,
    report_to: Optional[List[str]] = None,
    fp16: bool = False,
    gradient_accumulation_steps: int = 1
) -> Any:
    """
    Fine-tune a transformer model for text classification.

    Args:
        model: Transformer model
        tokenizer: Tokenizer
        train_texts: Training texts
        train_labels: Training labels
        val_texts: Validation texts
        val_labels: Validation labels
        output_dir: Directory to save results
        num_epochs: Number of training epochs
        batch_size: Batch size per device
        learning_rate: Learning rate
        max_length: Maximum sequence length
        weight_decay: Weight decay
        warmup_ratio: Ratio of training steps for LR warmup
        evaluation_strategy: When to evaluate ('no', 'steps', 'epoch')
        save_strategy: When to save checkpoints ('no', 'steps', 'epoch')
        load_best_model: Whether to load the best model at the end
        report_to: List of integrations to report to (e.g., ['tensorboard'])
        fp16: Whether to use mixed precision training
        gradient_accumulation_steps: Number of gradient accumulation steps

    Returns:
        Trained model
    """
    # Prepare datasets
    train_dataset = prepare_dataset(
        texts=train_texts,
        labels=train_labels,
        tokenizer=tokenizer,
        max_length=max_length,
        hf_dataset=True
    )
    
    validation_dataset = None
    if val_texts is not None and val_labels is not None:
        validation_dataset = prepare_dataset(
            texts=val_texts,
            labels=val_labels,
            tokenizer=tokenizer,
            max_length=max_length,
            hf_dataset=True
        )
    
    # Convert evaluation_strategy to IntervalStrategy
    if evaluation_strategy == "epoch":
        eval_strategy = IntervalStrategy.EPOCH
    elif evaluation_strategy == "steps":
        eval_strategy = IntervalStrategy.STEPS
    else:
        eval_strategy = IntervalStrategy.NO
        
    # Convert save_strategy to IntervalStrategy
    if save_strategy == "epoch":
        save_strat = IntervalStrategy.EPOCH
    elif save_strategy == "steps":
        save_strat = IntervalStrategy.STEPS
    else:
        save_strat = IntervalStrategy.NO
    
    # Prepare training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        warmup_ratio=warmup_ratio,
        evaluation_strategy=eval_strategy,
        save_strategy=save_strat,
        load_best_model_at_end=load_best_model and validation_dataset is not None,
        report_to=report_to if report_to else "none",
        fp16=fp16,
        gradient_accumulation_steps=gradient_accumulation_steps,
        save_total_limit=2  # Only keep the 2 best checkpoints
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )
    
    # Train model
    trainer.train()
    
    # Evaluate model if validation data is provided
    if validation_dataset is not None:
        metrics = trainer.evaluate()
        logging.info(f"Evaluation metrics: {metrics}")
    
    # Save final model
    trainer.save_model(f"{output_dir}/final-model")
    tokenizer.save_pretrained(f"{output_dir}/final-model")
    
    return model


def predict_text_classification(
    model: Any,
    tokenizer: Any,
    texts: List[str],
    max_length: int = 128,
    batch_size: int = 16,
    device: Optional[str] = None,
    return_probabilities: bool = False
) -> Union[List[int], Tuple[List[int], np.ndarray]]:
    """
    Make predictions with a fine-tuned transformer model.

    Args:
        model: Fine-tuned transformer model
        tokenizer: Tokenizer
        texts: List of texts to predict
        max_length: Maximum sequence length
        batch_size: Batch size
        device: Device to use ('cpu', 'cuda', etc.)
        return_probabilities: Whether to return class probabilities

    Returns:
        List of predictions or tuple of (predictions, probabilities)
    """
    # Set device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model.to(device)
    model.eval()
    
    # Prepare dataloader
    dataloader = prepare_dataset(
        texts=texts,
        tokenizer=tokenizer,
        max_length=max_length,
        batch_size=batch_size,
        shuffle=False,
        return_dataloader=True
    )
    
    # Make predictions
    predictions = []
    probabilities = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Making predictions"):
            # Move batch to device
            batch = {k: v.to(device) for k, v in batch.items()}
            
            # Forward pass
            outputs = model(**batch)
            logits = outputs.logits
            
            # Get predictions
            preds = torch.argmax(logits, dim=1)
            probs = torch.nn.functional.softmax(logits, dim=1)
            
            # Add to lists
            predictions.extend(preds.cpu().numpy())
            probabilities.extend(probs.cpu().numpy())
    
    # Return results
    if return_probabilities:
        return predictions, np.array(probabilities)
    else:
        return predictions


def evaluate_text_classification(
    model: Any,
    tokenizer: Any,
    texts: List[str],
    labels: List[int],
    max_length: int = 128,
    batch_size: int = 16,
    device: Optional[str] = None
) -> Dict[str, float]:
    """
    Evaluate a fine-tuned transformer model on a test set.

    Args:
        model: Fine-tuned transformer model
        tokenizer: Tokenizer
        texts: List of texts to evaluate
        labels: List of true labels
        max_length: Maximum sequence length
        batch_size: Batch size
        device: Device to use ('cpu', 'cuda', etc.)

    Returns:
        Dictionary with evaluation metrics
    """
    # Get predictions
    predictions = predict_text_classification(
        model=model,
        tokenizer=tokenizer,
        texts=texts,
        max_length=max_length,
        batch_size=batch_size,
        device=device
    )
    
    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
    acc = accuracy_score(labels, predictions)
    
    # Create report
    report = classification_report(labels, predictions, output_dict=True)
    
    # Return metrics
    metrics = {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'report': report
    }
    
    return metrics


def load_and_finetune_transformer(
    model_name: str,
    train_texts: List[str],
    train_labels: List[Union[int, float]],
    val_texts: Optional[List[str]] = None,
    val_labels: Optional[List[Union[int, float]]] = None,
    num_labels: int = 2,
    output_dir: str = "./results",
    num_epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 5e-5,
    max_length: int = 128
) -> Tuple[Any, Any]:
    """
    Load and fine-tune a transformer model for text classification.

    Args:
        model_name: Model name (use predefined shortcuts or HF model IDs)
        train_texts: Training texts
        train_labels: Training labels
        val_texts: Validation texts
        val_labels: Validation labels
        num_labels: Number of classification labels
        output_dir: Directory to save results
        num_epochs: Number of training epochs
        batch_size: Batch size per device
        learning_rate: Learning rate
        max_length: Maximum sequence length

    Returns:
        Tuple of (model, tokenizer)
    """
    # Load model and tokenizer
    tokenizer, model = load_transformer_model(
        model_name=model_name,
        num_labels=num_labels
    )
    
    # Fine-tune model
    model = finetune_transformer(
        model=model,
        tokenizer=tokenizer,
        train_texts=train_texts,
        train_labels=train_labels,
        val_texts=val_texts,
        val_labels=val_labels,
        output_dir=output_dir,
        num_epochs=num_epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        max_length=max_length
    )
    
    return model, tokenizer


# Example usage
def example_usage():
    """Example demonstrating usage of the module"""
    # Example data
    train_texts = [
        "I love this product, it works great.",
        "The service was terrible, I'm never coming back.",
        "This movie was just okay, nothing special.",
        "The restaurant had amazing food!",
        "I hate how this app crashes all the time."
    ]
    train_labels = [1, 0, 2, 1, 0]  # Positive (1), Negative (0), Neutral (2)
    
    val_texts = [
        "The food was good but service was slow.",
        "Best purchase I've made all year!"
    ]
    val_labels = [2, 1]
    
    # Load and fine-tune model
    model, tokenizer = load_and_finetune_transformer(
        model_name='distilbert',  # Using shorthand name
        train_texts=train_texts,
        train_labels=train_labels,
        val_texts=val_texts,
        val_labels=val_labels,
        num_labels=3,  # Positive, Negative, Neutral
        num_epochs=1,  # Just for demonstration
        batch_size=2
    )
    
    # Make predictions
    test_texts = ["This is amazing!", "I'm disappointed with the quality."]
    predictions = predict_text_classification(model, tokenizer, test_texts)
    
    print(f"Predictions: {predictions}")  # Expected: [1, 0]
