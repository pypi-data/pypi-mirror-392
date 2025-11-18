"""
Simple and concise implementations of gradient boosting models using XGBoost and LightGBM
for classification and regression tasks.
"""

import numpy as np
import xgboost as xgb
import lightgbm as lgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, roc_auc_score

def train_xgboost(X_train, y_train, X_val=None, y_val=None, params=None, num_rounds=100, task='classification'):
    """
    Train an XGBoost model.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features (optional)
        y_val: Validation labels (optional)
        params: Model parameters (dictionary)
        num_rounds: Number of boosting rounds
        task: 'classification' or 'regression'
    
    Returns:
        Trained XGBoost model
    """
    # Default parameters
    if params is None:
        params = {
            'max_depth': 6,
            'eta': 0.3,
            'objective': 'binary:logistic' if task == 'classification' else 'reg:squarederror',
            'eval_metric': 'logloss' if task == 'classification' else 'rmse',
            'silent': 1
        }
    
    # Convert data to DMatrix format
    dtrain = xgb.DMatrix(X_train, label=y_train)
    
    # Set up validation if provided
    evals = [(dtrain, 'train')]
    if X_val is not None and y_val is not None:
        dval = xgb.DMatrix(X_val, label=y_val)
        evals.append((dval, 'val'))
    
    # Train model
    model = xgb.train(params, dtrain, num_rounds, evals=evals, verbose_eval=10)
    return model

def train_lightgbm(X_train, y_train, X_val=None, y_val=None, params=None, num_rounds=100, task='classification'):
    """
    Train a LightGBM model.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features (optional)
        y_val: Validation labels (optional)
        params: Model parameters (dictionary)
        num_rounds: Number of boosting rounds
        task: 'classification' or 'regression'
    
    Returns:
        Trained LightGBM model
    """
    # Default parameters
    if params is None:
        params = {
            'boosting_type': 'gbdt',
            'objective': 'binary' if task == 'classification' else 'regression',
            'metric': 'binary_logloss' if task == 'classification' else 'rmse',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
        }
    
    # Convert data to LightGBM Dataset format
    train_data = lgb.Dataset(X_train, label=y_train)
    
    # Set up validation if provided
    valid_data = None
    if X_val is not None and y_val is not None:
        valid_data = lgb.Dataset(X_val, label=y_val)
    
    # Train model
    model = lgb.train(
        params,
        train_data,
        num_boost_round=num_rounds,
        valid_sets=[valid_data] if valid_data else None,
        callbacks=[lgb.log_evaluation(10)]
    )
    return model

def evaluate(model, X_test, y_test, model_type='xgboost', task='classification'):
    """
    Evaluate a trained gradient boosting model.
    
    Args:
        model: Trained model (XGBoost or LightGBM)
        X_test: Test features
        y_test: Test labels
        model_type: 'xgboost' or 'lightgbm'
        task: 'classification' or 'regression'
    
    Returns:
        Dictionary of evaluation metrics
    """
    if model_type.lower() == 'xgboost':
        dtest = xgb.DMatrix(X_test)
        y_pred = model.predict(dtest)
    else:  # lightgbm
        y_pred = model.predict(X_test)
    
    results = {}
    
    if task == 'classification':
        if model_type.lower() == 'xgboost':
            y_pred_class = (y_pred > 0.5).astype(int)
        else:
            y_pred_class = (y_pred > 0.5).astype(int)
        
        results['accuracy'] = accuracy_score(y_test, y_pred_class)
        results['auc'] = roc_auc_score(y_test, y_pred)
    else:  # regression
        results['mse'] = mean_squared_error(y_test, y_pred)
        results['rmse'] = np.sqrt(results['mse'])
    
    return results

def generate_data(n_samples=1000, task='classification'):
    """
    Generate sample data for demonstration.
    
    Args:
        n_samples: Number of samples
        task: 'classification' or 'regression'
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    if task == 'classification':
        X, y = make_classification(
            n_samples=n_samples, n_features=20, n_informative=10, 
            n_redundant=5, random_state=42
        )
    else:  # regression
        X, y = make_classification(
            n_samples=n_samples, n_features=20, n_informative=10, 
            n_redundant=5, random_state=42
        )
        # Convert to regression problem
        y = y + np.random.normal(0, 0.1, size=y.shape)
    
    return train_test_split(X, y, test_size=0.2, random_state=42)

def main():
    """Example usage of gradient boosting models."""
    # Generate sample data
    X_train, X_test, y_train, y_test = generate_data()
    
    print("Training XGBoost model...")
    xgb_model = train_xgboost(X_train, y_train)
    xgb_results = evaluate(xgb_model, X_test, y_test, model_type='xgboost')
    print(f"XGBoost results: {xgb_results}")
    
    print("\nTraining LightGBM model...")
    lgb_model = train_lightgbm(X_train, y_train)
    lgb_results = evaluate(lgb_model, X_test, y_test, model_type='lightgbm')
    print(f"LightGBM results: {lgb_results}")

if __name__ == "__main__":
    main()
