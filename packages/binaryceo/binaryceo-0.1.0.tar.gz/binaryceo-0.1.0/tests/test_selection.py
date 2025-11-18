"""
Unit tests for the selection module.

Tests the selection step (Module 5) that handles accept/reject decisions
for proposed binary positions.
"""

import numpy as np
import pytest

from binaryceo.selection import selection_step
from binaryceo.solution import CelestialBody
from binaryceo.termination import TerminationCriteria


def simple_fitness_function(position, **kwargs):
    """Simple fitness function for testing - just sum of selected features."""
    return float(np.sum(position))


def mock_fitness_function(position, **kwargs):
    """Mock fitness function that returns different values based on position."""
    # Return fitness based on number of 1s, with some variation
    base_fitness = np.sum(position) * 0.1
    # Add some variation based on position pattern
    if len(position) > 0:
        base_fitness += position[0] * 0.05  # First feature adds extra cost
    return base_fitness


class TestSelectionStepBasicFunctionality:
    """Test basic functionality of selection_step."""

    def test_empty_population_returns_none(self):
        """Test that empty population returns None."""
        result = selection_step(
            population=[],
            objective_function=simple_fitness_function,
            global_best_body=None,
        )
        assert result is None

    def test_single_body_without_proposal(self):
        """Test single body without proposed position."""
        body = CelestialBody(
            position=np.array([1, 0, 1]),
            continuous_position=np.array([1.0, -1.0, 1.0]),
            fitness=0.5,
        )
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        assert result is body
        assert result.fitness == 0.5
        assert np.array_equal(result.position, [1, 0, 1])

    def test_single_body_with_better_proposal(self):
        """Test single body with a better proposed position."""
        body = CelestialBody(
            position=np.array([1, 1, 1]),  # fitness = 3.0
            continuous_position=np.array([1.0, 1.0, 1.0]),
            fitness=3.0,
        )
        # Propose a better solution (fewer features)
        body.proposed_binary_position = np.array([1, 0, 0])  # fitness = 1.0
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        assert result is body
        assert result.fitness == 1.0  # Should accept better proposal
        assert np.array_equal(result.position, [1, 0, 0])
        assert result.proposed_binary_position is None  # Should be cleared

    def test_single_body_with_worse_proposal(self):
        """Test single body with a worse proposed position."""
        body = CelestialBody(
            position=np.array([1, 0, 0]),  # fitness = 1.0
            continuous_position=np.array([1.0, -1.0, -1.0]),
            fitness=1.0,
        )
        # Propose a worse solution (more features)
        body.proposed_binary_position = np.array([1, 1, 1])  # fitness = 3.0
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        assert result is body
        assert result.fitness == 1.0  # Should reject worse proposal
        assert np.array_equal(result.position, [1, 0, 0])
        assert result.proposed_binary_position is None  # Should be cleared


class TestSelectionStepEdgeCases:
    """Test edge cases and error conditions."""

    def test_body_with_none_fitness_gets_evaluated(self):
        """Test that body with None fitness gets evaluated."""
        body = CelestialBody(
            position=np.array([1, 0, 1]),
            continuous_position=np.array([1.0, -1.0, 1.0]),
            fitness=None,  # No fitness initially
        )
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        assert result is body
        assert result.fitness == 2.0  # Should be evaluated: sum([1, 0, 1]) = 2

    def test_body_with_invalid_position_attribute(self):
        """Test handling of edge case with position validation."""
        # Create a valid body for comparison
        body = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=1.0,
        )
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        # Should work normally with valid body
        assert result is body
        assert result.fitness == 1.0

    def test_all_zero_proposal_is_rejected(self):
        """Test that all-zero proposals are rejected."""
        body = CelestialBody(
            position=np.array([1, 0, 1]),
            continuous_position=np.array([1.0, -1.0, 1.0]),
            fitness=2.0,
        )
        # Propose all-zero solution (invalid)
        body.proposed_binary_position = np.array([0, 0, 0])
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        assert result is body
        assert result.fitness == 2.0  # Should keep original
        assert np.array_equal(result.position, [1, 0, 1])
        assert result.proposed_binary_position is None  # Should be cleared

    def test_empty_proposal_is_rejected(self):
        """Test that empty proposals are rejected."""
        body = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=1.0,
        )
        # Propose empty solution (invalid)
        body.proposed_binary_position = np.array([])
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        assert result is body
        assert result.fitness == 1.0  # Should keep original
        assert np.array_equal(result.position, [1, 0])
        assert result.proposed_binary_position is None  # Should be cleared


