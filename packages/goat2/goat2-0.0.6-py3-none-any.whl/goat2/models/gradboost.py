"""
Gradient Boosting implementations using XGBoost and LightGBM with unified interfaces.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union, Optional, Tuple, Any, Callable
import matplotlib.pyplot as plt
import joblib
from collections import defaultdict
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV, KFold, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score, roc_auc_score
)
import xgboost as xgb
import lightgbm as lgb
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


class GradientBooster:
    """Base class for gradient boosting implementations"""
    
    def __init__(self, model_type: str = 'xgboost', task: str = 'classification', **kwargs):
        """
        Initialize a gradient boosting model
        
        Args:
            model_type: Type of model ('xgboost' or 'lightgbm')
            task: Type of task ('classification' or 'regression')
            kwargs: Additional parameters to pass to the model
        """
        self.model_type = model_type.lower()
        self.task = task.lower()
        self.model = None
        self.feature_names = None
        self.feature_importance = None
        
        # Configure default parameters based on task
        self.params = self._get_default_params()
        
        # Update with user-provided parameters
        self.params.update(kwargs)
        
        # Initialize the model
        self._initialize_model()
        
    def _get_default_params(self) -> Dict:
        """Get default parameters based on model type and task"""
        params = {}
        
        if self.task == 'classification':
            if self.model_type == 'xgboost':
                params = {
                    'objective': 'binary:logistic',
                    'eval_metric': 'logloss',
                    'learning_rate': 0.1,
                    'max_depth': 6,
                    'min_child_weight': 1,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'n_estimators': 100,
                    'use_label_encoder': False
                }
            elif self.model_type == 'lightgbm':
                params = {
                    'objective': 'binary',
                    'metric': 'binary_logloss',
                    'learning_rate': 0.1,
                    'max_depth': 6,
                    'num_leaves': 31,
                    'feature_fraction': 0.8,
                    'bagging_fraction': 0.8,
                    'n_estimators': 100
                }
        else:  # regression
            if self.model_type == 'xgboost':
                params = {
                    'objective': 'reg:squarederror',
                    'eval_metric': 'rmse',
                    'learning_rate': 0.1,
                    'max_depth': 6,
                    'min_child_weight': 1,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'n_estimators': 100
                }
            elif self.model_type == 'lightgbm':
                params = {
                    'objective': 'regression',
                    'metric': 'rmse',
                    'learning_rate': 0.1,
                    'max_depth': 6,
                    'num_leaves': 31,
                    'feature_fraction': 0.8,
                    'bagging_fraction': 0.8,
                    'n_estimators': 100
                }
                
        return params
        
    def _initialize_model(self):
        """Initialize the model based on type and parameters"""
        if self.model_type == 'xgboost':
            if self.task == 'classification':
                self.model = xgb.XGBClassifier(**self.params)
            else:
                self.model = xgb.XGBRegressor(**self.params)
        elif self.model_type == 'lightgbm':
            if self.task == 'classification':
                self.model = lgb.LGBMClassifier(**self.params)
            else:
                self.model = lgb.LGBMRegressor(**self.params)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}. Use 'xgboost' or 'lightgbm'.")
    
    def fit(self, 
            X: Union[np.ndarray, pd.DataFrame], 
            y: Union[np.ndarray, pd.Series],
            eval_set: Optional[List[Tuple[Any, Any]]] = None,
            early_stopping_rounds: Optional[int] = None,
            verbose: bool = True,
            feature_names: Optional[List[str]] = None):
        """
        Train the model
        
        Args:
            X: Training features
            y: Training labels
            eval_set: Evaluation data for early stopping
            early_stopping_rounds: Number of rounds for early stopping
            verbose: Whether to print training progress
            feature_names: Names of features (extracted from DataFrame if not provided)
        """
        # Extract feature names if available
        if feature_names is None and isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
        else:
            self.feature_names = feature_names
            
        # Prepare eval set for xgboost
        if eval_set is None and self.model_type == 'xgboost':
            # Create a validation set if not provided
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
            eval_set = [(X_val, y_val)]
            # Update X and y to be the training portion
            X, y = X_train, y_train
            
        # Fit the model
        if self.model_type == 'xgboost':
            self.model.fit(
                X, y,
                eval_set=eval_set,
                early_stopping_rounds=early_stopping_rounds,
                verbose=verbose
            )
        else:  # lightgbm
            self.model.fit(
                X, y,
                eval_set=eval_set,
                early_stopping_rounds=early_stopping_rounds,
                verbose=verbose
            )
            
        # Calculate feature importance
        self._calculate_feature_importance()
        
        return self
    
    def _calculate_feature_importance(self):
        """Calculate feature importance"""
        if self.model is None:
            raise ValueError("Model must be trained before calculating feature importance")
            
        importance = self.model.feature_importances_
        
        if self.feature_names is not None:
            self.feature_importance = {
                name: score for name, score in zip(self.feature_names, importance)
            }
        else:
            self.feature_importance = {
                f"feature_{i}": score for i, score in enumerate(importance)
            }
    
    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions with the trained model"""
        if self.model is None:
            raise ValueError("Model must be trained before making predictions")
            
        return self.model.predict(X)
    
    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Get probability predictions (for classification only)"""
        if self.task != 'classification':
            raise ValueError("predict_proba is only available for classification tasks")
            
        if self.model is None:
            raise ValueError("Model must be trained before making predictions")
            
        return self.model.predict_proba(X)
    
    def evaluate(self, 
                X: Union[np.ndarray, pd.DataFrame], 
                y: Union[np.ndarray, pd.Series]) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            X: Test features
            y: Test labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model must be trained before evaluation")
            
        y_pred = self.predict(X)
        
        # Calculate metrics based on task
        metrics = {}
        
        if self.task == 'classification':
            metrics['accuracy'] = accuracy_score(y, y_pred)
            metrics['precision'] = precision_score(y, y_pred, average='weighted')
            metrics['recall'] = recall_score(y, y_pred, average='weighted')
            metrics['f1'] = f1_score(y, y_pred, average='weighted')
            
            # Add ROC AUC for binary classification
            if len(np.unique(y)) == 2:
                y_prob = self.predict_proba(X)[:, 1]
                metrics['roc_auc'] = roc_auc_score(y, y_prob)
        else:  # regression
            metrics['mse'] = mean_squared_error(y, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])
            metrics['mae'] = mean_absolute_error(y, y_pred)
            metrics['r2'] = r2_score(y, y_pred)
            
        return metrics
    
    def plot_feature_importance(self, top_n: int = 20, figsize: Tuple[int, int] = (10, 6)):
        """
        Plot feature importance
        
        Args:
            top_n: Number of top features to show
            figsize: Figure size (width, height)
        """
        if self.feature_importance is None:
            raise ValueError("Feature importance must be calculated first")
            
        # Sort by importance
        importance_dict = dict(sorted(
            self.feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n])
        
        # Prepare for plotting
        features = list(importance_dict.keys())
        importance = list(importance_dict.values())
        
        # Create plot
        plt.figure(figsize=figsize)
        plt.barh(range(len(features)), importance, align='center')
        plt.yticks(range(len(features)), features)
        plt.xlabel('Importance')
        plt.ylabel('Feature')
        plt.title(f'Top {len(features)} Feature Importance ({self.model_type.capitalize()})')
        plt.tight_layout()
        plt.show()
    
    def save_model(self, filepath: str):
        """Save the model to a file"""
        if self.model is None:
            raise ValueError("Model must be trained before saving")
            
        # Save the model
        if self.model_type == 'xgboost':
            self.model.save_model(filepath)
        else:  # lightgbm
            self.model.booster_.save_model(filepath)
            
        # Save model metadata separately
        metadata = {
            'model_type': self.model_type,
            'task': self.task,
            'params': self.params,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance
        }
        
        metadata_path = f"{filepath}_metadata.pkl"
        joblib.dump(metadata, metadata_path)
        
        logging.info(f"Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str):
        """Load a saved model"""
        # Load metadata
        metadata_path = f"{filepath}_metadata.pkl"
        metadata = joblib.load(metadata_path)
        
        # Create new instance
        instance = cls(
            model_type=metadata['model_type'],
            task=metadata['task'],
            **metadata['params']
        )
        
        # Load the model
        if instance.model_type == 'xgboost':
            if instance.task == 'classification':
                instance.model = xgb.XGBClassifier()
            else:
                instance.model = xgb.XGBRegressor()
            instance.model.load_model(filepath)
        else:  # lightgbm
            if instance.task == 'classification':
                instance.model = lgb.LGBMClassifier(**instance.params)
            else:
                instance.model = lgb.LGBMRegressor(**instance.params)
            instance.model.booster_ = lgb.Booster(model_file=filepath)
        
        # Restore metadata
        instance.feature_names = metadata['feature_names']
        instance.feature_importance = metadata['feature_importance']
        
        return instance


def tune_hyperparameters(
    X: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    param_grid: Dict[str, List[Any]],
    model_type: str = 'xgboost',
    task: str = 'classification',
    cv: int = 5,
    scoring: Optional[str] = None,
    n_iter: Optional[int] = 10,
    random_search: bool = True,
    n_jobs: int = -1,
    verbose: int = 1
) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """
    Perform hyperparameter tuning for gradient boosting models
    
    Args:
        X: Training features
        y: Training labels
        param_grid: Dictionary of parameter grid
        model_type: Type of model ('xgboost' or 'lightgbm')
        task: Type of task ('classification' or 'regression')
        cv: Number of cross-validation folds
        scoring: Scoring metric
        n_iter: Number of iterations for random search
        random_search: Whether to use random search (True) or grid search (False)
        n_jobs: Number of parallel jobs
        verbose: Verbosity level
        
    Returns:
        Tuple of (best parameters, cross-validation results)
    """
    # Create base model for tuning
    model = GradientBooster(model_type=model_type, task=task)
    
    # Select appropriate cross-validation strategy
    if task == 'classification' and len(np.unique(y)) > 1:
        cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    else:
        cv_strategy = KFold(n_splits=cv, shuffle=True, random_state=42)
    
    # Choose default scoring metric if not provided
    if scoring is None:
        if task == 'classification':
            scoring = 'f1_weighted'
        else:
            scoring = 'neg_mean_squared_error'
    
    # Perform hyperparameter search
    if random_search:
        search = RandomizedSearchCV(
            model.model,
            param_distributions=param_grid,
            n_iter=n_iter,
            scoring=scoring,
            cv=cv_strategy,
            n_jobs=n_jobs,
            verbose=verbose,
            random_state=42
        )
    else:
        search = GridSearchCV(
            model.model,
            param_grid=param_grid,
            scoring=scoring,
            cv=cv_strategy,
            n_jobs=n_jobs,
            verbose=verbose
        )
    
    # Fit the search
    search.fit(X, y)
    
    logging.info(f"Best parameters: {search.best_params_}")
    logging.info(f"Best score: {search.best_score_:.4f}")
    
    return search.best_params_, search.cv_results_


def cross_validate(
    X: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    model_type: str = 'xgboost',
    task: str = 'classification',
    cv: int = 5,
    params: Optional[Dict[str, Any]] = None,
    verbose: bool = True
) -> Dict[str, List[float]]:
    """
    Perform cross-validation for gradient boosting models
    
    Args:
        X: Training features
        y: Training labels
        model_type: Type of model ('xgboost' or 'lightgbm')
        task: Type of task ('classification' or 'regression')
        cv: Number of cross-validation folds
        params: Model parameters
        verbose: Whether to print progress
        
    Returns:
        Dictionary of evaluation metrics for each fold
    """
    # Create parameter dictionary if not provided
    if params is None:
        params = {}
    
    # Select appropriate cross-validation strategy
    if task == 'classification' and len(np.unique(y)) > 1:
        kf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    else:
        kf = KFold(n_splits=cv, shuffle=True, random_state=42)
    
    # Prepare results storage
    results = defaultdict(list)
    
    # Extract feature names if available
    feature_names = None
    if isinstance(X, pd.DataFrame):
        feature_names = X.columns.tolist()
    
    # Perform cross-validation
    for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
        if verbose:
            logging.info(f"Training fold {fold+1}/{cv}")
        
        # Split data
        if isinstance(X, pd.DataFrame):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        else:
            X_train, X_val = X[train_idx], X[val_idx]
            
        if isinstance(y, pd.Series):
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        else:
            y_train, y_val = y[train_idx], y[val_idx]
        
        # Train model
        model = GradientBooster(model_type=model_type, task=task, **params)
        model.fit(
            X_train, y_train, 
            feature_names=feature_names,
            verbose=False
        )
        
        # Evaluate
        metrics = model.evaluate(X_val, y_val)
        
        # Store results
        for metric, value in metrics.items():
            results[metric].append(value)
    
    # Calculate averages
    for metric in results:
        results[f"avg_{metric}"] = np.mean(results[metric])
        results[f"std_{metric}"] = np.std(results[metric])
    
    if verbose:
        for metric in sorted([m for m in results if m.startswith('avg_')]):
            logging.info(f"{metric}: {results[metric]:.4f} (±{results[metric.replace('avg', 'std')]:.4f})")
    
    return results


def train_gradient_booster(
    X_train: Union[np.ndarray, pd.DataFrame],
    y_train: Union[np.ndarray, pd.Series],
    X_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
    y_test: Optional[Union[np.ndarray, pd.Series]] = None,
    model_type: str = 'xgboost',
    task: str = 'classification',
    params: Optional[Dict[str, Any]] = None,
    early_stopping_rounds: Optional[int] = 50,
    verbose: bool = True,
    save_path: Optional[str] = None
) -> Tuple[GradientBooster, Optional[Dict[str, float]]]:
    """
    Train a gradient boosting model and evaluate on test data if provided
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        model_type: Type of model ('xgboost' or 'lightgbm')
        task: Type of task ('classification' or 'regression')
        params: Model parameters
        early_stopping_rounds: Number of rounds for early stopping
        verbose: Whether to print progress
        save_path: Path to save the model
        
    Returns:
        Tuple of (trained model, evaluation metrics if test data provided)
    """
    # Create parameter dictionary if not provided
    if params is None:
        params = {}
    
    # Create and train model
    model = GradientBooster(model_type=model_type, task=task, **params)
    
    # Prepare eval set if test data provided
    eval_set = None
    if X_test is not None and y_test is not None:
        eval_set = [(X_test, y_test)]
    
    # Train the model
    model.fit(
        X_train, y_train,
        eval_set=eval_set,
        early_stopping_rounds=early_stopping_rounds,
        verbose=verbose
    )
    
    # Evaluate if test data provided
    metrics = None
    if X_test is not None and y_test is not None:
        metrics = model.evaluate(X_test, y_test)
        
        if verbose:
            for metric, value in metrics.items():
                logging.info(f"{metric}: {value:.4f}")
    
    # Save model if path provided
    if save_path:
        model.save_model(save_path)
    
    return model, metrics
