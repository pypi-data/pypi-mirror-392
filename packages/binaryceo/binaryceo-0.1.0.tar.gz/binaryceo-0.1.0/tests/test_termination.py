"""Tests for termination module."""

import numpy as np

from binaryceo import (
    CelestialBody,
    TerminationCriteria,
    calculate_population_diversity,
    early_stopping_check,
    simple_termination_check,
)


class TestCalculatePopulationDiversity:
    """Tests for population diversity calculation."""

    def test_identical_population_has_zero_diversity(self):
        """Test that identical solutions have diversity = 0."""
        # Create 3 identical bodies
        position = np.array([1, 0, 1, 0, 1])
        bodies = [
            CelestialBody(
                position=position.copy(),
                continuous_position=np.array([1.0, -1.0, 1.0, -1.0, 1.0]),
                fitness=0.5,
            )
            for _ in range(3)
        ]

        diversity = calculate_population_diversity(bodies)
        assert diversity == 0.0

    def test_completely_different_population(self):
        """Test that maximally different solutions have high diversity."""
        # Create bodies with different positions
        bodies = [
            CelestialBody(
                position=np.array([1, 1, 1, 1, 1]),
                continuous_position=np.array([1.0, 1.0, 1.0, 1.0, 1.0]),
                fitness=0.1,
            ),
            CelestialBody(
                position=np.array([0, 0, 0, 0, 0]),
                continuous_position=np.array([-1.0, -1.0, -1.0, -1.0, -1.0]),
                fitness=0.2,
            ),
        ]

        diversity = calculate_population_diversity(bodies)
        assert diversity == 1.0  # All features different between the two bodies

    def test_single_body_has_full_diversity(self):
        """Test that single body returns diversity = 1.0."""
        body = CelestialBody(
            position=np.array([1, 0, 1, 0]),
            continuous_position=np.array([1.0, -1.0, 1.0, -1.0]),
            fitness=0.5,
        )

        diversity = calculate_population_diversity([body])
        assert diversity == 1.0

    def test_diversity_range(self):
        """Test that diversity is always in [0, 1] range."""
        # Create random population
        bodies = [
            CelestialBody(
                position=np.random.randint(0, 2, size=10),
                continuous_position=np.random.uniform(-2, 2, size=10),
                fitness=np.random.rand(),
            )
            for _ in range(5)
        ]

        diversity = calculate_population_diversity(bodies)
        assert 0.0 <= diversity <= 1.0


class TestSimpleTerminationCheck:
    """Tests for simple termination check function."""

    def test_max_iterations_reached(self):
        """Test termination when max iterations reached."""
        assert (
            simple_termination_check(
                iteration=100, max_iter=100, global_best_fitness=0.5
            )
            is True
        )

    def test_max_iterations_not_reached(self):
        """Test no termination when iterations under limit."""
        assert (
            simple_termination_check(
                iteration=50, max_iter=100, global_best_fitness=0.5
            )
            is False
        )

    def test_fitness_threshold_reached(self):
        """Test termination when fitness threshold reached."""
        assert (
            simple_termination_check(
                iteration=10,
                max_iter=100,
                global_best_fitness=0.01,
                fitness_threshold=0.05,
            )
            is True
        )

    def test_fitness_threshold_not_reached(self):
        """Test no termination when fitness above threshold."""
        assert (
            simple_termination_check(
                iteration=10,
                max_iter=100,
                global_best_fitness=0.10,
                fitness_threshold=0.05,
            )
            is False
        )


class TestEarlyStoppingCheck:
    """Tests for early stopping check function."""

    def test_early_stopping_no_improvement(self):
        """Test early stopping triggers with no improvement."""
        # Fitness stays at 0.5 for 10 iterations
        fitness_history = [0.5] * 11

        assert (
            early_stopping_check(
                fitness_history=fitness_history, patience=10, min_delta=1e-6
            )
            is True
        )

    def test_early_stopping_with_improvement(self):
        """Test no early stopping when improvement happens."""
        # Fitness improves from 0.5 to 0.3
        fitness_history = [0.5] * 5 + [0.3] * 6

        assert (
            early_stopping_check(
                fitness_history=fitness_history, patience=10, min_delta=1e-6
            )
            is False
        )

    def test_early_stopping_insufficient_history(self):
        """Test no early stopping with short history."""
        fitness_history = [0.5, 0.5, 0.5]

        assert (
            early_stopping_check(
                fitness_history=fitness_history, patience=10, min_delta=1e-6
            )
            is False
        )


