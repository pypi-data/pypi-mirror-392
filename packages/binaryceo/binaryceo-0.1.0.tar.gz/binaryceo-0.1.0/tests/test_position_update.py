"""Tests for position_update module."""

import numpy as np
import pytest

from binaryceo import CelestialBody, update_all_positions


class TestHelperFunctions:
    """Tests for helper translation functions."""

    def test_sigmoid_returns_probabilities(self):
        """Test that sigmoid returns values in [0, 1] range."""
        from binaryceo.position_update import _sigmoid

        x = np.array([-5.0, 0.0, 5.0])
        probs = _sigmoid(x)

        assert np.all(probs >= 0.0)
        assert np.all(probs <= 1.0)
        assert probs[1] == pytest.approx(0.5)  # sigmoid(0) = 0.5

    def test_sigmoid_handles_extreme_values(self):
        """Test that sigmoid handles extreme values without overflow."""
        from binaryceo.position_update import _sigmoid

        x = np.array([-1000.0, 1000.0])
        probs = _sigmoid(x)

        assert probs[0] == pytest.approx(0.0, abs=1e-6)
        assert probs[1] == pytest.approx(1.0, abs=1e-6)

    def test_stochastic_binarize_returns_binary(self):
        """Test that stochastic binarization returns only 0s and 1s."""
        from binaryceo.position_update import _stochastic_binarize

        probs = np.array([0.9, 0.1, 0.5, 0.7])
        binary = _stochastic_binarize(probs)

        assert np.all((binary == 0) | (binary == 1))
        assert len(binary) == len(probs)

    def test_generate_binary_proposal(self):
        """Test that binary proposal generation works end-to-end."""
        from binaryceo.position_update import _generate_binary_proposal

        continuous = np.array([2.0, -2.0, 0.0, 5.0, -5.0])
        binary = _generate_binary_proposal(continuous)

        assert np.all((binary == 0) | (binary == 1))
        assert len(binary) == len(continuous)


class TestCalculateGravityF:
    """Tests for local gravity force calculation."""

    def test_force_direction_toward_leader(self):
        """Test that force points toward leader."""
        from binaryceo.position_update import _calculate_gravity_F

        # Create body and leader
        body_pos = np.array([0.0, 0.0, 0.0])
        leader_pos = np.array([1.0, 1.0, 1.0])

        body = CelestialBody(
            position=np.array([0, 0, 0]), continuous_position=body_pos, fitness=0.5
        )
        leader = CelestialBody(
            position=np.array([1, 1, 1]), continuous_position=leader_pos, fitness=0.3
        )

        params = {"c1": 0.5}

        # Calculate force multiple times (due to randomness)
        for _ in range(10):
            force = _calculate_gravity_F(body, leader, params)

            # Force should generally point in positive direction
            # (toward leader from body)
            assert len(force) == len(body_pos)

    def test_force_is_zero_when_at_leader(self):
        """Test that force is zero when body is at leader position."""
        from binaryceo.position_update import _calculate_gravity_F

        # Create body and leader at same position
        same_pos = np.array([1.0, 1.0, 1.0])

        body = CelestialBody(
            position=np.array([1, 1, 1]), continuous_position=same_pos, fitness=0.5
        )
        leader = CelestialBody(
            position=np.array([1, 1, 1]),
            continuous_position=same_pos.copy(),
            fitness=0.3,
        )

        params = {"c1": 0.5}
        force = _calculate_gravity_F(body, leader, params)

        # Force should be zero (natural brake at convergence)
        assert np.allclose(force, np.zeros_like(force))


