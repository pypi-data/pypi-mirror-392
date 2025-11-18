"""
Neural network model implementations.
"""

from .resnet import (
    resnet18,
    resnet34,
    resnet50,
    resnet101,
    resnet152
)

from .resnetv2 import (
    resnetv2_18,
    resnetv2_34,
    resnetv2_50,
    resnetv2_101,
    resnetv2_152
)

from .inception_resnet import (
    inception_resnet_v1,
    inception_resnet_v2
)

from .text_lstm import TextLSTM

from .unet import (
    UNet,
    DoubleConv,
    Down,
    Up, 
    OutConv,
    train_unet
)

from .word2vec import (
    Word2Vec,
    Word2VecTrainer,
    train_word2vec
)

from .glove import (
    GloVeModel,
    GloVeTrainer,
    train_glove
)

from .hf_llm import (
    eval_llm,
    get_model_info as llm_get_model_info
)

from .hf_llm_ft import (
    finetune_llm,
    evaluate_finetuned_model,
    prepare_dataset,
    get_ft_config,
    batch_process
)

from .hf_vit import (
    load_vit,
    get_model_info as vit_get_model_info,
    train_vit,
    eval_vit
)

from .vae import (
    VAE,
    VAETrainer,
    visualize_vae,
    example_usage as vae_example_usage
)

from .gradboost import (
    GradientBooster,
    tune_hyperparameters,
    cross_validate,
    train_gradient_booster
)

from .tokenizer import (
    Tokenizer,
    clean_html,
    clean_urls,
    clean_emojis,
    clean_multiple_spaces,
    example_usage as tokenizer_example_usage
)

from .mlp import (
    MLP,
    MLPTrainer
)

from .seq2seq import (
    Encoder,
    Decoder,
    Attention,
    Seq2Seq,
    train_seq2seq,
    evaluate_seq2seq,
    example_usage as seq2seq_example_usage
)

from .hf_t import (
    load_transformer_model,
    finetune_transformer,
    predict_text_classification,
    evaluate_text_classification,
    load_and_finetune_transformer,
    prepare_dataset,
    example_usage as hf_t_example_usage,
    get_model_info as hf_t_get_model_info
)

__all__ = [
    # CNN models
    'resnet18',
    'resnet34',
    'resnet50',
    'resnet101',
    'resnet152',
    'resnetv2_18',
    'resnetv2_34',
    'resnetv2_50',
    'resnetv2_101',
    'resnetv2_152',
    'inception_resnet_v1',
    'inception_resnet_v2',
    
    # Text models
    'TextLSTM',
    
    # Image segmentation
    'UNet',
    'DoubleConv',
    'Down',
    'Up',
    'OutConv',
    'train_unet',
    
    # Word embeddings
    'Word2Vec',
    'Word2VecTrainer',
    'train_word2vec',
    'GloVeModel',
    'GloVeTrainer',
    'train_glove',
    
    # Tokenizer and text preprocessing
    'Tokenizer',
    'clean_html',
    'clean_urls',
    'clean_emojis',
    'clean_multiple_spaces',
    'tokenizer_example_usage',
    
    # LLM utilities
    'eval_llm',
    'llm_get_model_info',
    
    # LLM fine-tuning
    'finetune_llm',
    'evaluate_finetuned_model',
    'prepare_dataset',
    'get_ft_config',
    'batch_process',
    
    # Vision Transformer models
    'load_vit',
    'vit_get_model_info',
    'train_vit',
    'eval_vit',
    
    # Generative models
    'VAE',
    'VAETrainer',
    'visualize_vae',
    'vae_example_usage',
    
    # Gradient Boosting models
    'GradientBooster',
    'tune_hyperparameters',
    'cross_validate',
    'train_gradient_booster',
    
    # MLP models
    'MLP',
    'MLPTrainer',
    
    # Sequence-to-Sequence models
    'Encoder',
    'Decoder',
    'Attention',
    'Seq2Seq',
    'train_seq2seq',
    'evaluate_seq2seq',
    'seq2seq_example_usage',
    
    # Hugging Face Transformer for text classification
    'load_transformer_model',
    'finetune_transformer',
    'predict_text_classification',
    'evaluate_text_classification',
    'load_and_finetune_transformer',
    'prepare_dataset',
    'hf_t_example_usage',
    'hf_t_get_model_info'
]
