import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

from binaryceo.optimizer import run_binary_ceo


@pytest.mark.parametrize("local_mode", ["global_best", "top_k", "all"])
def test_run_binary_ceo_basic(local_mode):
    """
    Smoke test: run the full BinaryCEO loop for a few iterations with
    different local_search_mode values and ensure the outputs are sane.
    This will cover most of optimizer.py.
    """
    # Tiny synthetic dataset for speed
    X, y = make_classification(
        n_samples=60,
        n_features=8,
        n_informative=4,
        n_redundant=0,
        n_repeated=0,
        random_state=0,
    )

    model = LogisticRegression(max_iter=500, solver="liblinear")

    result = run_binary_ceo(
        X=X,
        y=y,
        model=model,
        pop_size=8,
        max_iter=3,
        n_systems=2,
        partition_method="distance_based",
        selection_probability=0.3,
        continuous_init="random",
        continuous_range=(-1.0, 1.0),
        min_features=1,
        accuracy_weight=0.8,
        cv_folds=3,
        local_search_enabled=True,
        local_search_mode=local_mode,
        local_search_top_k=2,
        random_state=42,
        verbose=False,  # keep tests quiet
    )

    # Basic structure checks
    assert "best_body" in result
    assert "best_position" in result
    assert "best_fitness" in result
    assert "history" in result

    best_pos = result["best_position"]
    best_fit = result["best_fitness"]
    history = result["history"]

    # best_position should be a binary vector of correct length
    assert isinstance(best_pos, np.ndarray)
    assert best_pos.shape == (X.shape[1],)
    assert set(np.unique(best_pos)).issubset({0, 1})

    # fitness should be a finite float
    assert isinstance(best_fit, float)
    assert np.isfinite(best_fit)

    # history lengths should match iterations completed
    assert len(history["best_fitness"]) == result["iterations_completed"]
    assert len(history["num_features"]) == result["iterations_completed"]

    # number of selected features should always be between 1 and n_features
    for n_sel in history["num_features"]:
        assert 1 <= n_sel <= X.shape[1]


def test_run_binary_ceo_reproducible():
    """
    With a fixed random_state, BinaryCEO should be reproducible:
    same best_position and best_fitness across runs.
    """
    X, y = make_classification(
        n_samples=40,
        n_features=6,
        n_informative=3,
        n_redundant=0,
        n_repeated=0,
        random_state=1,
    )

    model = LogisticRegression(max_iter=500, solver="liblinear")

    kwargs = dict(
        X=X,
        y=y,
        model=model,
        pop_size=6,
        max_iter=4,
        n_systems=2,
        partition_method="distance_based",
        selection_probability=0.4,
        continuous_init="random",
        continuous_range=(-1.0, 1.0),
        min_features=1,
        accuracy_weight=0.7,
        cv_folds=3,
        local_search_enabled=True,
        local_search_mode="global_best",
        local_search_top_k=2,
        random_state=123,  # important for reproducibility
        verbose=False,
    )

    result1 = run_binary_ceo(**kwargs)
    result2 = run_binary_ceo(**kwargs)

    pos1 = result1["best_position"]
    pos2 = result2["best_position"]
    fit1 = result1["best_fitness"]
    fit2 = result2["best_fitness"]

    # Exactly same mask and (almost) same fitness
    assert np.array_equal(pos1, pos2)
    assert pytest.approx(fit1, rel=1e-9) == fit2


class TestOptimizerVerboseOutput:
    """Tests for verbose output in optimizer."""

    def test_verbose_output_messages(self, capsys):
        """Test that verbose mode produces expected output."""
        X, y = make_classification(n_samples=30, n_features=5, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        _ = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=2,
            verbose=True,  # Enable verbose output
            random_state=42,
        )

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Initializing population" in captured.out
        assert "Iteration" in captured.out
        assert "Best fitness:" in captured.out
        assert "Total fitness evaluations:" in captured.out

    def test_verbose_termination_reason_output(self, capsys):
        """Test verbose output for termination reason."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        _ = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=2,  # Will terminate due to max iterations
            verbose=True,
            random_state=42,
        )

        # Check that termination reason was printed
        captured = capsys.readouterr()
        assert "Maximum iterations" in captured.out


class TestOptimizerErrorHandling:
    """Tests for error handling in optimizer."""

    def test_invalid_local_search_mode(self):
        """Test that invalid local search mode raises ValueError."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        with pytest.raises(ValueError, match="Unknown local_search_mode"):
            run_binary_ceo(
                X=X,
                y=y,
                model=model,
                pop_size=4,
                max_iter=1,
                local_search_enabled=True,
                local_search_mode="invalid_mode",  # Invalid mode
                verbose=False,
                random_state=42,
            )