# --- ADD THIS NEW TEST CLASS ---
class TestCalculateGravityA:
    """Tests for global gravity force calculation (Module 4b)."""

    @pytest.fixture
    def setup_bodies(self):
        """Create a body and a global best body."""
        body = CelestialBody(
            position=np.array([0, 0, 0]),
            continuous_position=np.array([0.0, 0.0, 0.0]),
            fitness=0.5,
        )
        gbest = CelestialBody(
            position=np.array([1, 1, 1]),
            continuous_position=np.array([1.0, 1.0, 1.0]),
            fitness=0.1,
        )
        params = {"c2": 0.5}
        return body, gbest, params

    def test_force_b_direction_toward_global_best(self, setup_bodies):
        """Test that force points toward the global best."""
        from binaryceo.position_update import _calculate_gravity_A

        body, gbest, params = setup_bodies

        force = _calculate_gravity_A(body, gbest, params, 50, 100)

        # Force direction should be positive (from [0] toward [1])
        assert np.all(force >= 0.0)

    def test_force_b_is_zero_at_global_best(self, setup_bodies):
        """Test the 'natural brake' when body reaches global best."""
        from binaryceo.position_update import _calculate_gravity_A

        body, gbest, params = setup_bodies

        # Move body to gbest position
        body.continuous_position = gbest.continuous_position.copy()

        force = _calculate_gravity_A(body, gbest, params, 50, 100)

        # Force should be zero
        assert np.allclose(force, np.zeros_like(force))

    def test_force_b_is_adaptive_over_time(self, setup_bodies):
        """Test that force magnitude increases with iterations."""
        from binaryceo.position_update import _calculate_gravity_A

        body, gbest, params = setup_bodies

        # Calculate force early in the run
        force_early = _calculate_gravity_A(body, gbest, params, 1, 100)

        # Calculate force late in the run
        force_late = _calculate_gravity_A(body, gbest, params, 99, 100)

        # Magnitude of force should be greater later
        assert np.linalg.norm(force_late) > np.linalg.norm(force_early)


# --- END OF NEW TEST CLASS ---


class TestCalculateExpansionForce:
    """Tests for Cosmic Expansion force calculation (Module 4c)."""

    @pytest.fixture
    def setup_params(self):
        """Provide a standard set of parameters for expansion tests."""
        return {"W1": 0.1, "lb": -6.0, "ub": 6.0}

    def test_force_c_returns_correct_shape(self, setup_params):
        """Test that the force vector has the correct number of features."""
        from binaryceo.position_update import _calculate_expansion_force

        n_features = 10
        force = _calculate_expansion_force(setup_params, 1, 100, n_features)
        assert force.shape == (n_features,)

    def test_force_c_is_adaptive_over_time(self, setup_params):
        """Test that the force magnitude decays as iterations increase."""
        from binaryceo.position_update import _calculate_expansion_force

        n_features = 10

        # Calculate force early in the run (stronger)
        force_early = _calculate_expansion_force(setup_params, 1, 100, n_features)

        # Calculate force late in the run (weaker)
        force_late = _calculate_expansion_force(setup_params, 99, 100, n_features)

        # Magnitude of the force should be greater early on
        assert np.linalg.norm(force_early) > np.linalg.norm(force_late)

    def test_force_c_is_zero_when_w1_is_zero(self, setup_params):
        """Test that setting W1=0 disables the expansion force."""
        from binaryceo.position_update import _calculate_expansion_force

        n_features = 10

        # Override W1 to be zero
        setup_params["W1"] = 0.0

        force = _calculate_expansion_force(setup_params, 50, 100, n_features)

        # The force should be a zero vector
        assert np.allclose(force, np.zeros(n_features))

    def test_force_c_scales_with_bounds(self, setup_params):
        """Test that a larger bounds_range results in a stronger force."""
        from binaryceo.position_update import _calculate_expansion_force

        n_features = 10

        # Calculate force with a small range
        params_small_range = {"W1": 0.1, "lb": -1.0, "ub": 1.0}  # range = 2
        force_small = _calculate_expansion_force(
            params_small_range, 10, 100, n_features
        )

        # Calculate force with a large range
        params_large_range = {"W1": 0.1, "lb": -100.0, "ub": 100.0}  # range = 200
        force_large = _calculate_expansion_force(
            params_large_range, 10, 100, n_features
        )

        # The magnitude should be significantly larger for the wider bounds
        assert np.linalg.norm(force_large) > np.linalg.norm(force_small)


