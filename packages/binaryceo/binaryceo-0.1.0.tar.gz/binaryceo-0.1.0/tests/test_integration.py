"""
Integration tests for Binary CEO algorithm.

Tests how different modules work together in realistic scenarios.
"""

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.neighbors import KNeighborsClassifier

from binaryceo.fitness import multi_objective_fitness
from binaryceo.initialization import initialize_population
from binaryceo.partitioning import partition_stellar_systems
from binaryceo.position_update import local_search, update_all_positions
from binaryceo.selection import selection_step
from binaryceo.solution import CelestialBody
from binaryceo.termination import TerminationCriteria


class TestSingleIterationWorkflow:
    """Test a complete single iteration of the algorithm."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        X, y = make_classification(
            n_samples=50,
            n_features=10,
            n_informative=5,
            n_redundant=2,
            n_clusters_per_class=1,
            random_state=42,
        )
        model = KNeighborsClassifier(n_neighbors=3)
        return X, y, model

    def test_complete_iteration_workflow(self, sample_data):
        """Test one complete iteration: init -> partition -> update -> select."""
        X, y, model = sample_data
        n_features = X.shape[1]
        pop_size = 8

        # Step 1: Initialize population
        population, global_best_position, global_best_fitness = initialize_population(
            pop_size=pop_size,
            n_features=n_features,
            objective_function=multi_objective_fitness,
            selection_probability=0.3,
            continuous_init="from_position",
            min_features=1,
            verbose=False,
            X=X,
            y=y,
            model=model,
            accuracy_weight=0.7,
            cv_folds=3,
        )

        # Verify initialization results
        assert len(population) == pop_size
        assert global_best_position is not None
        assert len(global_best_position) == n_features
        assert global_best_fitness < float("inf")

        # All bodies should have valid fitness
        for body in population:
            assert body.fitness is not None
            assert body.fitness >= 0
            assert body.position is not None
            assert body.continuous_position is not None
            assert len(body.position) == n_features
            assert len(body.continuous_position) == n_features

        # Find initial global best
        initial_global_best = min(population, key=lambda b: b.fitness)

        # Step 2: Partition into stellar systems
        n_systems = 3
        stellar_systems = partition_stellar_systems(
            population=population, n_systems=n_systems, method="fitness_based"
        )

        # Verify partitioning results
        assert len(stellar_systems) <= n_systems  # May be fewer if pop_size is small
        total_bodies = sum(len(system) for system in stellar_systems)
        assert total_bodies == pop_size

        # Each system should have at least one body (the leader)
        for system in stellar_systems:
            assert len(system) >= 1

        # Step 3: Position update
        params = {"c1": 0.5, "c2": 0.5, "a": 1.0, "W1": 0.1, "lb": -2.0, "ub": 2.0}

        update_all_positions(
            stellar_systems=stellar_systems,
            global_best_body=initial_global_best,
            population=population,
            params=params,
            iteration=0,
            max_iter=10,
        )

        # Verify position updates
        followers_with_proposals = 0
        for system in stellar_systems:
            for body in system[1:]:  # Skip leaders
                # Followers should have proposed positions
                if (
                    hasattr(body, "proposed_binary_position")
                    and body.proposed_binary_position is not None
                ):
                    followers_with_proposals += 1
                    assert len(body.proposed_binary_position) == n_features
                    assert np.all(
                        (body.proposed_binary_position == 0)
                        | (body.proposed_binary_position == 1)
                    )

        # At least some followers should have proposals
        assert followers_with_proposals > 0

        # Step 4: Selection step
        updated_global_best = selection_step(
            population=population,
            objective_function=multi_objective_fitness,
            global_best_body=initial_global_best,
            X=X,
            y=y,
            model=model,
            accuracy_weight=0.7,
            cv_folds=3,
        )

        # Verify selection results
        assert updated_global_best is not None
        assert (
            updated_global_best.fitness <= initial_global_best.fitness
        )  # Should not get worse

        # All proposed positions should be cleared
        for body in population:
            proposed = getattr(body, "proposed_binary_position", None)
            assert proposed is None

    def test_local_search_integration(self, sample_data):
        """Test local search integration with other components."""
        X, y, model = sample_data
        n_features = X.shape[1]

        # Create a single body for local search
        position = np.random.choice([0, 1], size=n_features, p=[0.7, 0.3])
        if position.sum() == 0:  # Ensure at least one feature
            position[0] = 1

        continuous_position = np.where(
            position == 1,
            2.0 + np.random.normal(0, 0.3, size=n_features),
            -2.0 + np.random.normal(0, 0.3, size=n_features),
        )

        fitness = multi_objective_fitness(
            position, X=X, y=y, model=model, accuracy_weight=0.7, cv_folds=3
        )

        body = CelestialBody(position, continuous_position, fitness)
        original_fitness = body.fitness

        # Apply local search
        improved_body = local_search(
            body=body,
            objective_function=multi_objective_fitness,
            X=X,
            y=y,
            model=model,
            accuracy_weight=0.7,
            cv_folds=3,
        )

        # Verify local search results
        assert improved_body is body  # Should return same instance
        assert improved_body.fitness <= original_fitness  # Should not get worse
        assert improved_body.position is not None
        assert len(improved_body.position) == n_features
        assert improved_body.position.sum() > 0  # Should have at least one feature


class TestTerminationIntegration:
    """Test integration of termination criteria with algorithm components."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        X, y = make_classification(
            n_samples=30, n_features=8, n_informative=4, random_state=42
        )
        model = KNeighborsClassifier(n_neighbors=3)
        return X, y, model

    def test_termination_with_initialization(self, sample_data):
        """Test termination criteria counts initialization evaluations."""
        X, y, model = sample_data
        n_features = X.shape[1]
        pop_size = 6

        # Create termination criteria
        termination_criteria = TerminationCriteria(
            max_iter=10, max_fitness_evals=100, verbose=False
        )
        termination_criteria.start_timing()

        # Initialize population with termination criteria
        population, _, _ = initialize_population(
            pop_size=pop_size,
            n_features=n_features,
            objective_function=multi_objective_fitness,
            selection_probability=0.3,
            verbose=False,
            termination_criteria=termination_criteria,
            X=X,
            y=y,
            model=model,
            accuracy_weight=0.7,
            cv_folds=3,
        )

        # Should have counted exactly pop_size evaluations
        stats = termination_criteria.get_statistics()
        assert stats["fitness_evals"] == pop_size

    def test_termination_with_selection(self, sample_data):
        """Test that termination criteria correctly counts selection evaluations."""
        X, y, model = sample_data
        n_features = X.shape[1]

        # Create termination criteria
        termination_criteria = TerminationCriteria(
            max_iter=10, max_fitness_evals=100, verbose=False
        )
        termination_criteria.start_timing()

        # Create population with proposed positions
        population = []
        for i in range(4):
            position = np.random.choice([0, 1], size=n_features, p=[0.6, 0.4])
            if position.sum() == 0:
                position[0] = 1

            continuous_position = np.random.uniform(-2, 2, size=n_features)
            fitness = multi_objective_fitness(
                position, X=X, y=y, model=model, accuracy_weight=0.7, cv_folds=3
            )

            body = CelestialBody(position, continuous_position, fitness)

            # Add proposed position
            proposed = position.copy()
            flip_idx = np.random.randint(0, n_features)
            proposed[flip_idx] = 1 - proposed[flip_idx]
            if proposed.sum() > 0:  # Only if valid
                body.proposed_binary_position = proposed

            population.append(body)

        initial_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Run selection step
        global_best = min(population, key=lambda b: b.fitness)
        selection_step(
            population=population,
            objective_function=multi_objective_fitness,
            global_best_body=global_best,
            termination_criteria=termination_criteria,
            X=X,
            y=y,
            model=model,
            accuracy_weight=0.7,
            cv_folds=3,
        )

        # Should have counted additional evaluations for proposed positions
        final_evals = termination_criteria.get_statistics()["fitness_evals"]
        assert final_evals > initial_evals

    def test_termination_with_local_search(self, sample_data):
        """Test that termination criteria correctly counts local search evaluations."""
        X, y, model = sample_data
        n_features = X.shape[1]

        # Create termination criteria
        termination_criteria = TerminationCriteria(
            max_iter=10, max_fitness_evals=100, verbose=False
        )
        termination_criteria.start_timing()

        # Create a body for local search
        position = np.random.choice([0, 1], size=n_features, p=[0.6, 0.4])
        if position.sum() == 0:
            position[0] = 1

        continuous_position = np.random.uniform(-2, 2, size=n_features)
        fitness = multi_objective_fitness(
            position, X=X, y=y, model=model, accuracy_weight=0.7, cv_folds=3
        )

        body = CelestialBody(position, continuous_position, fitness)

        initial_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Run local search
        local_search(
            body=body,
            objective_function=multi_objective_fitness,
            termination_criteria=termination_criteria,
            X=X,
            y=y,
            model=model,
            accuracy_weight=0.7,
            cv_folds=3,
        )

        # Should have counted additional evaluations for neighbors
        final_evals = termination_criteria.get_statistics()["fitness_evals"]
        assert final_evals > initial_evals


