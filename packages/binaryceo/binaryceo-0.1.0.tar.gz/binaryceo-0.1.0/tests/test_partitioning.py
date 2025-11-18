"""Tests for the stellar system partitioning module."""

import numpy as np
import pytest

# Import the components to be tested
from binaryceo.partitioning import partition_stellar_systems
from binaryceo.solution import CelestialBody


@pytest.fixture(scope="module")
def celestial_population():
    """
    Create a shared population of CelestialBody objects for testing.
    The fitness values are intentionally sorted for predictable behavior.
    """
    pop_size = 10
    n_features = 8
    population = []
    for i in range(pop_size):
        # Create predictable, unique positions
        position = np.zeros(n_features, dtype=int)
        if i < n_features:
            position[i] = 1  # e.g., [1,0,0..], [0,1,0..]

        # Create perfectly sorted fitness values for easy testing
        fitness = 0.1 * (i + 1)  # 0.1, 0.2, 0.3, ...

        # Velocity is not used in partitioning, can be zero
        velocity = np.zeros(n_features)

        population.append(CelestialBody(position, velocity, fitness))

    return population


class TestStellarSystemPartitioning:
    """Tests for the partition_stellar_systems function."""

    def test_partition_by_distance_to_leaders(self, celestial_population):
        """Tests partitioning logic based on leaders and Hamming distance."""

        n_systems = 3
        systems = partition_stellar_systems(
            celestial_population, n_systems, method="distance_based"
        )

        # 1. Check correct number of systems are created
        assert len(systems) == n_systems

        # 2. Check that no bodies were lost or duplicated
        total_bodies_in_systems = sum(len(s) for s in systems)
        assert total_bodies_in_systems == len(celestial_population)

        # 3. Check that the leaders (best fitness bodies) are in separate systems
        # The best 3 bodies should have fitness 0.1, 0.2, 0.3
        leader_fitnesses = {s[0].fitness for s in systems}

        actual_sorted_fitnesses = sorted(list(leader_fitnesses))
        expected_sorted_fitnesses = [0.1, 0.2, 0.3]

        # Use pytest.approx to handle floating-point inaccuracies
        assert actual_sorted_fitnesses == pytest.approx(expected_sorted_fitnesses)

    def test_partition_by_fitness(self, celestial_population):
        """
        Tests the fitness-based chunking partition method.
        """
        n_systems = 4
        systems = partition_stellar_systems(
            celestial_population, n_systems, method="fitness_based"
        )

        # 10 bodies into 4 systems should result in sizes: [2, 2, 2, 4]
        assert len(systems) == n_systems
        assert [len(s) for s in systems] == [2, 2, 2, 4]

        # Check that the first system contains the two best bodies
        assert systems[0][0].fitness == 0.1
        assert systems[0][1].fitness == 0.2

    def test_partition_randomly(self, celestial_population):
        """
        Tests the random partitioning method.
        """
        n_systems = 3
        systems = partition_stellar_systems(
            celestial_population, n_systems, method="random"
        )

        # 10 bodies into 3 systems should have sizes like [4, 3, 3]
        assert len(systems) == n_systems
        system_sizes = sorted([len(s) for s in systems])
        assert system_sizes == [3, 3, 4]

        # 2. Check that no bodies were lost
        total_bodies_in_systems = sum(len(s) for s in systems)
        assert total_bodies_in_systems == len(celestial_population)

    def test_edge_case_one_system(self, celestial_population):
        """
        Test that asking for one system returns the whole population in a single list.
        """
        systems = partition_stellar_systems(
            celestial_population, n_systems=1, method="distance_based"
        )
        assert len(systems) == 1
        assert len(systems[0]) == len(celestial_population)

    def test_edge_case_more_systems_than_bodies(self, celestial_population):
        """
        Test that if n_systems > pop_size, each body gets its own system.
        """
        small_pop = celestial_population[:3]
        systems = partition_stellar_systems(
            small_pop, n_systems=5, method="distance_based"
        )
        assert len(systems) == len(small_pop)  # Should be 3 systems
        assert all(len(s) == 1 for s in systems)

    def test_invalid_method(self, celestial_population):
        """
        Test that an unknown method raises a ValueError.
        """
        with pytest.raises(ValueError, match="Unknown partitioning method"):
            partition_stellar_systems(celestial_population, 3, method="invalid_method")

    def test_zero_systems_raises_error(self, celestial_population):
        """
        Test that n_systems=0 raises a ValueError.
        """
        with pytest.raises(ValueError):
            partition_stellar_systems(celestial_population, 0, method="distance_based")