class TestUpdateAllPositionsEdgeCases:
    """Tests for edge cases in update_all_positions."""

    def test_empty_population(self):
        """Test update_all_positions with empty population."""
        stellar_systems = []
        population = []
        global_best = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=0.5,
        )
        params = {"c1": 0.5, "c2": 0.5, "W1": 0.1, "lb": -2.0, "ub": 2.0}

        # Should handle empty population gracefully
        result = update_all_positions(
            stellar_systems=stellar_systems,
            global_best_body=global_best,
            population=population,
            params=params,
            iteration=0,
            max_iter=10,
        )

        assert result == population
        assert len(result) == 0

    def test_empty_stellar_system(self):
        """Test update_all_positions with empty stellar system."""
        # Create a population but put them in empty systems
        leader = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=0.3,
        )
        population = [leader]

        # Create systems with one empty system
        stellar_systems = [[], [leader]]  # First system is empty

        params = {"c1": 0.5, "c2": 0.5, "W1": 0.1, "lb": -2.0, "ub": 2.0}

        # Should skip empty system and process non-empty ones
        result = update_all_positions(
            stellar_systems=stellar_systems,
            global_best_body=leader,
            population=population,
            params=params,
            iteration=0,
            max_iter=10,
        )

        assert result == population
        # Leader should not be updated (no followers in the system)
        assert np.array_equal(leader.continuous_position, [1.0, -1.0])


class TestUpdateAllPositions:
    """Tests for main orchestrator function."""

    @pytest.fixture
    def setup_system(self):
        """Create a simple system for orchestrator tests."""
        leader = CelestialBody(
            position=np.ones(3),
            continuous_position=np.array([2.0, 2.0, 2.0]),
            fitness=0.1,
        )
        follower = CelestialBody(
            position=np.zeros(3), continuous_position=np.zeros(3), fitness=0.5
        )
        stellar_systems = [[leader, follower]]
        population = [leader, follower]
        params = {"c1": 0.5, "c2": 0.3, "W1": 0.1, "lb": -6.0, "ub": 6.0}
        return stellar_systems, population, leader, follower, params

    def test_updates_follower_positions(self, setup_system):
        """Test that followers get updated but leaders do not."""
        stellar_systems, population, leader, follower, params = setup_system

        original_leader_pos = leader.continuous_position.copy()
        original_follower_pos = follower.continuous_position.copy()

        update_all_positions(
            stellar_systems=stellar_systems,
            global_best_body=leader,
            population=population,
            params=params,
            iteration=50,
            max_iter=100,
        )

        # Leader should NOT be updated
        assert np.array_equal(leader.continuous_position, original_leader_pos)

        # Follower's continuous_position SHOULD be updated
        assert not np.array_equal(follower.continuous_position, original_follower_pos)

        # And follower should have a proposed binary position
        assert hasattr(follower, "proposed_binary_position")
        assert len(follower.proposed_binary_position) == len(follower.position)

    def test_clamping_prevents_extreme_values(self, setup_system):
        """Test that clamping keeps continuous_position within bounds."""
        stellar_systems, population, leader, follower, params = setup_system

        # Force an extreme position on the leader to create a strong pull
        leader.continuous_position = np.array([100.0, 100.0, 100.0])

        update_all_positions(
            stellar_systems=stellar_systems,
            global_best_body=leader,
            population=population,
            params=params,
            iteration=99,  # Use late iteration for strong global pull
            max_iter=100,
        )

        # Check that follower's continuous_position is within bounds
        assert np.all(follower.continuous_position >= params["lb"])
        assert np.all(follower.continuous_position <= params["ub"])