class TestDataFlowIntegration:
    """Test data flow between different algorithm components."""

    def test_position_consistency_across_modules(self):
        """Test that position data remains consistent across module calls."""
        # Create test data
        X, y = make_classification(n_samples=40, n_features=6, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        # Initialize small population
        population, _, _ = initialize_population(
            pop_size=4,
            n_features=6,
            objective_function=multi_objective_fitness,
            selection_probability=0.4,
            verbose=False,
            X=X,
            y=y,
            model=model,
            accuracy_weight=0.7,
            cv_folds=3,
        )

        # Store original positions
        original_positions = [body.position.copy() for body in population]

        # Partition systems
        systems = partition_stellar_systems(population, n_systems=2, method="random")

        # Verify positions unchanged by partitioning
        for i, body in enumerate(population):
            assert np.array_equal(body.position, original_positions[i])

        # Update positions
        params = {"c1": 0.5, "c2": 0.5, "a": 1.0, "W1": 0.1, "lb": -2.0, "ub": 2.0}
        global_best = min(population, key=lambda b: b.fitness)

        update_all_positions(
            stellar_systems=systems,
            global_best_body=global_best,
            population=population,
            params=params,
            iteration=0,
            max_iter=5,
        )

        # Original positions should still be unchanged (only proposed positions added)
        for i, body in enumerate(population):
            assert np.array_equal(body.position, original_positions[i])

        # But some bodies should have proposed positions
        has_proposals = any(
            hasattr(body, "proposed_binary_position")
            and body.proposed_binary_position is not None
            for body in population
        )
        assert has_proposals

    def test_fitness_consistency(self):
        """Test that fitness values remain consistent across operations."""
        # Create test data
        X, y = make_classification(n_samples=30, n_features=5, random_state=42)
        model = KNeighborsClassifier(n_neighbors=3)

        # Create a body with known position
        position = np.array([1, 0, 1, 0, 1])
        continuous_position = np.array([2.0, -2.0, 1.5, -1.5, 2.2])

        # Calculate fitness directly
        expected_fitness = multi_objective_fitness(
            position, X=X, y=y, model=model, accuracy_weight=0.7, cv_folds=3
        )

        body = CelestialBody(position, continuous_position, expected_fitness)

        # Fitness should remain the same after various operations
        assert body.fitness == expected_fitness

        # Copy should have same fitness
        body_copy = body.copy()
        assert body_copy.fitness == expected_fitness

        # Adding to list shouldn't change fitness
        population = [body]
        assert population[0].fitness == expected_fitness

        # Partitioning shouldn't change fitness
        systems = partition_stellar_systems(population, n_systems=1, method="random")
        assert systems[0][0].fitness == expected_fitness


if __name__ == "__main__":
    pytest.main([__file__])
