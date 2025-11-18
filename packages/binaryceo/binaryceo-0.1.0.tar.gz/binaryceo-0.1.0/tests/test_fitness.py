"""Tests for the fitness functions module."""

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.neighbors import KNeighborsClassifier

# Import the functions you're testing
from binaryceo.fitness import classification_fitness, multi_objective_fitness


@pytest.fixture(scope="module")
def fitness_data():
    """
    Create a small, shared dataset and model for testing fitness functions.
    This fixture is run once per module, saving time.
    """
    # Create a tiny, fast-to-process dataset
    X, y = make_classification(
        n_samples=50, n_features=10, n_informative=5, n_redundant=0, random_state=42
    )
    # Use the k-NN model from your presentation [cite: 81]
    model = KNeighborsClassifier(n_neighbors=3)

    # Return a dictionary for easy access in tests
    return {"X": X, "y": y, "model": model, "n_features": X.shape[1]}


class TestClassificationFitness:
    """Tests for the classification_fitness function."""

    def test_no_features_selected(self, fitness_data):
        """
        Test the critical edge case where no features are selected.
        Fitness must be 1.0 (worst possible).
        [cite: 599-601, 650-652]
        """
        position = np.zeros(fitness_data["n_features"], dtype=int)
        fitness = classification_fitness(position, **fitness_data)
        assert fitness == 1.0

    def test_all_features_selected(self, fitness_data):
        """
        Test with all features selected.
        Should return a valid fitness score between 0 and 1.
        """
        position = np.ones(fitness_data["n_features"], dtype=int)
        fitness = classification_fitness(position, **fitness_data)
        assert 0.0 <= fitness <= 1.0

    def test_some_features_selected(self, fitness_data):
        """
        Test with a partial feature set.
        Should return a valid fitness score.
        """
        position = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
        fitness = classification_fitness(position, **fitness_data)
        assert 0.0 <= fitness <= 1.0


class TestFitnessExceptionHandling:
    """Tests for exception handling in fitness functions."""

    def test_classification_fitness_exception_handling(self):
        """Test that classification_fitness handles exceptions gracefully."""

        # Create a mock model that will raise an exception
        class FailingModel:
            def fit(self, X, y):
                raise ValueError("Model training failed")

            def predict(self, X):
                raise ValueError("Model prediction failed")

        X, y = make_classification(n_samples=20, n_features=5, random_state=42)
        position = np.array([1, 1, 0, 1, 0])
        model = FailingModel()

        # Should handle exception and return worst fitness (1.0)
        fitness = classification_fitness(position, X=X, y=y, model=model, cv_folds=2)
        assert fitness == 1.0

    def test_multi_objective_fitness_exception_handling(self):
        """Test that multi_objective_fitness handles exceptions gracefully."""

        # Create a mock model that will raise an exception
        class FailingModel:
            def fit(self, X, y):
                raise RuntimeError("Critical model failure")

            def predict(self, X):
                raise RuntimeError("Critical prediction failure")

        X, y = make_classification(n_samples=20, n_features=5, random_state=42)
        position = np.array([1, 0, 1, 0, 1])
        model = FailingModel()

        # Should handle exception and return worst fitness (1.0)
        fitness = multi_objective_fitness(
            position, X=X, y=y, model=model, accuracy_weight=0.7, cv_folds=2
        )
        assert fitness == 1.0


class TestMultiObjectiveFitness:
    """Tests for the multi_objective_fitness (project-specific) function."""

    def test_no_features_selected(self, fitness_data):
        """
        Test the critical edge case. Fitness must be 1.0.
        [cite: 599-601, 650-652]
        """
        position = np.zeros(fitness_data["n_features"], dtype=int)
        fitness = multi_objective_fitness(position, **fitness_data)
        assert fitness == 1.0

    def test_balancing_logic(self, fitness_data):
        """
        Test the core multi-objective logic.
        We'll show that a solution with *worse* accuracy can win
        if it is *significantly* more sparse.
        """
        # Solution A: Good accuracy, 8 features
        # Manually set high-performing features
        pos_A = np.array([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])  # 8 features

        # Solution B: Bad accuracy, 2 features
        # Manually set low-performing features
        pos_B = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1])  # 2 features

        # --- Default weight (accuracy_weight=0.7) ---
        # We expect the good accuracy solution (A) to win
        fit_A_default = multi_objective_fitness(
            pos_A, **fitness_data, accuracy_weight=0.7
        )
        fit_B_default = multi_objective_fitness(
            pos_B, **fitness_data, accuracy_weight=0.7
        )

        # Note: With this dataset, pos_A is much better, so its fitness will be lower
        assert fit_A_default < fit_B_default

        # --- Sparsity-focused weight (accuracy_weight=0.1) ---
        # Now we *punish* feature count heavily.
        # Let's see if the very sparse solution (B) can beat A.

        fit_A_sparse_focus = multi_objective_fitness(
            pos_A, **fitness_data, accuracy_weight=0.1
        )
        fit_B_sparse_focus = multi_objective_fitness(
            pos_B, **fitness_data, accuracy_weight=0.1
        )

        # Even if B's error_rate is high, its sparsity_rate is low (0.2)
        # and A's sparsity_rate is high (0.8).
        # The 0.9*sparsity_rate penalty will likely make A's fitness higher (worse)
        # than B's.

        print(
            f"Focus Accuracy (A): {fit_A_default:.4f} | "
            f"Focus Sparsity (A): {fit_A_sparse_focus:.4f}"
        )
        print(
            f"Focus Accuracy (B): {fit_B_default:.4f} | "
            f"Focus Sparsity (B): {fit_B_sparse_focus:.4f}"
        )

        # This assert proves the weighting is working.
        # A wins when accuracy is key, B wins when sparsity is key.
        assert fit_A_sparse_focus > fit_B_sparse_focus