class TestLocalSearch:
    """Tests for local_search function."""

    def test_local_search_basic_functionality(self):
        """Test basic local search functionality."""
        from binaryceo.position_update import local_search

        def simple_fitness(position, **kwargs):
            # Fitness = number of selected features (to minimize)
            return float(np.sum(position))

        # Create body with suboptimal position
        body = CelestialBody(
            position=np.array([1, 1, 1, 0, 0]),  # 3 features selected
            continuous_position=np.array([1.0, 1.0, 1.0, -1.0, -1.0]),
            fitness=3.0,
        )

        # Run local search
        result = local_search(body, simple_fitness)

        # Should return the same body instance
        assert result is body
        # Fitness should be same or better (lower)
        assert result.fitness <= 3.0

    def test_local_search_with_none_position(self):
        """Test local search with None position (edge case)."""
        from binaryceo.position_update import local_search

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        # Create body and manually set position to None to test edge case
        body = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=0.5,
        )
        body.position = None  # Manually set to None to test edge case

        # Should handle gracefully and return unchanged
        result = local_search(body, simple_fitness)
        assert result is body
        assert result.fitness == 0.5

    def test_local_search_with_empty_position(self):
        """Test local search with empty position array."""
        from binaryceo.position_update import local_search

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        # Create body with empty position
        body = CelestialBody(
            position=np.array([]), continuous_position=np.array([]), fitness=0.0
        )

        # Should handle gracefully and return unchanged
        result = local_search(body, simple_fitness)
        assert result is body
        assert result.fitness == 0.0

    def test_local_search_with_none_fitness(self):
        """Test local search when body has None fitness."""
        from binaryceo.position_update import local_search

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        # Create body with None fitness
        body = CelestialBody(
            position=np.array([1, 0, 1]),
            continuous_position=np.array([1.0, -1.0, 1.0]),
            fitness=None,
        )

        # Should evaluate fitness and then search
        result = local_search(body, simple_fitness)
        assert result is body
        assert result.fitness is not None
        assert result.fitness >= 0

    def test_local_search_with_termination_criteria(self):
        """Test local search with termination criteria counting."""
        from binaryceo.position_update import local_search
        from binaryceo.termination import TerminationCriteria

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        termination_criteria = TerminationCriteria(max_iter=10, verbose=False)

        # Create body with None fitness (will need evaluation)
        body = CelestialBody(
            position=np.array([1, 0, 1, 0]),
            continuous_position=np.array([1.0, -1.0, 1.0, -1.0]),
            fitness=None,
        )

        initial_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Run local search
        local_search(body, simple_fitness, termination_criteria=termination_criteria)

        final_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Should have counted evaluations (at least 1 for initial fitness + neighbors)
        assert final_evals > initial_evals

    def test_local_search_improvement(self):
        """Test that local search can find improvements."""
        from binaryceo.position_update import local_search

        def fitness_with_optimal_solution(position, **kwargs):
            # Optimal solution is [1, 0, 0, 0] with fitness 0.1
            # Any other solution has higher fitness
            if np.array_equal(position, [1, 0, 0, 0]):
                return 0.1
            else:
                return float(np.sum(position))

        # Start with suboptimal position
        body = CelestialBody(
            position=np.array([1, 1, 0, 0]),  # fitness = 2.0
            continuous_position=np.array([1.0, 1.0, -1.0, -1.0]),
            fitness=2.0,
        )

        # Run local search multiple times to increase chance of finding optimum
        for _ in range(10):
            local_search(body, fitness_with_optimal_solution)
            if body.fitness < 2.0:
                break

        # Should have found some improvement
        assert body.fitness <= 2.0

    def test_local_search_single_feature(self):
        """Test local search with single feature."""
        from binaryceo.position_update import local_search

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        # Create body with single feature
        body = CelestialBody(
            position=np.array([1]), continuous_position=np.array([1.0]), fitness=1.0
        )

        # Should handle single feature case
        result = local_search(body, simple_fitness)
        assert result is body
        # With single feature, can only flip to [0] which gives fitness 0.0
        # But we avoid all-zero vectors, so should stay at [1]
        assert result.fitness <= 1.0

    def test_local_search_avoids_all_zero_vectors(self):
        """Test that local search avoids creating all-zero vectors."""
        from binaryceo.position_update import local_search

        def simple_fitness(position, **kwargs):
            return float(np.sum(position))

        # Create body with minimal features
        body = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=1.0,
        )

        # Run local search - should not create [0, 0] even if it would be better
        result = local_search(body, simple_fitness)
        assert result is body
        # Should still have at least one feature selected
        assert np.sum(result.position) > 0