class TestSelectionStepGlobalBestTracking:
    """Test global best tracking functionality."""

    def test_global_best_initialization_from_population(self):
        """Test that global best is initialized from population when None."""
        body1 = CelestialBody(
            position=np.array([1, 1, 1]),
            continuous_position=np.array([1.0, 1.0, 1.0]),
            fitness=3.0,
        )
        body2 = CelestialBody(
            position=np.array([1, 0, 0]),
            continuous_position=np.array([1.0, -1.0, -1.0]),
            fitness=1.0,  # Better fitness
        )
        population = [body1, body2]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,  # Start with None
        )

        # Should return body2 as it has better fitness
        assert result is body2
        assert result.fitness == 1.0

    def test_global_best_updated_by_accepted_proposal(self):
        """Test that global best is updated when a proposal creates new best."""
        # Create initial global best
        global_best = CelestialBody(
            position=np.array([1, 0, 0]),
            continuous_position=np.array([1.0, -1.0, -1.0]),
            fitness=1.0,
        )

        # Create body with proposal that will be even better
        body = CelestialBody(
            position=np.array([1, 1, 0]),  # fitness = 2.0
            continuous_position=np.array([1.0, 1.0, -1.0]),
            fitness=2.0,
        )
        body.proposed_binary_position = np.array(
            [0, 0, 1]
        )  # fitness = 1.0, but different pattern
        population = [body]

        result = selection_step(
            population=population,
            objective_function=mock_fitness_function,  # Uses more complex fitness
            global_best_body=global_best,
        )

        # The result should be the updated body (if it became better than global_best)
        assert result.fitness <= global_best.fitness

    def test_global_best_with_none_fitness_is_updated(self):
        """Test updating global best when it has None fitness."""
        global_best = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=0.5,  # Valid fitness
        )

        body = CelestialBody(
            position=np.array([0, 1]),
            continuous_position=np.array([-1.0, 1.0]),
            fitness=1.0,
        )
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=global_best,
        )

        # Should keep global_best since it has better fitness
        assert result.fitness == 0.5


class TestSelectionStepMultiplePopulation:
    """Test selection with multiple bodies in population."""

    def test_multiple_bodies_with_mixed_proposals(self):
        """Test population with some bodies having proposals, others not."""
        body1 = CelestialBody(
            position=np.array([1, 1]),
            continuous_position=np.array([1.0, 1.0]),
            fitness=2.0,
        )
        # No proposal for body1

        body2 = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=1.0,
        )
        body2.proposed_binary_position = np.array([0, 1])  # Same fitness but different

        body3 = CelestialBody(
            position=np.array([0, 0]),
            continuous_position=np.array([-1.0, -1.0]),
            fitness=0.0,
        )
        body3.proposed_binary_position = np.array([1, 1])  # Worse proposal

        population = [body1, body2, body3]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        # Should return body3 as it has best fitness (0.0)
        assert result is body3
        assert result.fitness == 0.0

        # Check that proposals were processed
        assert body1.proposed_binary_position is None  # Never had one
        assert body2.proposed_binary_position is None  # Should be cleared
        assert body3.proposed_binary_position is None  # Should be cleared

    def test_all_bodies_have_none_fitness_initially(self):
        """Test when all bodies start with None fitness."""
        body1 = CelestialBody(
            position=np.array([1, 1]),
            continuous_position=np.array([1.0, 1.0]),
            fitness=None,
        )
        body2 = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=None,
        )
        population = [body1, body2]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        # Both should be evaluated, better one should be global best
        assert body1.fitness == 2.0
        assert body2.fitness == 1.0
        assert result is body2  # Better fitness


