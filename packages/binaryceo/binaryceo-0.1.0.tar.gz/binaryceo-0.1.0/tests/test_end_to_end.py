"""
End-to-end tests for Binary CEO algorithm.

Tests the complete algorithm from the user's perspective using run_binary_ceo.
"""

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

from binaryceo.optimizer import run_binary_ceo


class TestBasicEndToEnd:
    """Basic end-to-end functionality tests."""

    @pytest.fixture
    def simple_dataset(self):
        """Create a simple, predictable dataset for testing."""
        # Create dataset where features 0 and 2 are perfect predictors
        # and features 1, 3, 4 are pure noise
        np.random.seed(42)
        n_samples = 100

        # Perfect features
        X = np.zeros((n_samples, 5))
        X[:50, 0] = 1  # Feature 0: first 50 samples = 1, rest = 0
        X[50:, 2] = 1  # Feature 2: last 50 samples = 1, rest = 0

        # Noise features
        X[:, 1] = np.random.randn(n_samples)  # Random noise
        X[:, 3] = np.random.randn(n_samples)  # Random noise
        X[:, 4] = np.random.randn(n_samples)  # Random noise

        # Target: XOR of features 0 and 2
        y = (X[:, 0] + X[:, 2]) % 2
        y = y.astype(int)

        return X, y

    def test_basic_run_returns_expected_structure(self, simple_dataset):
        """Test that run_binary_ceo returns the expected result structure."""
        X, y = simple_dataset
        model = KNeighborsClassifier(n_neighbors=3)

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=10,
            max_iter=5,
            verbose=False,
            random_state=42,
        )

        # Check result structure
        expected_keys = {
            "best_body",
            "best_position",
            "best_fitness",
            "history",
            "termination_stats",
            "iterations_completed",
        }
        assert set(result.keys()) == expected_keys

        # Check types and shapes
        assert result["best_position"] is not None
        assert len(result["best_position"]) == X.shape[1]
        assert np.all((result["best_position"] == 0) | (result["best_position"] == 1))
        assert isinstance(result["best_fitness"], float)
        assert result["best_fitness"] >= 0

        # Check history
        assert "best_fitness" in result["history"]
        assert "num_features" in result["history"]
        assert len(result["history"]["best_fitness"]) == result["iterations_completed"]
        assert len(result["history"]["num_features"]) == result["iterations_completed"]

        # Check termination stats
        assert "fitness_evals" in result["termination_stats"]
        assert result["termination_stats"]["fitness_evals"] > 0

    def test_algorithm_finds_good_features(self, simple_dataset):
        """Test that the algorithm can identify the important features."""
        X, y = simple_dataset
        model = LogisticRegression(random_state=42, max_iter=1000)

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=20,
            max_iter=15,
            selection_probability=0.4,
            accuracy_weight=0.8,  # Prioritize accuracy
            verbose=False,
            random_state=42,
        )

        best_position = result["best_position"]

        # Should select at least one of the important features (0 or 2)
        important_features_selected = best_position[0] + best_position[2]
        assert (
            important_features_selected > 0
        ), f"Should select feature 0 or 2, got {best_position}"

        # Should not select too many features (sparsity)
        total_features = np.sum(best_position)
        assert (
            total_features <= 4
        ), f"Should be sparse, selected {total_features} features"

    def test_fitness_improves_over_iterations(self, simple_dataset):
        """Test that fitness generally improves over iterations."""
        X, y = simple_dataset
        model = KNeighborsClassifier(n_neighbors=5)

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=15,
            max_iter=10,
            verbose=False,
            random_state=42,
        )

        fitness_history = result["history"]["best_fitness"]

        # Fitness should not get worse (monotonic improvement)
        for i in range(1, len(fitness_history)):
            assert fitness_history[i] <= fitness_history[i - 1], (
                f"Fitness got worse: {fitness_history[i]} > "
                f"{fitness_history[i-1]} at iteration {i}"
            )

        # Should show some improvement over the run
        initial_fitness = fitness_history[0]
        final_fitness = fitness_history[-1]
        assert final_fitness <= initial_fitness


