from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM, pipeline
from tqdm import tqdm
from typing import Dict, Any, Optional, List, Union
import torch

# Dictionary of smaller LLMs with parameter counts (in billions), all under 5B
MODEL_PARAMS = {
    # Phi models (Microsoft)
    "microsoft/phi-1": 1.3,
    "microsoft/phi-1.5": 1.3,
    "microsoft/phi-2": 2.7,
    "microsoft/Phi-3-mini-4k-instruct": 3.8,
    "microsoft/Phi-3-mini-128k-instruct": 3.8,
    
    # Gemma models (Google)
    "google/gemma-2b": 2.0,
    "google/gemma-2b-it": 2.0,
    
    # TinyLlama models
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0": 1.1,
    "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T": 1.1,
    
    # Smaller Mistral models
    "mistralai/Mistral-7B-v0.1": 4.0,  # Quantized version
    
    # FLAN models
    "google/flan-t5-small": 0.08,
    "google/flan-t5-base": 0.25,
    "google/flan-t5-large": 0.8,
    
    # GPT-2 models (OpenAI)
    "gpt2": 0.124,
    "gpt2-medium": 0.355,
    "gpt2-large": 0.774,
    "gpt2-xl": 1.5,
    
    # GPT-Neo models (EleutherAI)
    "EleutherAI/gpt-neo-125m": 0.125,
    "EleutherAI/gpt-neo-1.3B": 1.3,
    "EleutherAI/gpt-neo-2.7B": 2.7,
    
    # Google T5 models
    "google-t5/t5-small": 0.06,
    "google-t5/t5-base": 0.22,
    "google-t5/t5-large": 0.77,
    "google-t5/t5-3b": 3.0,
    "google/t5-v1_1-small": 0.06,
    "google/t5-v1_1-base": 0.22,
    "google/t5-v1_1-large": 0.77,
    "google/t5-v1_1-xl": 3.0,
    
    # Additional BLOOM models
    "bigscience/bloom-560m": 0.56,
    "bigscience/bloom-1b1": 1.1,
    "bigscience/bloom-1b7": 1.7,
    "bigscience/bloomz-560m": 0.56,
    "bigscience/bloomz-1b1": 1.1,
    "bigscience/bloomz-1b7": 1.7,
    
    # Smaller OPT models
    "facebook/opt-125m": 0.125,
    "facebook/opt-350m": 0.35,
    "facebook/opt-1.3b": 1.3,
    "facebook/opt-2.7b": 2.7,
}

# Dictionary mapping models to their appropriate pipeline type
MODEL_PIPELINES = {
    # Models that use text-generation pipeline (decoder-only models)
    "microsoft/phi": "text-generation",
    "google/gemma": "text-generation",
    "TinyLlama": "text-generation",
    "mistralai": "text-generation",
    "gpt2": "text-generation",
    "EleutherAI/gpt-neo": "text-generation",
    "bigscience/bloom": "text-generation",
    "bigscience/bloomz": "text-generation",
    "facebook/opt": "text-generation",
    
    # Models that use text2text-generation pipeline (encoder-decoder models)
    "t5": "text2text-generation",
    "google/flan-t5": "text2text-generation",
    "google-t5": "text2text-generation",
    "google/t5": "text2text-generation",
}

def get_pipeline_type(model_name: str) -> str:
    """
    Determine the appropriate pipeline type for a given model.
    
    Args:
        model_name: The HuggingFace model identifier
        
    Returns:
        Pipeline type: either "text-generation" or "text2text-generation"
    """
    for prefix, pipeline_type in MODEL_PIPELINES.items():
        if prefix.lower() in model_name.lower():
            return pipeline_type
    
    # Default to text-generation if no match is found
    return "text-generation"

