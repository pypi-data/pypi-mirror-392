"""
Unit tests for the solution module (CelestialBody class).

Tests the core data structure used throughout the Binary CEO algorithm.
"""

import numpy as np
import pytest

from binaryceo.solution import CelestialBody


class TestCelestialBodyCreation:
    """Test CelestialBody creation and basic properties."""

    def test_basic_creation(self):
        """Test basic CelestialBody creation with required parameters."""
        position = np.array([1, 0, 1, 0])
        continuous_position = np.array([2.1, -1.8, 1.9, -2.2])
        fitness = 0.25

        body = CelestialBody(
            position=position, continuous_position=continuous_position, fitness=fitness
        )

        assert np.array_equal(body.position, position)
        assert np.array_equal(body.continuous_position, continuous_position)
        assert body.fitness == fitness
        assert body.proposed_binary_position is None

    def test_arrays_are_copied(self):
        """Test that input arrays are copied, not referenced."""
        position = np.array([1, 0, 1])
        continuous_position = np.array([2.0, -1.0, 1.5])
        fitness = 0.3

        body = CelestialBody(position, continuous_position, fitness)

        # Modify original arrays
        position[0] = 0
        continuous_position[0] = -5.0

        # Body should be unchanged
        assert body.position[0] == 1
        assert body.continuous_position[0] == 2.0


class TestCelestialBodyCopy:
    """Test the copy functionality of CelestialBody."""

    def test_copy_creates_independent_instance(self):
        """Test that copy() creates a truly independent copy."""
        position = np.array([1, 0, 1, 0])
        continuous_position = np.array([2.1, -1.8, 1.9, -2.2])
        fitness = 0.25

        original = CelestialBody(position, continuous_position, fitness)
        original.proposed_binary_position = np.array([0, 1, 0, 1])

        # Create copy
        copy = original.copy()

        # Verify basic attributes are equal
        assert np.array_equal(copy.position, original.position)
        assert np.array_equal(copy.continuous_position, original.continuous_position)
        assert copy.fitness == original.fitness
        assert np.array_equal(
            copy.proposed_binary_position, original.proposed_binary_position
        )

        # Verify they are independent copies (not references)
        copy.position[0] = 0
        copy.continuous_position[0] = -5.0
        copy.fitness = 0.8
        copy.proposed_binary_position[0] = 1

        # Original should be unchanged
        assert original.position[0] == 1
        assert original.continuous_position[0] == 2.1
        assert original.fitness == 0.25
        assert original.proposed_binary_position[0] == 0

    def test_copy_with_none_proposed_position(self):
        """Test copying when proposed_binary_position is None."""
        position = np.array([1, 0])
        continuous_position = np.array([1.0, -1.0])
        fitness = 0.5

        original = CelestialBody(position, continuous_position, fitness)
        copy = original.copy()

        assert copy.proposed_binary_position is None

        # Modify copy
        copy.proposed_binary_position = np.array([0, 1])

        # Original should still be None
        assert original.proposed_binary_position is None


class TestCelestialBodyComparison:
    """Test comparison operators for CelestialBody."""

    def test_less_than_operator(self):
        """Test the __lt__ operator for fitness comparison."""
        position = np.array([1, 0])
        continuous_position = np.array([1.0, -1.0])

        body1 = CelestialBody(position, continuous_position, fitness=0.2)
        body2 = CelestialBody(position, continuous_position, fitness=0.3)
        body3 = CelestialBody(position, continuous_position, fitness=0.2)

        # Test less than
        assert body1 < body2  # 0.2 < 0.3
        assert not (body2 < body1)  # 0.3 not < 0.2
        assert not (body1 < body3)  # 0.2 not < 0.2 (equal)

    def test_less_than_with_none_fitness(self):
        """Test __lt__ behavior when fitness is None."""
        position = np.array([1, 0])
        continuous_position = np.array([1.0, -1.0])

        body1 = CelestialBody(position, continuous_position, fitness=None)
        body2 = CelestialBody(position, continuous_position, fitness=0.3)
        body3 = CelestialBody(position, continuous_position, fitness=None)

        # None fitness should return False
        assert not (body1 < body2)
        assert not (body2 < body1)
        assert not (body1 < body3)

    def test_equality_operator(self):
        """Test the __eq__ operator."""
        position1 = np.array([1, 0, 1])
        position2 = np.array([1, 0, 0])  # Different position
        continuous_position = np.array([1.0, -1.0, 0.5])

        body1 = CelestialBody(position1, continuous_position, fitness=0.2)
        body2 = CelestialBody(position1.copy(), continuous_position, fitness=0.2)
        body3 = CelestialBody(position2, continuous_position, fitness=0.2)
        body4 = CelestialBody(position1, continuous_position, fitness=0.3)

        # Same position and fitness should be equal
        assert body1 == body2

        # Different position should not be equal
        assert body1 != body3

        # Different fitness should not be equal
        assert body1 != body4

        # Non-CelestialBody should not be equal
        assert body1 != "not a body"
        assert body1 != 42

    def test_equality_with_none_fitness(self):
        """Test equality when fitness is None."""
        position = np.array([1, 0])
        continuous_position = np.array([1.0, -1.0])

        body1 = CelestialBody(position, continuous_position, fitness=None)
        body2 = CelestialBody(position.copy(), continuous_position, fitness=None)
        body3 = CelestialBody(position, continuous_position, fitness=0.2)

        assert body1 == body2  # Both None fitness
        assert body1 != body3  # One None, one not