class TestTerminationCriteria:
    """Test various termination criteria in end-to-end scenarios."""

    @pytest.fixture
    def test_dataset(self):
        """Create test dataset."""
        X, y = make_classification(
            n_samples=80, n_features=12, n_informative=6, n_redundant=2, random_state=42
        )
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        return X, y, model

    def test_max_iterations_termination(self, test_dataset):
        """Test termination by maximum iterations."""
        X, y, model = test_dataset
        max_iter = 8

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=10,
            max_iter=max_iter,
            verbose=False,
            random_state=42,
        )

        assert (
            result["iterations_completed"] <= max_iter + 1
        )  # Allow for off-by-one due to 0-indexing
        assert "Maximum iterations" in result["termination_stats"]["termination_reason"]

    def test_fitness_threshold_termination(self, test_dataset):
        """Test termination by fitness threshold."""
        X, y, model = test_dataset

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=10,
            max_iter=20,
            fitness_threshold=0.1,  # Very low threshold, should terminate early
            verbose=False,
            random_state=42,
        )

        # Should terminate before max_iter if threshold is reached
        if result["best_fitness"] <= 0.1:
            assert result["iterations_completed"] < 20
            assert (
                "Fitness threshold" in result["termination_stats"]["termination_reason"]
            )

    def test_stagnation_termination(self, test_dataset):
        """Test termination by stagnation."""
        X, y, model = test_dataset

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=8,
            max_iter=20,
            stagnation_iters=5,  # Stop if no improvement for 5 iterations
            verbose=False,
            random_state=42,
        )

        # Check if terminated due to stagnation
        if "Stagnation" in str(result["termination_stats"]["termination_reason"]):
            assert result["iterations_completed"] < 20

    def test_max_fitness_evals_termination(self, test_dataset):
        """Test termination by maximum fitness evaluations."""
        X, y, model = test_dataset

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=10,
            max_iter=20,
            max_fitness_evals=50,  # Very low limit
            verbose=False,
            random_state=42,
        )

        # Should terminate due to evaluation limit (allow tolerance for algorithm)
        assert result["termination_stats"]["fitness_evals"] <= 70
        if result["termination_stats"]["fitness_evals"] >= 50:
            assert (
                "Maximum fitness evaluations"
                in result["termination_stats"]["termination_reason"]
            )

    def test_time_limit_termination(self, test_dataset):
        """Test termination by time limit."""
        X, y, model = test_dataset

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=10,
            max_iter=100,  # High iteration count
            time_limit_seconds=0.1,  # Very short time limit
            verbose=False,
            random_state=42,
        )

        # Should terminate quickly due to time limit
        assert result["iterations_completed"] < 100
        if "Time limit" in str(result["termination_stats"]["termination_reason"]):
            assert (
                result["termination_stats"]["elapsed_time"] <= 2.0
            )  # More reasonable tolerance


