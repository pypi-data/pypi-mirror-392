import os
import pandas as pd
import torch
from tqdm import tqdm
import evaluate

from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

# --- 1. CONFIGURATION ---

# Set this to True to train and evaluate a fine-tuned model.
# Set this to False to evaluate the zero-shot base model.
DO_FINETUNING = False
ZERO_SHOT = True

# --- Paths and Model Names ---
base_model_checkpoint = "google-t5/t5-base"
fine_tuned_model_path = "./fine-tuned-t5-translation" # Directory to save/load the fine-tuned model

# --- Device Setup ---
# To use a specific GPU (e.g., cuda:1), run script with: CUDA_VISIBLE_DEVICES=1 python your_script.py
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")


# --- 2. Load and Prepare the Dataset ---
# This step is the same for both workflows.
with open("fra.txt", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

english_texts_prefixed = ["translate English to French: " + line.split("\t")[0] for line in lines]
french_texts = [line.split("\t")[1] for line in lines]

# We need a consistent test set for fair comparison
train_en_prefixed, test_en_prefixed, train_fr, test_fr = train_test_split(
    english_texts_prefixed, french_texts, test_size=0.1, random_state=42
)

print(f"Dataset prepared: {len(train_en_prefixed)} training samples, {len(test_en_prefixed)} test samples.")


# --- 3. Fine-Tuning Workflow (if enabled) ---
if DO_FINETUNING:
    if not os.path.isdir(fine_tuned_model_path):
        print(f"No fine-tuned model found at '{fine_tuned_model_path}'. Starting training...")
        tokenizer = T5Tokenizer.from_pretrained(base_model_checkpoint)
        model = T5ForConditionalGeneration.from_pretrained(base_model_checkpoint)
        
        train_df = pd.DataFrame({"english_text": train_en_prefixed, "french_text": train_fr})
        test_df = pd.DataFrame({"english_text": test_en_prefixed, "french_text": test_fr})
        raw_datasets = DatasetDict({
            "train": Dataset.from_pandas(train_df),
            "test": Dataset.from_pandas(test_df)
        })

        def tokenize_function(examples):
            model_inputs = tokenizer(
                examples["english_text"], max_length=128, truncation=True, padding="max_length"
            )
            labels = tokenizer(
                text_target=examples["french_text"], max_length=128, truncation=True, padding="max_length"
            )
            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        tokenized_datasets = raw_datasets.map(tokenize_function, batched=True, remove_columns=["english_text", "french_text"])
        
        training_args = Seq2SeqTrainingArguments(
            output_dir="t5-training-checkpoints",
            eval_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            weight_decay=0.01,
            save_total_limit=3,
            num_train_epochs=3,
            predict_with_generate=True,
            fp16=torch.cuda.is_available(),
        )

        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["test"],
            tokenizer=tokenizer,
        )

        trainer.train()
        print(f"Training complete. Saving model to: {fine_tuned_model_path}")
        trainer.save_model(fine_tuned_model_path)
    else:
        print(f"Fine-tuned model already exists at '{fine_tuned_model_path}'. Skipping training.")


# --- 4. Model Loading for Evaluation ---
if DO_FINETUNING:
    model_to_evaluate_path = fine_tuned_model_path
    print(f"\n--- Loading FINE-TUNED model for evaluation ---")
else:
    if ZERO_SHOT:
        model_to_evaluate_path = base_model_checkpoint
        print(f"\n--- Loading ZERO-SHOT base model for evaluation ---")
    else:
        model_to_evaluate_path = fine_tuned_model_path
        print(f"\n--- Loading FINE-TUNED model for evaluation ---")

tokenizer = T5Tokenizer.from_pretrained(model_to_evaluate_path)
model = T5ForConditionalGeneration.from_pretrained(model_to_evaluate_path)
model.to(device)
model.eval()


# --- 5. Evaluation using Manual Generation Loop ---
batch_size = 32
hypotheses = []

print("Generating translations for the test set...")
with torch.no_grad():
    for i in tqdm(range(0, len(test_en_prefixed), batch_size)):
        batch = test_en_prefixed[i:i + batch_size]
        inputs = tokenizer(
            batch, return_tensors="pt", padding=True, truncation=True, max_length=128
        ).to(device)
        
        outputs = model.generate(
            **inputs, max_length=128, num_beams=4, early_stopping=True
        )
        
        decoded_preds = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        hypotheses.extend(decoded_preds)

# --- 6. Calculate and Display Results using 'evaluate' library ---

# Load the BLEU metric from the library
bleu_metric = evaluate.load("bleu")

# The 'evaluate' library expects references to be a list of lists.
# Since we have one reference per sentence, we wrap each one in a list.
references_for_eval = [[ref] for ref in test_fr]

# Compute the score
results = bleu_metric.compute(predictions=hypotheses, references=references_for_eval)

print("\n--- Evaluation Complete ---")
print(f"Model evaluated: {model_to_evaluate_path}")

# The result 'bleu' is a score from 0.0 to 1.0. We multiply by 100 for the standard 0-100 scale.
print(f"BLEU Score: {results['bleu'] * 100:.2f}")

# Print the full results dictionary for more details (precisions, etc.)
print("Full evaluation results:", results)

print("\n--- Sanity Check: Example Translations ---")
for i in range(5):
    print(f"Source:     {test_en_prefixed[i]}")
    print(f"Reference:  {test_fr[i]}")
    print(f"Prediction: {hypotheses[i]}\n")