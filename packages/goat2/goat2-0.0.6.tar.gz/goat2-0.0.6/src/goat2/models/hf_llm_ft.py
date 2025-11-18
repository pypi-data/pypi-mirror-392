from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    AutoModelForSeq2SeqLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling,
    DataCollatorForSeq2Seq
)
from peft import (
    get_peft_model,
    LoraConfig,
    TaskType,
    prepare_model_for_kbit_training
)
from datasets import Dataset, load_dataset
from tqdm import tqdm
from typing import Dict, Any, Optional, List, Union, Tuple, Callable
import torch
import os
import numpy as np
import evaluate
from torch.utils.data import DataLoader

# Import model information from the original file
from .hf_llm import get_pipeline_type, get_model_info, MODEL_PARAMS

# Fine-tuning configurations for different model sizes
FT_CONFIGS = {
    "tiny": {  # < 500M
        "lora_r": 8,
        "lora_alpha": 16,
        "lora_dropout": 0.05,
        "learning_rate": 5e-4,
        "batch_size": 8,
        "gradient_accumulation_steps": 2,
    },
    "small": {  # 500M - 1.5B
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.10,
        "learning_rate": 2e-4,
        "batch_size": 4,
        "gradient_accumulation_steps": 4,
    },
    "medium": {  # 1.5B - 3B
        "lora_r": 32,
        "lora_alpha": 64,
        "lora_dropout": 0.10,
        "learning_rate": 1e-4,
        "batch_size": 2,
        "gradient_accumulation_steps": 8,
    },
    "large": {  # 3B - 5B
        "lora_r": 64,
        "lora_alpha": 128,
        "lora_dropout": 0.10,
        "learning_rate": 5e-5,
        "batch_size": 1,
        "gradient_accumulation_steps": 16,
    }
}

def get_ft_config(model_name: str) -> Dict[str, Any]:
    """
    Get appropriate fine-tuning configuration based on model size.
    
    Args:
        model_name: HuggingFace model identifier
        
    Returns:
        Dictionary with fine-tuning hyperparameters
    """
    # Get model size in billions
    params = get_model_info(model_name)
    
    if not isinstance(params, (int, float)):
        raise ValueError(f"Model {model_name} not found in parameter dictionary.")
    
    # Select appropriate config based on size
    if params < 0.5:
        return FT_CONFIGS["tiny"]
    elif params < 1.5:
        return FT_CONFIGS["small"]
    elif params < 3.0:
        return FT_CONFIGS["medium"]
    else:
        return FT_CONFIGS["large"]

def prepare_dataset(
    data: Union[Dataset, Dict, str],
    tokenizer: Any,
    text_column: str = "text",
    input_column: Optional[str] = None,
    target_column: Optional[str] = None,
    max_length: int = 512,
    pipeline_type: str = "text-generation",
    is_chat_dataset: bool = False,
    chat_template: Optional[str] = None,
) -> Dataset:
    """
    Prepare dataset for fine-tuning by tokenizing and formatting inputs/outputs.
    
    Args:
        data: Dataset object, dictionary, or path to dataset
        tokenizer: HuggingFace tokenizer
        text_column: Column containing text data (for single-text format)
        input_column: Column containing input text (for input-target format)
        target_column: Column containing target text (for input-target format)
        max_length: Maximum sequence length
        pipeline_type: Either "text-generation" or "text2text-generation"
        is_chat_dataset: Whether the dataset follows chat format (messages)
        chat_template: Optional custom chat template
    
    Returns:
        Processed dataset ready for training
    """
    # Handle different input types
    if isinstance(data, str):
        dataset = load_dataset(data)["train"]
    elif isinstance(data, dict):
        dataset = Dataset.from_dict(data)
    else:
        dataset = data
    
    # Define tokenization function based on model type and format
    if pipeline_type == "text2text-generation":
        # For encoder-decoder models
        def tokenize_function(examples):
            inputs = examples[input_column] if input_column else examples[text_column]
            targets = examples[target_column] if target_column and target_column in examples else None
            
            model_inputs = tokenizer(
                inputs, 
                max_length=max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            if targets:
                with tokenizer.as_target_tokenizer():
                    labels = tokenizer(
                        targets,
                        max_length=max_length,
                        padding="max_length",
                        truncation=True,
                        return_tensors="pt"
                    ).input_ids
                model_inputs["labels"] = labels
            
            return model_inputs
            
    else:
        # For decoder-only models
        if is_chat_dataset:
            # For chat datasets
            def tokenize_function(examples):
                if chat_template:
                    # Use custom template
                    tokenizer.chat_template = chat_template
                
                # Format messages using tokenizer's chat template
                formatted_inputs = []
                for msg_list in examples["messages"] if "messages" in examples else examples:
                    formatted_inputs.append(tokenizer.apply_chat_template(
                        msg_list,
                        tokenize=False,
                        add_generation_prompt=False
                    ))
                
                tokenized_inputs = tokenizer(
                    formatted_inputs,
                    max_length=max_length,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt"
                )
                
                tokenized_inputs["labels"] = tokenized_inputs["input_ids"].clone()
                return tokenized_inputs
        else:
            # For standard text datasets
            def tokenize_function(examples):
                texts = examples[text_column]
                tokenized_inputs = tokenizer(
                    texts,
                    max_length=max_length,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt"
                )
                
                tokenized_inputs["labels"] = tokenized_inputs["input_ids"].clone()
                return tokenized_inputs
    
    # Apply tokenization to the dataset
    return dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=[col for col in dataset.column_names if col not in ["input_ids", "attention_mask", "labels"]]
    )

