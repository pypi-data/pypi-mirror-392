"""Tests for initialization module."""

import numpy as np
import pytest

from binaryceo import (
    CelestialBody,
    create_sparse_binary_vector,
    initialize_from_custom_positions,
    initialize_population,
)


class TestCelestialBody:
    """Tests for CelestialBody class."""

    def test_initialization_with_defaults(self):
        """Test CelestialBody initialization with required parameters."""
        position = np.array([1, 0, 1, 0])
        continuous_position = np.array([1.0, -1.0, 1.0, -1.0])
        fitness = 0.5
        body = CelestialBody(
            position=position, continuous_position=continuous_position, fitness=fitness
        )

        assert np.array_equal(body.position, position)
        assert np.array_equal(body.continuous_position, continuous_position)
        assert body.fitness == fitness

    def test_initialization_with_all_params(self):
        """Test CelestialBody initialization with all parameters."""
        position = np.array([1, 0, 1, 0])
        continuous_position = np.array([0.5, -0.3, 0.1, -0.8])
        fitness = 0.25

        body = CelestialBody(
            position=position, continuous_position=continuous_position, fitness=fitness
        )

        assert np.array_equal(body.position, position)
        assert np.array_equal(body.continuous_position, continuous_position)
        assert body.fitness == fitness

    def test_copy_creates_deep_copy(self):
        """Test that copy() creates a deep copy."""
        position = np.array([1, 0, 1, 0])
        continuous_position = np.array([0.5, -0.3, 0.1, -0.8])
        fitness = 0.25

        body1 = CelestialBody(
            position=position, continuous_position=continuous_position, fitness=fitness
        )
        body2 = body1.copy()

        # Modify the copy
        body2.position[0] = 0
        body2.continuous_position[0] = 1.0
        body2.fitness = 0.5

        # Original should be unchanged
        assert body1.position[0] == 1
        assert body1.continuous_position[0] == 0.5
        assert body1.fitness == 0.25


class TestCreateSparseBinaryVector:
    """Tests for create_sparse_binary_vector function."""

    def test_vector_is_binary(self):
        """Test that output is binary (only 0s and 1s)."""
        vector = create_sparse_binary_vector(n_features=100)
        assert np.all((vector == 0) | (vector == 1))

    def test_vector_length(self):
        """Test that output has correct length."""
        n_features = 50
        vector = create_sparse_binary_vector(n_features=n_features)
        assert len(vector) == n_features

    def test_min_features_satisfied(self):
        """Test that minimum features constraint is satisfied."""
        min_features = 5
        vector = create_sparse_binary_vector(
            n_features=100,
            selection_probability=0.0,  # Force zeros
            min_features=min_features,
        )
        assert np.sum(vector) >= min_features

    def test_no_zero_vector(self):
        """Test that zero vectors are prevented."""
        # Try many times to ensure it never produces zero vector
        for _ in range(50):
            vector = create_sparse_binary_vector(
                n_features=10, selection_probability=0.01  # Very low probability
            )
            assert np.sum(vector) > 0