class TestTerminationCriteria:
    """Tests for TerminationCriteria class."""

    def test_initialization(self):
        """Test basic initialization."""
        criteria = TerminationCriteria(
            max_iter=100, fitness_threshold=0.05, stagnation_iters=20
        )

        assert criteria.max_iter == 100
        assert criteria.fitness_threshold == 0.05
        assert criteria.stagnation_iters == 20

    def test_reset(self):
        """Test that reset clears internal state."""
        criteria = TerminationCriteria(max_iter=100, verbose=False)

        # Simulate some iterations
        criteria.should_terminate(0, 0.5)
        criteria.should_terminate(1, 0.4)

        # Reset
        criteria.reset()

        stats = criteria.get_statistics()
        assert len(stats["best_fitness_history"]) == 0
        assert stats["last_improvement_iter"] == 0

    def test_max_iterations_termination(self):
        """Test termination by max iterations."""
        criteria = TerminationCriteria(max_iter=10, verbose=False)

        # Should not terminate before max_iter
        for i in range(10):
            result = criteria.should_terminate(i, 0.5)
            assert result is False

        # Should terminate at max_iter
        result = criteria.should_terminate(10, 0.5)
        assert result is True
        assert "Maximum iterations" in criteria.get_termination_reason()

    def test_fitness_threshold_termination(self):
        """Test termination by fitness threshold."""
        criteria = TerminationCriteria(
            max_iter=100, fitness_threshold=0.05, verbose=False
        )

        # Should not terminate with high fitness
        assert criteria.should_terminate(0, 0.5) is False

        # Should terminate when threshold reached
        assert criteria.should_terminate(1, 0.04) is True
        assert "Fitness threshold" in criteria.get_termination_reason()

    def test_stagnation_termination(self):
        """Test termination by stagnation."""
        criteria = TerminationCriteria(max_iter=100, stagnation_iters=5, verbose=False)

        # No improvement for 5 iterations
        for i in range(6):
            result = criteria.should_terminate(i, 0.5)

        # Should terminate due to stagnation
        assert result is True
        assert "Stagnation" in criteria.get_termination_reason()

    def test_diversity_termination(self):
        """Test termination by low diversity."""
        criteria = TerminationCriteria(max_iter=100, min_diversity=0.1, verbose=False)

        # Create low diversity population (all identical)
        position = np.array([1, 0, 1, 0, 1])
        low_diversity_pop = [
            CelestialBody(
                position=position.copy(),
                continuous_position=np.array([1.0, -1.0, 1.0, -1.0, 1.0]),
                fitness=0.5,
            )
            for _ in range(3)
        ]

        result = criteria.should_terminate(
            iteration=0, global_best_fitness=0.5, population=low_diversity_pop
        )

        assert result is True
        assert "Low diversity" in criteria.get_termination_reason()

    def test_fitness_eval_count_termination(self):
        """Test termination by max fitness evaluations."""
        criteria = TerminationCriteria(
            max_iter=100, max_fitness_evals=50, verbose=False
        )

        # Increment fitness evals
        for _ in range(50):
            criteria.increment_fitness_evals()

        result = criteria.should_terminate(0, 0.5)

        assert result is True
        assert "Maximum fitness evaluations" in criteria.get_termination_reason()

    def test_time_limit_termination(self):
        """Test termination by time limit."""
        import time

        criteria = TerminationCriteria(
            max_iter=100, time_limit_seconds=0.1, verbose=False  # 100ms
        )

        criteria.start_timing()

        # Should not terminate immediately
        assert criteria.should_terminate(0, 0.5) is False

        # Wait for time limit to expire
        time.sleep(0.15)

        # Should terminate after time limit
        assert criteria.should_terminate(1, 0.5) is True
        assert "Time limit" in criteria.get_termination_reason()

    def test_improvement_tracking(self):
        """Test that improvement is correctly tracked."""
        criteria = TerminationCriteria(max_iter=100, verbose=False)

        # Improving fitness
        criteria.should_terminate(0, 0.5)
        criteria.should_terminate(1, 0.4)  # Improvement
        criteria.should_terminate(2, 0.3)  # Improvement

        stats = criteria.get_statistics()
        assert stats["last_improvement_iter"] == 2

    def test_get_statistics(self):
        """Test statistics retrieval."""
        criteria = TerminationCriteria(max_iter=100, verbose=False)

        # Run a few iterations
        criteria.should_terminate(0, 0.5)
        criteria.should_terminate(1, 0.4)
        criteria.increment_fitness_evals(10)

        stats = criteria.get_statistics()

        assert stats["fitness_evals"] == 10
        assert len(stats["best_fitness_history"]) == 2
        assert stats["best_fitness_history"] == [0.5, 0.4]
        assert stats["last_improvement_iter"] == 1

    def test_get_statistics_with_timing(self):
        """Test statistics retrieval with elapsed time."""
        criteria = TerminationCriteria(max_iter=100, verbose=False)

        # Start timing
        criteria.start_timing()

        # Run a few iterations
        criteria.should_terminate(0, 0.5)
        criteria.should_terminate(1, 0.4)

        stats = criteria.get_statistics()

        # Should include elapsed_time when timing was started
        assert "elapsed_time" in stats
        assert stats["elapsed_time"] >= 0

    def test_multiple_criteria_simultaneously(self):
        """Test using multiple termination criteria at once."""
        criteria = TerminationCriteria(
            max_iter=100, fitness_threshold=0.05, stagnation_iters=10, verbose=False
        )

        # Should terminate by fitness threshold first
        criteria.should_terminate(0, 0.5)
        result = criteria.should_terminate(1, 0.01)

        assert result is True
        assert "Fitness threshold" in criteria.get_termination_reason()


