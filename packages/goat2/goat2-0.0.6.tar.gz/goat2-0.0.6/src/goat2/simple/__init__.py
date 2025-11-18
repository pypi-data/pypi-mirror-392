"""
Simple models and utilities for text and image classification tasks.

This package provides implementation of:
- Text classification: LSTM-based models and utilities
- Image classification: ResNet-based models and CIFAR-10 utilities
- Gradient Boosting: XGBoost and LightGBM implementations
- Pandas operations: Common data manipulation functionalities
- Scikit-learn models: Various ML model implementations and utilities
"""

# Import text classification components
from .textclass import (
    TextDataset,
    BiLSTMClassifier,
    train as train_text,
    evaluate as evaluate_text,
    generate_data as generate_text_data
)

# Import image classification components
from .imgclass import (
    load_cifar10,
    train as train_img,
    evaluate as evaluate_img
)

# Import gradient boosting components
from .gb import (
    train_xgboost,
    train_lightgbm,
    evaluate as evaluate_gb,
    generate_data as generate_gb_data
)

# Import pandas utilities
from .pd import (
    create_sample_dataframe,
    basic_exploration,
    filtering_and_selection,
    grouping_and_aggregation,
    handle_missing_data,
    merging_and_joining,
    data_transformation,
    time_series_operations
)

# Import scikit-learn utilities
from .sklearn import (
    load_sample_data,
    data_preprocessing_example,
    classification_models_example,
    regression_models_example,
    cross_validation_example,
    hyperparameter_tuning_example,
    feature_selection_example,
    pipeline_example
)

__all__ = [
    # Text classification
    'TextDataset',
    'BiLSTMClassifier',
    'train_text',
    'evaluate_text',
    'generate_text_data',
    
    # Image classification
    'load_cifar10',
    'train_img',
    'evaluate_img',
    
    # Gradient Boosting
    'train_xgboost',
    'train_lightgbm',
    'evaluate_gb',
    'generate_gb_data',
    
    # Pandas utilities
    'create_sample_dataframe',
    'basic_exploration',
    'filtering_and_selection',
    'grouping_and_aggregation',
    'handle_missing_data',
    'merging_and_joining',
    'data_transformation',
    'time_series_operations',
    
    # Scikit-learn utilities
    'load_sample_data',
    'data_preprocessing_example',
    'classification_models_example',
    'regression_models_example',
    'cross_validation_example',
    'hyperparameter_tuning_example',
    'feature_selection_example',
    'pipeline_example'
]