class TestInitializePopulation:
    """Tests for initialize_population function."""

    @staticmethod
    def dummy_fitness(position, **kwargs):
        """Dummy fitness function for testing."""
        return np.sum(position) / len(position)

    def test_population_size(self):
        """Test that correct number of bodies are created."""
        pop_size = 10
        n_features = 20

        population, _, _ = initialize_population(
            pop_size=pop_size,
            n_features=n_features,
            objective_function=self.dummy_fitness,
            verbose=False,
        )

        assert len(population) == pop_size

    def test_all_bodies_have_fitness(self):
        """Test that all bodies have fitness calculated."""
        population, _, _ = initialize_population(
            pop_size=5,
            n_features=10,
            objective_function=self.dummy_fitness,
            verbose=False,
        )

        for body in population:
            assert body.fitness is not None
            assert isinstance(body.fitness, float)

    def test_global_best_is_actually_best(self):
        """Test that global best has the best fitness."""
        population, best_pos, best_fit = initialize_population(
            pop_size=10,
            n_features=20,
            objective_function=self.dummy_fitness,
            verbose=False,
        )

        # Check that global best fitness matches the best in population
        min_fitness = min(body.fitness for body in population)
        assert best_fit == min_fitness

    def test_continuous_initialization_zero(self):
        """Test zero continuous_position initialization."""
        population, _, _ = initialize_population(
            pop_size=5,
            n_features=10,
            objective_function=self.dummy_fitness,
            continuous_init="zero",
            verbose=False,
        )

        for body in population:
            assert np.allclose(body.continuous_position, np.zeros(10))

    def test_continuous_initialization_random(self):
        """Test random continuous_position initialization."""
        population, _, _ = initialize_population(
            pop_size=5,
            n_features=10,
            objective_function=self.dummy_fitness,
            continuous_init="random",
            continuous_range=(-1.0, 1.0),
            verbose=False,
        )

        for body in population:
            # Check continuous_position values are in range
            assert np.all(body.continuous_position >= -1.0)
            assert np.all(body.continuous_position <= 1.0)

    def test_invalid_continuous_init_raises_error(self):
        """Test that invalid continuous_init raises ValueError."""
        with pytest.raises(ValueError, match="Invalid continuous_init"):
            initialize_population(
                pop_size=5,
                n_features=10,
                objective_function=self.dummy_fitness,
                continuous_init="invalid",
                verbose=False,
            )

    def test_fitness_function_receives_kwargs(self):
        """Test that kwargs are passed to fitness function."""

        def fitness_with_kwargs(position, multiplier=1.0):
            return np.sum(position) * multiplier

        population, _, best_fit = initialize_population(
            pop_size=5,
            n_features=10,
            objective_function=fitness_with_kwargs,
            verbose=False,
            multiplier=2.0,
        )

        # Fitness should be doubled due to multiplier
        assert best_fit > 0


class TestInitializeFromCustomPositions:
    """Tests for initialize_from_custom_positions function."""

    @staticmethod
    def dummy_fitness(position, **kwargs):
        """Dummy fitness function for testing."""
        return np.sum(position) / len(position)

    def test_custom_initialization(self):
        """Test initialization from custom positions."""
        custom_positions = [
            np.array([1, 0, 1, 0]),
            np.array([0, 1, 1, 0]),
            np.array([1, 1, 0, 0]),
        ]

        population, best_pos, best_fit = initialize_from_custom_positions(
            positions=custom_positions,
            objective_function=self.dummy_fitness,
            verbose=False,
        )

        assert len(population) == 3
        assert best_fit is not None

    def test_invalid_position_raises_error(self):
        """Test that invalid positions raise errors."""
        # Test with non-binary values
        invalid_positions = [np.array([1, 0, 2, 0])]  # Contains 2, not binary

        with pytest.raises(ValueError, match="not binary"):
            initialize_from_custom_positions(
                positions=invalid_positions,
                objective_function=self.dummy_fitness,
                continuous_init="random",
            )

    def test_zero_vector_raises_error(self):
        """Test that zero vectors raise errors."""
        zero_positions = [np.array([0, 0, 0])]  # All zeros

        with pytest.raises(ValueError, match="no features selected"):
            initialize_from_custom_positions(
                positions=zero_positions,
                objective_function=self.dummy_fitness,
                continuous_init="random",
            )


class TestInitializationVerboseOutput:
    """Tests for verbose output in initialization functions."""

    def test_initialize_population_verbose_output(self, capsys):
        """Test verbose output during population initialization."""

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        population, _, _ = initialize_population(
            pop_size=5,
            n_features=4,
            objective_function=simple_fitness,
            verbose=True,  # Enable verbose output
        )

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Initializing 5 solutions with 4 features" in captured.out
        assert "This may take time" in captured.out
        assert "Initialization complete!" in captured.out
        assert "Best fitness:" in captured.out
        assert "Best solution:" in captured.out

    def test_initialize_population_progress_output(self, capsys):
        """Test progress output during initialization."""

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        # Use larger population to trigger progress messages
        population, _, _ = initialize_population(
            pop_size=12,  # Should trigger progress at 10% intervals
            n_features=3,
            objective_function=simple_fitness,
            verbose=True,
        )

        # Check that progress output was printed
        captured = capsys.readouterr()
        assert "Initialized" in captured.out
        assert "Best so far:" in captured.out