class TestTerminationVerboseOutput:
    """Tests for verbose output in termination criteria."""

    def test_verbose_max_iterations_output(self, capsys):
        """Test verbose output for max iterations termination."""
        criteria = TerminationCriteria(max_iter=2, verbose=True)

        # Should terminate at max_iter with verbose output
        assert criteria.should_terminate(2, 0.5) is True

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Maximum iterations" in captured.out

    def test_verbose_fitness_threshold_output(self, capsys):
        """Test verbose output for fitness threshold termination."""
        criteria = TerminationCriteria(
            max_iter=100, fitness_threshold=0.1, verbose=True
        )

        # Should terminate with verbose output
        assert criteria.should_terminate(0, 0.05) is True

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Fitness threshold" in captured.out

    def test_verbose_stagnation_output(self, capsys):
        """Test verbose output for stagnation termination."""
        criteria = TerminationCriteria(max_iter=100, stagnation_iters=3, verbose=True)

        # Create stagnation scenario
        for i in range(4):
            result = criteria.should_terminate(i, 0.5)

        # Should terminate due to stagnation
        assert result is True

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Stagnation" in captured.out

    def test_verbose_diversity_output(self, capsys):
        """Test verbose output for diversity termination."""
        criteria = TerminationCriteria(max_iter=100, min_diversity=0.5, verbose=True)

        # Create low diversity population
        position = np.array([1, 0, 1])
        low_diversity_pop = [
            CelestialBody(
                position=position.copy(),
                continuous_position=np.array([1.0, -1.0, 1.0]),
                fitness=0.5,
            )
            for _ in range(3)
        ]

        # Should terminate due to low diversity
        assert criteria.should_terminate(0, 0.5, population=low_diversity_pop) is True

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Low diversity" in captured.out

    def test_verbose_max_fitness_evals_output(self, capsys):
        """Test verbose output for max fitness evaluations termination."""
        criteria = TerminationCriteria(max_iter=100, max_fitness_evals=5, verbose=True)

        # Increment evaluations to trigger termination
        for _ in range(6):
            criteria.increment_fitness_evals()

        # Should terminate due to max evaluations
        assert criteria.should_terminate(0, 0.5) is True

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Maximum fitness evaluations" in captured.out

    def test_verbose_time_limit_output(self, capsys):
        """Test verbose output for time limit termination."""
        criteria = TerminationCriteria(
            max_iter=100,
            time_limit_seconds=0.001,  # Very short time limit
            verbose=True,
        )

        criteria.start_timing()
        import time

        time.sleep(0.002)  # Sleep longer than limit

        # Should terminate due to time limit
        assert criteria.should_terminate(0, 0.5) is True

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Time limit" in captured.out


class TestTerminationIntegration:
    """Integration tests for termination in algorithm context."""

    def test_typical_algorithm_loop(self):
        """Test termination in a typical algorithm loop."""
        criteria = TerminationCriteria(max_iter=20, stagnation_iters=5, verbose=False)

        population = [
            CelestialBody(
                position=np.random.randint(0, 2, size=10),
                continuous_position=np.random.uniform(-2, 2, size=10),
                fitness=0.5 - i * 0.01,
            )
            for i in range(5)
        ]

        iteration = 0
        max_iter = 20

        for iteration in range(max_iter):
            # Simulate fitness improvement
            global_best_fitness = 0.5 - iteration * 0.01

            if criteria.should_terminate(
                iteration=iteration,
                global_best_fitness=global_best_fitness,
                population=population,
            ):
                break

        # Should complete without errors
        assert iteration >= 0
        stats = criteria.get_statistics()
        assert len(stats["best_fitness_history"]) > 0
