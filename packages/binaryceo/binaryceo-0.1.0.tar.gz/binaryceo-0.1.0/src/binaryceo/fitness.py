"""
Standard fitness functions for BinaryCEO.

These functions are designed to be passed to the initialization
and optimization modules. They adhere to the required signature:
    fitness_func(position, **kwargs) -> float

Where lower fitness is always better (minimization).
"""

import numpy as np
from sklearn.model_selection import cross_val_score


def classification_fitness(
    position: np.ndarray,
    X: np.ndarray,
    y: np.ndarray,
    model: object,
    cv_folds: int = 3,
    **kwargs,
) -> float:
    """
    Calculates fitness based *only* on classification error.

    This is a basic fitness function useful for testing the algorithm's
    ability to optimize for accuracy alone.

    Args:
        position: The binary solution vector.
        X: Feature matrix (from **kwargs).
        y: Target labels (from **kwargs).
        model: A scikit-learn compatible classifier (from **kwargs).
        cv_folds: Number of cross-validation folds.
        **kwargs: Catches any other arguments.

    Returns:
        float: The classification error (1 - accuracy).
    """
    # Step 1: Get selected features
    selected_indices = np.where(position == 1)[0]

    # Step 2: Handle edge case: no features selected
    if len(selected_indices) == 0:
        return 1.0  # Return worst possible fitness

    # Step 3: Subset data
    X_selected = X[:, selected_indices]

    # Step 4: Evaluate with cross-validation
    try:
        scores = cross_val_score(model, X_selected, y, cv=cv_folds, scoring="accuracy")
        accuracy = np.mean(scores)

        # Step 5: Return error rate (lower is better)
        return 1 - accuracy

    except Exception as e:
        # Handle cases where model training fails (e.g., single class in fold)
        print(f"Fitness evaluation failed: {e}")
        return 1.0  # Return worst fitness on error


def multi_objective_fitness(
    position: np.ndarray,
    X: np.ndarray,
    y: np.ndarray,
    model: object,
    cv_folds: int = 3,
    accuracy_weight: float = 0.7,
    **kwargs,
) -> float:
    """
    Calculates fitness based on a weighted sum of two objectives:
    1. Classification Error (to be minimized)
    2. Sparsity Rate (number of features, to be minimized)

    This function directly implements the multi-objective goal
    of your project.

    Args:
        position: The binary solution vector.
        X: Feature matrix (from **kwargs).
        y: Target labels (from **kwargs).
        model: A scikit-learn compatible classifier (from **kwargs).
        cv_folds: Number of cross-validation folds.
        accuracy_weight: The balance between accuracy and sparsity (alpha).
        **kwargs: Catches any other arguments.

    Returns:
        float: The combined, weighted fitness score (lower is better).
    """
    # Step 1: Get selected features
    selected_indices = np.where(position == 1)[0]

    # Step 2: Handle edge case: no features selected
    if len(selected_indices) == 0:
        return 1.0  # Return worst possible fitness

    # Step 3: Subset data and get feature counts
    X_selected = X[:, selected_indices]
    n_total_features = X.shape[1]
    n_selected = len(selected_indices)

    # Step 4: Evaluate Objectives
    try:
        # Objective 1: Classification Error
        scores = cross_val_score(model, X_selected, y, cv=cv_folds, scoring="accuracy")
        accuracy = np.mean(scores)
        error_rate = 1 - accuracy

        # Objective 2: Sparsity Rate
        sparsity_rate = n_selected / n_total_features

        # Step 5: Combine objectives with weighting
        sparsity_weight = 1.0 - accuracy_weight

        fitness = (accuracy_weight * error_rate) + (sparsity_weight * sparsity_rate)

        return fitness

    except Exception as e:
        # Handle cases where model training fails
        print(f"Fitness evaluation failed: {e}")
        return 1.0  # Return worst fitness on error