class TestInitializationTerminationIntegration:
    """Tests for termination criteria integration in initialization."""

    def test_initialize_population_with_termination_criteria(self):
        """Test that initialization counts fitness evaluations."""
        from binaryceo.termination import TerminationCriteria

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        termination_criteria = TerminationCriteria(max_iter=10, verbose=False)
        initial_evals = termination_criteria.get_statistics()["fitness_evals"]

        population, _, _ = initialize_population(
            pop_size=5,
            n_features=4,
            objective_function=simple_fitness,
            termination_criteria=termination_criteria,
            verbose=False,
        )

        final_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Should have counted 5 evaluations (one per individual)
        assert final_evals == initial_evals + 5

    def test_initialize_from_custom_positions_with_termination_criteria(self):
        """Test custom initialization with termination criteria."""
        from binaryceo.termination import TerminationCriteria

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        termination_criteria = TerminationCriteria(max_iter=10, verbose=False)
        initial_evals = termination_criteria.get_statistics()["fitness_evals"]

        custom_positions = [np.array([1, 0, 1]), np.array([0, 1, 1])]

        population, _, _ = initialize_from_custom_positions(
            positions=custom_positions,
            objective_function=simple_fitness,
            continuous_init="random",
            termination_criteria=termination_criteria,
            verbose=False,
        )

        final_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Should have counted 2 evaluations (one per custom position)
        assert final_evals == initial_evals + 2


class TestInitializationEdgeCases:
    """Tests for edge cases and different initialization strategies."""

    def test_custom_initialization_zero_continuous_init(self):
        """Test custom initialization with zero continuous initialization."""

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        custom_positions = [np.array([1, 0, 1]), np.array([0, 1, 1])]

        population, _, _ = initialize_from_custom_positions(
            positions=custom_positions,
            objective_function=simple_fitness,
            continuous_init="zero",  # This should trigger line 221
            verbose=False,
        )

        # All continuous positions should be zero
        for body in population:
            assert np.allclose(body.continuous_position, 0.0)

    def test_custom_initialization_random_continuous_init(self):
        """Test custom initialization with random continuous initialization."""

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        custom_positions = [np.array([1, 0, 1]), np.array([0, 1, 1])]

        population, _, _ = initialize_from_custom_positions(
            positions=custom_positions,
            objective_function=simple_fitness,
            continuous_init="random",  # This should trigger line 223
            continuous_range=(-2.0, 2.0),
            verbose=False,
        )

        # All continuous positions should be in range
        for body in population:
            assert np.all(body.continuous_position >= -2.0)
            assert np.all(body.continuous_position <= 2.0)

    def test_custom_initialization_invalid_continuous_init(self):
        """Test custom initialization with invalid continuous init."""

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        custom_positions = [np.array([1, 0, 1])]

        # This should trigger line 236 (invalid continuous_init error)
        with pytest.raises(ValueError, match="Invalid continuous_init"):
            initialize_from_custom_positions(
                positions=custom_positions,
                objective_function=simple_fitness,
                continuous_init="invalid_strategy",
                verbose=False,
            )

    def test_custom_initialization_verbose_output(self, capsys):
        """Test verbose output in custom initialization."""

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        custom_positions = [np.array([1, 0, 1]), np.array([0, 1, 1])]

        population, _, _ = initialize_from_custom_positions(
            positions=custom_positions,
            objective_function=simple_fitness,
            continuous_init="from_position",
            verbose=True,  # This should trigger line 256
        )

        # Check that verbose output was printed
        captured = capsys.readouterr()
        assert "Initializing 2 solutions from custom positions" in captured.out
        assert "Custom initialization complete!" in captured.out
        assert "Best fitness:" in captured.out