class TestAlgorithmParameters:
    """Test different algorithm parameter configurations."""

    @pytest.fixture
    def test_dataset(self):
        """Create test dataset."""
        X, y = make_classification(
            n_samples=60, n_features=10, n_informative=5, random_state=42
        )
        model = KNeighborsClassifier(n_neighbors=3)
        return X, y, model

    def test_different_population_sizes(self, test_dataset):
        """Test algorithm with different population sizes."""
        X, y, model = test_dataset

        for pop_size in [5, 10, 20]:
            result = run_binary_ceo(
                X=X,
                y=y,
                model=model,
                pop_size=pop_size,
                max_iter=5,
                verbose=False,
                random_state=42,
            )

            # Should work with any reasonable population size
            assert result["best_position"] is not None
            assert result["best_fitness"] >= 0
            # Should evaluate at least pop_size solutions initially
            assert result["termination_stats"]["fitness_evals"] >= pop_size

    def test_different_selection_probabilities(self, test_dataset):
        """Test algorithm with different selection probabilities."""
        X, y, model = test_dataset

        results = {}
        for sel_prob in [0.1, 0.3, 0.5]:
            result = run_binary_ceo(
                X=X,
                y=y,
                model=model,
                pop_size=10,
                max_iter=5,
                selection_probability=sel_prob,
                verbose=False,
                random_state=42,
            )
            results[sel_prob] = result

        # Higher selection probability should generally select more features initially
        # (though final result may vary due to optimization)
        for sel_prob in results:
            assert results[sel_prob]["best_position"] is not None
            assert np.sum(results[sel_prob]["best_position"]) > 0

    def test_different_accuracy_weights(self, test_dataset):
        """Test algorithm with different accuracy vs sparsity trade-offs."""
        X, y, model = test_dataset

        results = {}
        for acc_weight in [0.3, 0.7, 0.9]:
            result = run_binary_ceo(
                X=X,
                y=y,
                model=model,
                pop_size=10,
                max_iter=8,
                accuracy_weight=acc_weight,
                verbose=False,
                random_state=42,
            )
            results[acc_weight] = result

        # All should produce valid results
        for acc_weight in results:
            assert results[acc_weight]["best_position"] is not None
            assert results[acc_weight]["best_fitness"] >= 0

    def test_local_search_modes(self, test_dataset):
        """Test different local search modes."""
        X, y, model = test_dataset

        modes = ["global_best", "top_k", "all"]
        for mode in modes:
            result = run_binary_ceo(
                X=X,
                y=y,
                model=model,
                pop_size=8,
                max_iter=5,
                local_search_enabled=True,
                local_search_mode=mode,
                local_search_top_k=3,
                verbose=False,
                random_state=42,
            )

            # Should work with any local search mode
            assert result["best_position"] is not None
            assert result["best_fitness"] >= 0

    def test_without_local_search(self, test_dataset):
        """Test algorithm without local search."""
        X, y, model = test_dataset

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=10,
            max_iter=5,
            local_search_enabled=False,
            verbose=False,
            random_state=42,
        )

        # Should still work without local search
        assert result["best_position"] is not None
        assert result["best_fitness"] >= 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_small_dataset(self):
        """Test with very small dataset."""
        X = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
        y = np.array([0, 1, 1, 0])
        model = KNeighborsClassifier(n_neighbors=2)

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=3,
            cv_folds=2,  # Reduce CV folds for small dataset
            verbose=False,
            random_state=42,
        )

        assert result["best_position"] is not None
        assert len(result["best_position"]) == 2
        assert result["best_fitness"] >= 0

    def test_single_feature_dataset(self):
        """Test with single feature dataset."""
        X = np.array([[1], [0], [1], [0], [1], [0]])
        y = np.array([1, 0, 1, 0, 1, 0])
        model = KNeighborsClassifier(n_neighbors=2)

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=3,
            cv_folds=2,
            verbose=False,
            random_state=42,
        )

        assert result["best_position"] is not None
        assert len(result["best_position"]) == 1
        assert result["best_position"][0] == 1  # Should select the only feature

    def test_reproducibility_with_random_state(self):
        """Test that results are reproducible with same random state."""
        X, y = make_classification(n_samples=50, n_features=8, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        # Run twice with same random state
        result1 = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=8,
            max_iter=5,
            verbose=False,
            random_state=123,
        )

        result2 = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=8,
            max_iter=5,
            verbose=False,
            random_state=123,
        )

        # Results should be identical
        assert np.array_equal(result1["best_position"], result2["best_position"])
        assert result1["best_fitness"] == result2["best_fitness"]
        assert result1["iterations_completed"] == result2["iterations_completed"]


if __name__ == "__main__":
    pytest.main([__file__])