class TestOptimizerEdgeCases:
    """Tests for edge cases in optimizer."""

    def test_global_best_with_none_position(self):
        """Test handling when global best has None position."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        # This should handle the case where global_best_body.position might be None
        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=1,
            verbose=False,
            random_state=42,
        )

        # Should still produce valid results
        assert result["best_position"] is not None
        assert result["best_fitness"] >= 0

    def test_termination_criteria_integration(self):
        """Test integration with various termination criteria."""
        X, y = make_classification(n_samples=30, n_features=6, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        # Test with stagnation termination
        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=6,
            max_iter=20,
            stagnation_iters=5,  # Should terminate if no improvement
            verbose=False,
            random_state=42,
        )

        assert "termination_stats" in result
        assert result["termination_stats"]["termination_reason"] is not None

    def test_fitness_threshold_termination(self):
        """Test termination by fitness threshold."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=20,
            fitness_threshold=0.8,  # High threshold, likely to terminate early
            verbose=False,
            random_state=42,
        )

        # Should have termination stats
        assert "termination_stats" in result
        assert result["iterations_completed"] <= 20

    def test_max_fitness_evals_termination(self):
        """Test termination by maximum fitness evaluations."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=20,
            max_fitness_evals=20,  # Low limit
            verbose=False,
            random_state=42,
        )

        # Should terminate due to evaluation limit
        assert result["termination_stats"]["fitness_evals"] <= 25  # Some tolerance

    def test_different_continuous_init_strategies(self):
        """Test different continuous initialization strategies."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        strategies = ["from_position", "random", "zero"]

        for strategy in strategies:
            result = run_binary_ceo(
                X=X,
                y=y,
                model=model,
                pop_size=4,
                max_iter=2,
                continuous_init=strategy,
                verbose=False,
                random_state=42,
            )

            # Should work with any strategy
            assert result["best_position"] is not None
            assert result["best_fitness"] >= 0

    def test_different_partition_methods(self):
        """Test different partitioning methods."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        methods = ["fitness_based", "distance_based", "random"]

        for method in methods:
            result = run_binary_ceo(
                X=X,
                y=y,
                model=model,
                pop_size=6,
                max_iter=2,
                partition_method=method,
                verbose=False,
                random_state=42,
            )

            # Should work with any method
            assert result["best_position"] is not None
            assert result["best_fitness"] >= 0

    def test_custom_position_update_params(self):
        """Test with custom position update parameters."""
        X, y = make_classification(n_samples=20, n_features=4, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        custom_params = {
            "c1": 0.8,
            "c2": 0.3,
            "a": 1.5,
            "W1": 0.2,
            "lb": -3.0,
            "ub": 3.0,
        }

        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=4,
            max_iter=2,
            position_update_params=custom_params,
            verbose=False,
            random_state=42,
        )

        # Should work with custom parameters
        assert result["best_position"] is not None
        assert result["best_fitness"] >= 0

    def test_edge_case_none_position_handling(self):
        """Test the edge case where global_best_body.position might be None."""
        X, y = make_classification(
            n_samples=15,
            n_features=5,
            n_informative=2,
            n_redundant=0,
            n_repeated=0,
            random_state=42,
        )
        model = KNeighborsClassifier(n_neighbors=2)

        # Run with small population to potentially trigger edge cases
        result = run_binary_ceo(
            X=X,
            y=y,
            model=model,
            pop_size=2,
            max_iter=1,
            verbose=False,
            random_state=42,
        )

        # Should handle any edge cases gracefully
        assert result["best_position"] is not None
        assert result["best_fitness"] >= 0
        assert "history" in result
        assert len(result["history"]["num_features"]) > 0