class TestSelectionStepTerminationIntegration:
    """Test integration with termination criteria."""

    def test_fitness_evaluations_are_counted(self):
        """Test that fitness evaluations are properly counted."""
        termination_criteria = TerminationCriteria(max_iter=10, verbose=False)

        body1 = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=None,  # Will need evaluation
        )
        body2 = CelestialBody(
            position=np.array([0, 1]),
            continuous_position=np.array([-1.0, 1.0]),
            fitness=1.0,
        )
        body2.proposed_binary_position = np.array([1, 1])  # Will need evaluation

        population = [body1, body2]

        initial_evals = termination_criteria.get_statistics()["fitness_evals"]

        selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
            termination_criteria=termination_criteria,
        )

        final_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Should count: 1 for body1 initial + 1 for body2 proposal = 2 evaluations
        assert final_evals == initial_evals + 2

    def test_no_termination_criteria_works(self):
        """Test that function works without termination criteria."""
        body = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=None,
        )
        population = [body]

        # Should work without termination_criteria
        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
            termination_criteria=None,
        )

        assert result is body
        assert result.fitness == 1.0


class TestSelectionStepCoverageTargeted:
    """Tests specifically targeting uncovered lines."""

    def test_body_with_none_fitness_in_population_scan(self):
        """Test the specific case where body.fitness is None during population scan."""
        # Create a body with None fitness that will be skipped in the initial scan
        body1 = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=None,
        )
        # Manually set position to None to trigger the continue condition
        body1.position = None

        body2 = CelestialBody(
            position=np.array([0, 1]),
            continuous_position=np.array([-1.0, 1.0]),
            fitness=1.0,
        )
        population = [body1, body2]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        # Should select body2 since body1 is skipped
        assert result is body2
        assert result.fitness == 1.0

    def test_body_needs_fitness_evaluation_in_main_loop(self):
        """Test body that needs fitness evaluation in the main processing loop."""
        # Start with a valid global best
        global_best = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=1.0,
        )

        # Create body with None fitness that will be evaluated in main loop
        body = CelestialBody(
            position=np.array([0, 1]),
            continuous_position=np.array([-1.0, 1.0]),
            fitness=None,  # This will trigger evaluation in main loop
        )
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=global_best,
        )

        # Body should now have fitness evaluated
        assert body.fitness == 1.0
        # Result should be the better of global_best and body (both have fitness 1.0)
        assert result.fitness == 1.0

    def test_body_fitness_evaluation_with_termination_criteria(self):
        """Test fitness evaluation counting with termination criteria."""
        termination_criteria = TerminationCriteria(max_iter=10, verbose=False)

        global_best = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=1.0,
        )

        # Create body that needs fitness evaluation in main loop
        body = CelestialBody(
            position=np.array([0, 1]),
            continuous_position=np.array([-1.0, 1.0]),
            fitness=None,  # Will be evaluated in main loop
        )
        population = [body]

        initial_evals = termination_criteria.get_statistics()["fitness_evals"]

        _ = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=global_best,
            termination_criteria=termination_criteria,
        )

        final_evals = termination_criteria.get_statistics()["fitness_evals"]

        # Should have counted 1 evaluation for the body's fitness
        assert final_evals == initial_evals + 1
        assert body.fitness == 1.0


class TestSelectionStepComplexScenarios:
    """Test complex real-world scenarios."""

    def test_body_with_none_fitness_and_proposal(self):
        """Test body that has None fitness but also has a proposal."""
        body = CelestialBody(
            position=np.array([1, 1]),
            continuous_position=np.array([1.0, 1.0]),
            fitness=None,  # No initial fitness
        )
        body.proposed_binary_position = np.array([1, 0])  # Better proposal
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        # Should accept the proposal since it's better than current
        assert result is body
        assert result.fitness == 1.0  # Proposal fitness
        assert np.array_equal(result.position, [1, 0])
        assert result.proposed_binary_position is None

    def test_proposal_equal_to_current_fitness(self):
        """Test when proposed fitness equals current fitness."""
        body = CelestialBody(
            position=np.array([1, 0]),
            continuous_position=np.array([1.0, -1.0]),
            fitness=1.0,
        )
        body.proposed_binary_position = np.array([0, 1])  # Same fitness = 1.0
        population = [body]

        result = selection_step(
            population=population,
            objective_function=simple_fitness_function,
            global_best_body=None,
        )

        # Should keep original since proposal is not strictly better
        assert result is body
        assert result.fitness == 1.0
        assert np.array_equal(result.position, [1, 0])  # Original position
        assert result.proposed_binary_position is None


if __name__ == "__main__":
    pytest.main([__file__])