def finetune_llm(
    data: Union[Dataset, Dict, str],
    model_name: str = "microsoft/phi-2",
    output_dir: str = "./fine-tuned-model",
    text_column: str = "text",
    input_column: Optional[str] = None,
    target_column: Optional[str] = None,
    is_chat_dataset: bool = False,
    chat_template: Optional[str] = None,
    num_train_epochs: int = 3,
    max_length: int = 512,
    learning_rate: Optional[float] = None,
    lora_r: Optional[int] = None,
    lora_alpha: Optional[int] = None,
    lora_dropout: Optional[float] = None,
    batch_size: Optional[int] = None,
    gradient_accumulation_steps: Optional[int] = None,
    warmup_ratio: float = 0.1,
    weight_decay: float = 0.01,
    eval_data: Optional[Union[Dataset, Dict, str]] = None,
    eval_steps: int = 200,
    logging_steps: int = 50,
    use_4bit: bool = True,
    device: Optional[str] = None,
) -> Tuple[Any, Any]:
    """
    Fine-tune a language model using PEFT/LoRA.
    
    Args:
        data: Training data
        model_name: HuggingFace model identifier
        output_dir: Directory to save the fine-tuned model
        text_column: Column containing text data
        input_column: Column containing input text
        target_column: Column containing target text
        is_chat_dataset: Whether dataset follows chat format
        chat_template: Custom chat template
        num_train_epochs: Number of training epochs
        max_length: Maximum sequence length
        learning_rate, lora_r, lora_alpha, lora_dropout, batch_size, gradient_accumulation_steps: 
            Training params (if None, will be auto-selected based on model size)
        warmup_ratio: Ratio of steps for learning rate warmup
        weight_decay: Weight decay for regularization
        eval_data: Evaluation dataset
        eval_steps: How often to evaluate during training
        logging_steps: How often to log during training
        use_4bit: Whether to use 4-bit quantization
        device: Computing device (auto-detected if None)
    
    Returns:
        Tuple of (model, tokenizer)
    """
    # Determine device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Determine pipeline type
    pipeline_type = get_pipeline_type(model_name)
    
    # Get model-specific fine-tuning config
    ft_config = get_ft_config(model_name)
    
    # Override config with user-provided values
    if learning_rate is not None:
        ft_config["learning_rate"] = learning_rate
    if lora_r is not None:
        ft_config["lora_r"] = lora_r
    if lora_alpha is not None:
        ft_config["lora_alpha"] = lora_alpha
    if lora_dropout is not None:
        ft_config["lora_dropout"] = lora_dropout
    if batch_size is not None:
        ft_config["batch_size"] = batch_size
    if gradient_accumulation_steps is not None:
        ft_config["gradient_accumulation_steps"] = gradient_accumulation_steps
    
    print(f"Loading {model_name} ({get_model_info(model_name)}B parameters) with {pipeline_type} pipeline...")
    
    # Initialize tokenizer and model based on pipeline type
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    # Ensure the tokenizer has padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with quantization if specified
    quantization_config = None
    if use_4bit:
        quantization_config = {"load_in_4bit": True, "bnb_4bit_compute_dtype": torch.bfloat16}
    
    if pipeline_type == "text2text-generation":
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, 
            trust_remote_code=True,
            device_map="auto" if device == "cuda" else None,
            quantization_config=quantization_config
        )
        task_type = TaskType.SEQ_2_SEQ_LM
        data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    else:  # text-generation
        model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            trust_remote_code=True,
            device_map="auto" if device == "cuda" else None,
            quantization_config=quantization_config
        )
        task_type = TaskType.CAUSAL_LM
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    # Prepare dataset
    train_dataset = prepare_dataset(
        data=data,
        tokenizer=tokenizer,
        text_column=text_column,
        input_column=input_column,
        target_column=target_column,
        max_length=max_length,
        pipeline_type=pipeline_type,
        is_chat_dataset=is_chat_dataset,
        chat_template=chat_template
    )
    
    # Prepare evaluation dataset if provided
    eval_dataset = None
    if eval_data:
        eval_dataset = prepare_dataset(
            data=eval_data,
            tokenizer=tokenizer,
            text_column=text_column,
            input_column=input_column,
            target_column=target_column,
            max_length=max_length,
            pipeline_type=pipeline_type,
            is_chat_dataset=is_chat_dataset,
            chat_template=chat_template
        )
    
    # Prepare model for training
    if use_4bit:
        model = prepare_model_for_kbit_training(model)
    
    # Configure LoRA
    peft_config = LoraConfig(
        task_type=task_type,
        r=ft_config["lora_r"],
        lora_alpha=ft_config["lora_alpha"],
        lora_dropout=ft_config["lora_dropout"],
        target_modules=None,  # Auto-detect target modules
        bias="none"
    )
    
    # Get PEFT model
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=ft_config["batch_size"],
        gradient_accumulation_steps=ft_config["gradient_accumulation_steps"],
        learning_rate=ft_config["learning_rate"],
        weight_decay=weight_decay,
        warmup_ratio=warmup_ratio,
        logging_dir=f"{output_dir}/logs",
        logging_steps=logging_steps,
        save_strategy="steps",
        save_steps=eval_steps,
        evaluation_strategy="steps" if eval_dataset else "no",
        eval_steps=eval_steps if eval_dataset else None,
        load_best_model_at_end=True if eval_dataset else False,
        fp16=torch.cuda.is_available(),
        report_to="tensorboard",
    )
    
    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # Fine-tune model
    print(f"Starting fine-tuning of {model_name}...")
    trainer.train()
    
    # Save fine-tuned model and tokenizer
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print(f"Model fine-tuning complete. Saved to {output_dir}")
    
    return model, tokenizer