class TestCelestialBodyHashing:
    """Test hashing functionality for CelestialBody."""

    def test_hash_function(self):
        """Test that CelestialBody can be hashed."""
        position = np.array([1, 0, 1])
        continuous_position = np.array([1.0, -1.0, 0.5])
        fitness = 0.25

        body = CelestialBody(position, continuous_position, fitness)

        # Should be able to compute hash
        hash_value = hash(body)
        assert isinstance(hash_value, int)

    def test_equal_bodies_have_same_hash(self):
        """Test that equal bodies have the same hash."""
        position = np.array([1, 0, 1])
        continuous_position = np.array([1.0, -1.0, 0.5])
        fitness = 0.25

        body1 = CelestialBody(position, continuous_position, fitness)
        body2 = CelestialBody(position.copy(), continuous_position, fitness)

        assert body1 == body2
        assert hash(body1) == hash(body2)

    def test_bodies_can_be_used_in_sets(self):
        """Test that CelestialBody can be used in sets and dictionaries."""
        position1 = np.array([1, 0])
        position2 = np.array([0, 1])
        continuous_position = np.array([1.0, -1.0])

        body1 = CelestialBody(position1, continuous_position, fitness=0.2)
        body2 = CelestialBody(position2, continuous_position, fitness=0.3)
        body3 = CelestialBody(
            position1.copy(), continuous_position, fitness=0.2
        )  # Same as body1

        # Test set operations
        body_set = {body1, body2, body3}
        assert len(body_set) == 2  # body1 and body3 are equal, so only 2 unique

        # Test dictionary operations
        body_dict = {body1: "first", body2: "second"}
        assert body_dict[body3] == "first"  # body3 should map to same as body1


class TestCelestialBodyStringRepresentation:
    """Test string representation of CelestialBody."""

    def test_repr_with_valid_fitness(self):
        """Test __repr__ with valid fitness value."""
        position = np.array([1, 0, 1, 0, 1])  # 3 features selected
        continuous_position = np.array([1.0, -1.0, 0.5, -0.5, 1.5])
        fitness = 0.123456

        body = CelestialBody(position, continuous_position, fitness)
        repr_str = repr(body)

        assert "CelestialBody" in repr_str
        assert "features=3/5" in repr_str
        assert "fitness=0.123456" in repr_str

    def test_repr_with_none_fitness(self):
        """Test __repr__ with None fitness value."""
        position = np.array([1, 0])  # 1 feature selected
        continuous_position = np.array([1.0, -1.0])
        fitness = None

        body = CelestialBody(position, continuous_position, fitness)
        repr_str = repr(body)

        assert "CelestialBody" in repr_str
        assert "features=1/2" in repr_str
        assert "fitness=N/A" in repr_str


class TestCelestialBodyProposedPosition:
    """Test proposed_binary_position functionality."""

    def test_proposed_position_initialization(self):
        """Test that proposed_binary_position starts as None."""
        position = np.array([1, 0])
        continuous_position = np.array([1.0, -1.0])
        fitness = 0.5

        body = CelestialBody(position, continuous_position, fitness)
        assert body.proposed_binary_position is None

    def test_proposed_position_assignment(self):
        """Test assigning to proposed_binary_position."""
        position = np.array([1, 0])
        continuous_position = np.array([1.0, -1.0])
        fitness = 0.5

        body = CelestialBody(position, continuous_position, fitness)
        proposed = np.array([0, 1])
        body.proposed_binary_position = proposed

        assert np.array_equal(body.proposed_binary_position, proposed)

        # Original position should be unchanged
        assert np.array_equal(body.position, [1, 0])


if __name__ == "__main__":
    pytest.main([__file__])