def get_model_info(model_name: Optional[str] = None) -> Union[Dict[str, float], float]:
    """
    Get parameter count information for LLMs.
    
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

def eval_llm(
    data: Any,
    text_column: str = 'text',
    label_column: str = 'label',
    system_prompt: str = "You are a classifier that outputs exactly one word or phrase from a fixed set of options.",
    task_prompt: str = "Classify the following text into exactly one of these categories: {labels}. Text: ",
    model_name: str = "microsoft/Phi-3-mini-4k-instruct",
    stride: int = 1,
    device: Optional[str] = None,
    max_new_tokens: int = 10,
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Evaluate text classification using zero-shot prompting with an LLM.
    
    Args:
        data: DataFrame or dictionary containing text data and labels
        text_column: Name of the column containing text to classify
        label_column: Name of the column containing ground truth labels
        system_prompt: System prompt for the model
        task_prompt: Prompt template for the classification task (use {labels} to insert options)
        model_name: HuggingFace model identifier
        stride: Process every nth sample
        device: Computing device (auto-detected if None)
        max_new_tokens: Maximum new tokens to generate
        labels: List of possible label values (if None, will be extracted from data)
        
    Returns:
        Dictionary with evaluation metrics
    """
    # Determine device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Extract unique labels if not provided
    if labels is None:
        if isinstance(data, dict):
            labels = list(set(data[label_column]))
        else:  # DataFrame or similar
            labels = list(set(data[label_column].iloc if hasattr(data[label_column], 'iloc') else data[label_column]))
    
    # Format labels as a comma-separated string
    labels_str = ", ".join([f'"{label}"' for label in labels])
    
    # Replace {labels} placeholder in task prompt
    task_prompt = task_prompt.format(labels=labels_str)
    
    # Determine pipeline type
    pipeline_type = get_pipeline_type(model_name)
    print(f"Loading {model_name} ({get_model_info(model_name)}B parameters) with {pipeline_type} pipeline...")
    
    # Initialize model and tokenizer based on pipeline type
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    if pipeline_type == "text2text-generation":
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True).to(device)
    else:  # text-generation
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).to(device)
    
    # Create the appropriate pipeline
    classification_pipe = pipeline(
        pipeline_type,
        model=model,
        tokenizer=tokenizer,
        device=0 if device == "cuda" else -1
    )
    
    # Configure generation parameters for deterministic output
    gen_config = {
        "max_new_tokens": max_new_tokens,
        "temperature": 0.0,  # Zero temperature for deterministic output
        "do_sample": False,  # Don't sample
        "num_beams": 1,      # No beam search needed for deterministic output
        "top_p": 1.0,        # No nucleus sampling
        "top_k": 0,          # No top-k filtering
        "repetition_penalty": 1.0,  # No repetition penalty
    }
    
    # Add pipeline-specific config
    if pipeline_type == "text-generation":
        gen_config["return_full_text"] = False
    
    # Get data length depending on the data type
    if hasattr(data, '__len__'):
        data_length = len(data)
    else:
        data_length = len(data[text_column])
    
    # Evaluate
    correct, total = 0, 0
    predictions = []
    
    for i in tqdm(range(0, data_length, stride)):
        # Access text based on data type
        if isinstance(data, dict):
            text = data[text_column][i]
            true_label = data[label_column][i]
        else:  # DataFrame or similar
            text = data[text_column].iloc[i] if hasattr(data[text_column], 'iloc') else data[text_column][i]
            true_label = data[label_column].iloc[i] if hasattr(data[label_column], 'iloc') else data[label_column][i]
        
        # Format input based on pipeline type
        if pipeline_type == "text2text-generation":
            # For encoder-decoder models, combine system and task prompt
            input_text = f"{system_prompt}\n{task_prompt}{text}"
            raw_prediction = classification_pipe(input_text, **gen_config)[0]['generated_text']
        else:
            # For decoder-only models, use message format
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{task_prompt}{text}"},
            ]
            raw_prediction = classification_pipe(messages, **gen_config)[0]['generated_text']
        
        # Clean prediction to match expected format (remove extra spaces, quotes, periods)
        prediction = raw_prediction.strip().strip('"\'.,').lower()
        
        # For exact matching, we also convert true label to lowercase
        true_label_str = str(true_label).lower()
        
        # Store prediction
        predictions.append(prediction)
        
        # Check if prediction matches true label
        if prediction in true_label_str or true_label_str in prediction:
            correct += 1
        total += 1
    
    # Calculate accuracy
    accuracy = correct / total if total > 0 else 0
    
    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "model": model_name,
        "params_billions": get_model_info(model_name),
        "pipeline_type": pipeline_type,
        "predictions": predictions
    }


# Example usage:
if __name__ == "__main__":
    # Print available models
    print("Available models (all under 5B parameters):")
    for model, params in sorted(get_model_info().items(), key=lambda x: x[1]):
        print(f"- {model}: {params}B parameters")
    
    # Example for sentiment classification
    # results = eval_llm(
    #     data=validation_data,
    #     system_prompt="You are a classifier that outputs exactly one word from the provided options. No explanations.",
    #     task_prompt="Classify the following text as either \"positive\" or \"negative\". Only respond with one word. Text: ",
    #     model_name="microsoft/Phi-3-mini-4k-instruct",
    #     labels=["positive", "negative"]
    # )
    # print(f"Accuracy: {results['accuracy']:.2%} ({results['correct']}/{results['total']})")
