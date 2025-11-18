# src/binaryceo/partitioning.py

from typing import Dict, List

import numpy as np

# Assuming your CelestialBody class is in a sibling 'solution' module
from .solution import CelestialBody


# Helper function for clarity
def _calculate_hamming_distance(pos1: np.ndarray, pos2: np.ndarray) -> int:
    """Calculates the Hamming distance between two binary vectors."""
    return np.sum(pos1 != pos2)


def _partition_by_distance_to_leaders(
    population: List[CelestialBody], n_systems: int
) -> List[List[CelestialBody]]:
    """
    Partitions the population by finding leaders and assigning followers based on
    the minimum Hamming distance.
    """
    if n_systems <= 0:
        raise ValueError("Number of systems must be positive.")
    if len(population) < n_systems:
        # If there are fewer bodies than systems, put each body in its own system.
        return [[body] for body in population]

    # 1. Sort the population by fitness (ascending, as lower is better)
    sorted_pop = sorted(population, key=lambda body: body.fitness)

    # 2. Select the top 'n_systems' bodies as leaders
    leaders = sorted_pop[:n_systems]
    followers = sorted_pop[n_systems:]

    # 3. Create the stellar systems dictionary, keyed by leader object ID for uniqueness
    #    This ensures each leader has its own system.
    stellar_systems_dict: Dict[int, List[CelestialBody]] = {
        id(leader): [leader] for leader in leaders
    }

    # 4. For every follower, assign it to the system of the closest leader
    for body in followers:
        min_distance = float("inf")
        closest_leader = None

        for leader in leaders:
            distance = _calculate_hamming_distance(body.position, leader.position)
            if distance < min_distance:
                min_distance = distance
                closest_leader = leader

        # Assign the body to the system of the determined closest leader
        if closest_leader is not None:
            stellar_systems_dict[id(closest_leader)].append(body)

    # 5. Return the partitions as a list of lists
    return list(stellar_systems_dict.values())


def _partition_by_fitness(
    population: List[CelestialBody], n_systems: int
) -> List[List[CelestialBody]]:
    """Partitions the population by sorting by fitness and creating equal chunks."""
    sorted_pop = sorted(population, key=lambda body: body.fitness)

    systems = []
    bodies_per_system = len(sorted_pop) // n_systems

    for i in range(n_systems):
        start = i * bodies_per_system
        # Ensure the last system gets all remaining bodies
        end = start + bodies_per_system if i < n_systems - 1 else len(sorted_pop)
        systems.append(sorted_pop[start:end])

    return systems


def _partition_randomly(
    population: List[CelestialBody], n_systems: int
) -> List[List[CelestialBody]]:
    """Randomly assigns bodies to systems."""
    shuffled = population.copy()
    np.random.shuffle(shuffled)

    systems = [[] for _ in range(n_systems)]
    for i, body in enumerate(shuffled):
        system_idx = i % n_systems
        systems[system_idx].append(body)

    return systems


# This is the main function you will call from your algorithm's main loop
def partition_stellar_systems(
    population: List[CelestialBody], n_systems: int = 3, method: str = "distance_based"
) -> List[List[CelestialBody]]:
    """
    Partition population into stellar systems using a specified method.

    Args:
        population: List of CelestialBody objects.
        n_systems: The number of stellar systems to create.
        method: The partitioning strategy. Supported: "distance_based",
                "fitness_based", "random".

    Returns:
        A list of stellar systems, where each system is a List[CelestialBody].
    """
    if method == "distance_based":
        # This is the method described in your primary modular plan
        return _partition_by_distance_to_leaders(population, n_systems)
    elif method == "fitness_based":
        return _partition_by_fitness(population, n_systems)
    elif method == "random":
        return _partition_randomly(population, n_systems)
    else:
        raise ValueError(f"Unknown partitioning method: {method}")
