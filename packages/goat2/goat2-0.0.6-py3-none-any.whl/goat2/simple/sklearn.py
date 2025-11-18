"""
Practical examples of scikit-learn usage for machine learning.
This module demonstrates:
- Data preprocessing
- Model training and evaluation
- Cross-validation
- Hyperparameter tuning
- Feature selection
- Working with pipelines
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets, metrics, model_selection

# Model imports
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier

# Preprocessing imports
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif, f_regression, RFE

def load_sample_data(dataset_name='iris'):
    """Load and prepare a sample dataset."""
    print(f"Loading {dataset_name} dataset...")
    
    if dataset_name == 'iris':
        data = datasets.load_iris()
        X, y = data.data, data.target
        feature_names = data.feature_names
        target_names = data.target_names
        task = 'classification'
        
    elif dataset_name == 'boston':
        data = datasets.fetch_california_housing()
        X, y = data.data, data.target
        feature_names = data.feature_names
        target_names = ['housing_price']
        task = 'regression'
        
    elif dataset_name == 'digits':
        data = datasets.load_digits()
        X, y = data.data, data.target
        feature_names = [f'pixel_{i}' for i in range(X.shape[1])]
        target_names = [str(i) for i in range(10)]
        task = 'classification'
        
    elif dataset_name == 'breast_cancer':
        data = datasets.load_breast_cancer()
        X, y = data.data, data.target
        feature_names = data.feature_names
        target_names = data.target_names
        task = 'classification'
        
    else:
        raise ValueError(f"Dataset '{dataset_name}' not supported")
    
    print(f"Dataset shape: {X.shape}")
    print(f"Task type: {task}")
    print(f"Number of classes: {len(target_names)}" if task == 'classification' else "Regression task")
    
    return X, y, feature_names, target_names, task

def data_preprocessing_example(X, numeric_features=None, categorical_features=None):
    """Demonstrate data preprocessing techniques."""
    print("\n=== Data Preprocessing Examples ===")
    
    # If features are not specified, assume all are numeric
    if numeric_features is None:
        numeric_features = list(range(X.shape[1]))
    
    if categorical_features is None:
        categorical_features = []
    
    # Basic scaling
    print("\nStandard scaling (z-score normalization):")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print(f"Original data mean: {X.mean(axis=0)[:3]}...")
    print(f"Original data std: {X.std(axis=0)[:3]}...")
    print(f"Scaled data mean: {X_scaled.mean(axis=0)[:3]}...")
    print(f"Scaled data std: {X_scaled.std(axis=0)[:3]}...")
    
    # MinMax scaling
    print("\nMinMax scaling (to [0,1] range):")
    min_max_scaler = MinMaxScaler()
    X_minmax = min_max_scaler.fit_transform(X)
    print(f"Scaled data min: {X_minmax.min(axis=0)[:3]}...")
    print(f"Scaled data max: {X_minmax.max(axis=0)[:3]}...")
    
    # Creating a preprocessing pipeline
    print("\nCreating a preprocessing pipeline:")
    
    # For a mixed dataset with numeric and categorical features
    if len(categorical_features) > 0:
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        print("Created a pipeline for mixed numeric/categorical data")
    else:
        # For numeric-only data
        preprocessor = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        print("Created a pipeline for numeric-only data")
    
    # Inject some missing values to demonstrate imputation
    X_with_missing = X.copy()
    rng = np.random.RandomState(42)
    n_samples, n_features = X.shape
    mask = rng.choice([True, False], size=n_samples * n_features, p=[0.1, 0.9])
    mask = mask.reshape(n_samples, n_features)
    X_with_missing[mask] = np.nan
    
    print(f"\nData with artificially injected missing values:")
    print(f"Missing values count: {np.isnan(X_with_missing).sum()}")
    
    X_preprocessed = preprocessor.fit_transform(X_with_missing)
    print(f"Preprocessed data shape: {X_preprocessed.shape}")
    print(f"Any missing values after preprocessing: {np.isnan(X_preprocessed).sum()}")
    
    return preprocessor, X_preprocessed

def classification_models_example(X, y):
    """Demonstrate various classification models."""
    print("\n=== Classification Models Example ===")
    
    # Split data
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Define models to test
    classifiers = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(3),
        "SVM (linear)": SVC(kernel="linear", C=1, random_state=42),
        "SVM (RBF)": SVC(gamma=2, C=1, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42),
        "Neural Net": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
        "Naive Bayes": GaussianNB()
    }
    
    # Train and evaluate each model
    results = {}
    for name, clf in classifiers.items():
        print(f"\nTraining {name}...")
        clf.fit(X_train, y_train)
        
        # Predictions
        y_pred = clf.predict(X_test)
        
        # Evaluate
        accuracy = metrics.accuracy_score(y_test, y_pred)
        f1 = metrics.f1_score(y_test, y_pred, average='weighted')
        
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 Score: {f1:.4f}")
        
        # Store results
        results[name] = {
            'model': clf,
            'accuracy': accuracy,
            'f1': f1
        }
    
    # Find best model
    best_model_name = max(results, key=lambda x: results[x]['accuracy'])
    print(f"\nBest model: {best_model_name} with accuracy: {results[best_model_name]['accuracy']:.4f}")
    
    return results

def regression_models_example(X, y):
    """Demonstrate regression models."""
    print("\n=== Regression Models Example ===")
    
    # Split data
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Define regression models
    regressors = {
        "Linear Regression": LinearRegression(),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42)
    }
    
    # Train and evaluate each model
    results = {}
    for name, reg in regressors.items():
        print(f"\nTraining {name}...")
        reg.fit(X_train, y_train)
        
        # Predictions
        y_pred = reg.predict(X_test)
        
        # Evaluate
        mse = metrics.mean_squared_error(y_test, y_pred)
        r2 = metrics.r2_score(y_test, y_pred)
        
        print(f"MSE: {mse:.4f}")
        print(f"R² Score: {r2:.4f}")
        
        # Store results
        results[name] = {
            'model': reg,
            'mse': mse,
            'r2': r2
        }
    
    # Find best model
    best_model_name = max(results, key=lambda x: results[x]['r2'])
    print(f"\nBest model: {best_model_name} with R²: {results[best_model_name]['r2']:.4f}")
    
    return results

def cross_validation_example(X, y, task='classification'):
    """Demonstrate cross-validation techniques."""
    print("\n=== Cross-Validation Example ===")
    
    if task == 'classification':
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        scoring = 'accuracy'
    else:  # regression
        model = GradientBoostingRegressor(random_state=42)
        scoring = 'neg_mean_squared_error'
    
    # K-Fold Cross-Validation
    print("\nK-Fold Cross-Validation:")
    cv_scores = model_selection.cross_val_score(
        model, X, y, cv=5, scoring=scoring
    )
    
    if task == 'classification':
        print(f"Cross-validated accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    else:
        print(f"Cross-validated neg MSE: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Stratified K-Fold (for classification)
    if task == 'classification':
        print("\nStratified K-Fold Cross-Validation:")
        skf = model_selection.StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = model_selection.cross_val_score(
            model, X, y, cv=skf, scoring=scoring
        )
        print(f"Stratified CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Time series split (for time series data)
    print("\nTime Series Split (for demonstration):")
    tscv = model_selection.TimeSeriesSplit(n_splits=5)
    cv_scores = model_selection.cross_val_score(
        model, X, y, cv=tscv, scoring=scoring
    )
    
    if task == 'classification':
        print(f"Time series CV accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    else:
        print(f"Time series CV neg MSE: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    return cv_scores

def hyperparameter_tuning_example(X, y, task='classification'):
    """Demonstrate hyperparameter tuning."""
    print("\n=== Hyperparameter Tuning Example ===")
    
    # Split data
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    if task == 'classification':
        model = RandomForestClassifier(random_state=42)
        param_grid = {
            'n_estimators': [10, 50, 100],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        }
        scoring = 'accuracy'
    else:  # regression
        model = GradientBoostingRegressor(random_state=42)
        param_grid = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7]
        }
        scoring = 'neg_mean_squared_error'
    
    # Grid Search
    print("\nGrid Search:")
    grid_search = model_selection.GridSearchCV(
        model, param_grid, cv=5, scoring=scoring
    )
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    # Evaluate on test set
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    
    if task == 'classification':
        test_score = metrics.accuracy_score(y_test, y_pred)
        print(f"Test accuracy with best model: {test_score:.4f}")
    else:
        test_score = metrics.mean_squared_error(y_test, y_pred)
        print(f"Test MSE with best model: {test_score:.4f}")
    
    # Random Search
    print("\nRandom Search (faster alternative):")
    random_search = model_selection.RandomizedSearchCV(
        model, param_grid, n_iter=5, cv=5, scoring=scoring, random_state=42
    )
    random_search.fit(X_train, y_train)
    
    print(f"Best parameters: {random_search.best_params_}")
    print(f"Best cross-validation score: {random_search.best_score_:.4f}")
    
    return grid_search, random_search

def feature_selection_example(X, y, feature_names, task='classification'):
    """Demonstrate feature selection techniques."""
    print("\n=== Feature Selection Example ===")
    
    # Univariate feature selection
    print("\nUnivariate Feature Selection:")
    if task == 'classification':
        selector = SelectKBest(f_classif, k=min(3, len(feature_names)))
    else:  # regression
        selector = SelectKBest(f_regression, k=min(3, len(feature_names)))
    
    X_new = selector.fit_transform(X, y)
    
    # Get selected feature indices and names
    selected_indices = selector.get_support(indices=True)
    selected_features = [feature_names[i] for i in selected_indices]
    
    print(f"Selected features: {selected_features}")
    print(f"Feature scores: {selector.scores_[selected_indices]}")
    
    # Recursive Feature Elimination
    print("\nRecursive Feature Elimination:")
    if task == 'classification':
        model = RandomForestClassifier(random_state=42)
    else:  # regression
        model = LinearRegression()
    
    rfe = RFE(estimator=model, n_features_to_select=min(3, len(feature_names)))
    rfe.fit(X, y)
    
    # Get selected feature indices and names
    rfe_selected = [i for i, selected in enumerate(rfe.support_) if selected]
    rfe_selected_features = [feature_names[i] for i in rfe_selected]
    
    print(f"Selected features: {rfe_selected_features}")
    print(f"Feature ranking (lower is better): {rfe.ranking_}")
    
    # Feature importance from tree-based models
    print("\nFeature Importance from Random Forest:")
    if task == 'classification':
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
    else:  # regression
        rf = GradientBoostingRegressor(n_estimators=100, random_state=42)
    
    rf.fit(X, y)
    
    # Get feature importance
    importances = rf.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print("Feature ranking by importance:")
    for i, idx in enumerate(indices[:min(5, len(feature_names))]):
        print(f"{i+1}. {feature_names[idx]} ({importances[idx]:.4f})")
    
    return {
        'univariate': {
            'selector': selector,
            'selected_features': selected_features
        },
        'rfe': {
            'selector': rfe,
            'selected_features': rfe_selected_features
        },
        'importance': {
            'model': rf,
            'importances': importances,
            'ranked_features': [feature_names[i] for i in indices]
        }
    }

def pipeline_example(X, y, task='classification'):
    """Demonstrate scikit-learn pipeline usage."""
    print("\n=== Pipeline Example ===")
    
    # Split data
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Create a pipeline with preprocessing and model
    if task == 'classification':
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('feature_selection', SelectKBest(f_classif, k=min(5, X.shape[1]))),
            ('classifier', RandomForestClassifier(random_state=42))
        ])
        
        # Parameters to tune
        param_grid = {
            'feature_selection__k': [2, 3, 4] if X.shape[1] >= 4 else [2],
            'classifier__n_estimators': [10, 50],
            'classifier__max_depth': [None, 10]
        }
        
        scoring = 'accuracy'
        
    else:  # regression
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('feature_selection', SelectKBest(f_regression, k=min(5, X.shape[1]))),
            ('regressor', GradientBoostingRegressor(random_state=42))
        ])
        
        # Parameters to tune
        param_grid = {
            'feature_selection__k': [2, 3, 4] if X.shape[1] >= 4 else [2],
            'regressor__n_estimators': [50, 100],
            'regressor__learning_rate': [0.01, 0.1]
        }
        
        scoring = 'neg_mean_squared_error'
    
    # Grid search with cross-validation
    print("\nGrid search with pipeline:")
    grid_search = model_selection.GridSearchCV(
        pipeline, param_grid, cv=3, scoring=scoring
    )
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    # Evaluate on test set
    best_pipeline = grid_search.best_estimator_
    y_pred = best_pipeline.predict(X_test)
    
    if task == 'classification':
        test_score = metrics.accuracy_score(y_test, y_pred)
        print(f"Test accuracy with best pipeline: {test_score:.4f}")
        print("\nClassification report:")
        print(metrics.classification_report(y_test, y_pred))
    else:
        test_score = metrics.mean_squared_error(y_test, y_pred)
        r2 = metrics.r2_score(y_test, y_pred)
        print(f"Test MSE with best pipeline: {test_score:.4f}")
        print(f"Test R² with best pipeline: {r2:.4f}")
    
    return best_pipeline, test_score

def main():
    """Run various scikit-learn examples."""
    # Load data
    X, y, feature_names, target_names, task = load_sample_data('iris')
    
    # Run examples
    preprocessor, X_preprocessed = data_preprocessing_example(X)
    
    if task == 'classification':
        model_results = classification_models_example(X, y)
    else:
        model_results = regression_models_example(X, y)
    
    cv_scores = cross_validation_example(X, y, task)
    grid_search, random_search = hyperparameter_tuning_example(X, y, task)
    feature_selection_results = feature_selection_example(X, y, feature_names, task)
    best_pipeline, test_score = pipeline_example(X, y, task)
    
    print("\n=== Summary ===")
    print(f"Completed examples for {task} on sample dataset")
    print(f"Final model test score: {test_score:.4f}")

if __name__ == "__main__":
    main()