def batch_process(
    data: Union[Dataset, Dict, List],
    process_fn: Callable,
    batch_size: int = 8,
    text_column: str = "text",
    **kwargs
) -> List:
    """
    Process data in batches using the provided function.
    
    Args:
        data: Dataset to process
        process_fn: Function to apply to each batch
        batch_size: Size of each batch
        text_column: Column containing text data
        **kwargs: Additional arguments to pass to process_fn
        
    Returns:
        List of results from processing each batch
    """
    # Convert data to appropriate format
    if isinstance(data, dict):
        dataset = Dataset.from_dict(data)
    elif isinstance(data, list):
        # Assume list of strings or dicts
        if isinstance(data[0], str):
            dataset = Dataset.from_dict({text_column: data})
        else:
            dataset = Dataset.from_list(data)
    else:
        dataset = data
    
    # Create DataLoader
    dataloader = DataLoader(dataset, batch_size=batch_size)
    
    # Process batches
    results = []
    for batch in tqdm(dataloader, desc="Processing batches"):
        batch_result = process_fn(batch, **kwargs)
        results.extend(batch_result)
    
    return results

def evaluate_finetuned_model(
    model_path: str,
    eval_data: Union[Dataset, Dict, str],
    text_column: str = "text",
    label_column: str = "label",
    input_column: Optional[str] = None,
    target_column: Optional[str] = None,
    is_chat_dataset: bool = False,
    system_prompt: str = "You are a helpful assistant.",
    metric: str = "accuracy",
    device: Optional[str] = None,
    max_new_tokens: int = 20,
    batch_size: int = 4
) -> Dict[str, Any]:
    """
    Evaluate a fine-tuned model on a dataset.
    
    Args:
        model_path: Path to the fine-tuned model
        eval_data: Evaluation dataset
        text_column: Column containing text data
        label_column: Column containing ground truth labels
        input_column: Column containing input text
        target_column: Column containing target text
        is_chat_dataset: Whether dataset follows chat format
        system_prompt: System prompt for chat format
        metric: Evaluation metric (accuracy, f1, etc.)
        device: Computing device
        max_new_tokens: Maximum new tokens to generate
        batch_size: Batch size for evaluation
    
    Returns:
        Dictionary with evaluation results
    """
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # Determine if it's a seq2seq model based on directory contents
    is_seq2seq = False
    try:
        if os.path.exists(os.path.join(model_path, "encoder")):
            is_seq2seq = True
    except:
        pass
    
    # Load appropriate model type
    if is_seq2seq:
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        pipeline_type = "text2text-generation"
    else:
        model = AutoModelForCausalLM.from_pretrained(model_path)
        pipeline_type = "text-generation"
    
    # Determine device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
    model = model.to(device)
    
    # Load evaluation data
    if isinstance(eval_data, str):
        dataset = load_dataset(eval_data)["validation"]
    elif isinstance(eval_data, dict):
        dataset = Dataset.from_dict(eval_data)
    else:
        dataset = eval_data
    
    # Load metric
    metric_fn = evaluate.load(metric)
    
    # Define processing function for batches
    def process_batch(batch, **kwargs):
        predictions = []
        references = []
        
        for i in range(len(batch[text_column])):
            text = batch[text_column][i]
            
            # Determine input format based on model type
            if is_chat_dataset:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
                inputs = tokenizer.apply_chat_template(messages, tokenize=True, return_tensors="pt").to(device)
            elif input_column and input_column in batch:
                inputs = tokenizer(batch[input_column][i], return_tensors="pt").to(device)
            else:
                inputs = tokenizer(text, return_tensors="pt").to(device)
            
            # Generate output
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.0,
                    do_sample=False,
                    num_beams=1
                )
            
            # Decode prediction
            if pipeline_type == "text2text-generation":
                prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                # For text-generation, only return the new tokens
                input_length = inputs.input_ids.shape[1]
                prediction = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
            
            # Get reference
            if target_column and target_column in batch:
                reference = batch[target_column][i]
            else:
                reference = batch[label_column][i]
            
            predictions.append(prediction)
            references.append(reference)
        
        return [{"prediction": pred, "reference": ref} for pred, ref in zip(predictions, references)]
    
    # Process data in batches
    results = batch_process(
        dataset,
        process_fn=process_batch,
        batch_size=batch_size,
        text_column=text_column
    )
    
    # Extract predictions and references
    predictions = [r["prediction"] for r in results]
    references = [r["reference"] for r in results]
    
    # Calculate metric
    metric_result = metric_fn.compute(predictions=predictions, references=references)
    
    return {
        "model": model_path,
        "metric": metric,
        "results": metric_result,
        "predictions": predictions,
        "references": references
    }

# Example usage
if __name__ == "__main__":
    # Example dataset
    example_data = {
        "text": [
            "This movie was fantastic!",
            "I really hated the service.",
            "The food was just okay, nothing special.",
            "Best purchase I've made all year!"
        ],
        "label": ["positive", "negative", "neutral", "positive"]
    }
    
    # Example fine-tuning
    # model, tokenizer = finetune_llm(
    #     data=example_data,
    #     model_name="microsoft/phi-2",
    #     output_dir="./fine-tuned-sentiment-model",
    #     num_train_epochs=1,
    #     batch_size=2
    # )
    
    # Example evaluation
    # results = evaluate_finetuned_model(
    #     model_path="./fine-tuned-sentiment-model",
    #     eval_data=example_data,
    #     metric="accuracy"
    # )
    # print(f"Evaluation results: {results['results']}")
