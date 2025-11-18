"""
Initialization module for Binary CEO algorithm.

This module handles the creation of the initial population of celestial bodies,
which is the "Big Bang" of the algorithm. Proper initialization with diversity
and validity is crucial for effective exploration of the search space.
"""

from typing import Any, Callable, List, Tuple

import numpy as np

from .solution import CelestialBody


def create_sparse_binary_vector(
    n_features: int, selection_probability: float = 0.1, min_features: int = 1
) -> np.ndarray:
    """
    Create a sparse binary vector for feature selection.

    Uses a low selection probability to avoid starting with too many features,
    which would slow down fitness evaluation significantly.

    Args:
        n_features: Total number of features
        selection_probability: Probability of each feature being selected (default: 0.1)
        min_features: Minimum number of features to select (default: 1)

    Returns:
        Binary vector of shape (n_features,) with at least min_features ones
    """
    # Generate sparse binary vector
    position = (np.random.rand(n_features) < selection_probability).astype(int)

    # Edge case: Ensure at least min_features are selected
    # This prevents zero-vectors which would crash fitness evaluation
    if np.sum(position) < min_features:
        # Randomly select min_features positions to flip to 1
        zero_indices = np.where(position == 0)[0]
        selected_indices = np.random.choice(
            zero_indices, size=min_features, replace=False
        )
        position[selected_indices] = 1

    return position


def initialize_population(
    pop_size: int,
    n_features: int,
    objective_function: Callable,
    selection_probability: float = 0.1,
    continuous_init: str = "from_position",
    continuous_range: Tuple[float, float] = (-1.0, 1.0),
    min_features: int = 1,
    verbose: bool = True,
    termination_criteria=None,
    **obj_func_kwargs: Any,
) -> Tuple[List[CelestialBody], np.ndarray, float]:
    """
    Initialize the population for Binary CEO algorithm.

    This is the "Big Bang" of your algorithm - it creates the initial universe
    of celestial bodies (solutions) with diversity and validity.

    Args:
        pop_size: Number of solutions in the population
        n_features: Total number of features in the dataset
        objective_function: Function to evaluate fitness. Must have signature:
            objective_function(position, **kwargs) -> float
        selection_probability: Probability of each feature being selected initially
        continuous_init: Initialization strategy for continuous_position:
            - "from_position" (default): Initialize from binary position with noise
            - "zero": Initialize to zeros (not recommended)
            - "random": Random initialization in continuous_range
        continuous_range: Range for random continuous_position initialization
            (if continuous_init="random")
        min_features: Minimum number of features per solution
        verbose: Whether to print progress messages
        termination_criteria: Optional TerminationCriteria instance for counting
            evaluations
        **obj_func_kwargs: Additional keyword arguments to pass to objective_function

    Returns:
        Tuple of (population, global_best_position, global_best_fitness):
        - population: List of CelestialBody objects
        - global_best_position: Binary vector of the best solution found
        - global_best_fitness: Fitness score of the best solution

    Example:
        >>> def fitness_func(position, X, y, model):
        ...     # Your fitness calculation
        ...     return score
        >>>
        >>> population, best_pos, best_fit = initialize_population(
        ...     pop_size=50,
        ...     n_features=1000,
        ...     objective_function=fitness_func,
        ...     X=X_train,
        ...     y=y_train,
        ...     model=my_classifier
        ... )
    """
    if verbose:
        print(f"Initializing {pop_size} solutions with {n_features} features...")
        print("This may take time as each solution requires fitness evaluation.")

    population = []
    global_best_fitness = float("inf")
    global_best_position = None

    for i in range(pop_size):
        # Component 1: Create sparse binary position vector
        position = create_sparse_binary_vector(
            n_features=n_features,
            selection_probability=selection_probability,
            min_features=min_features,
        )

        # Component 2: Initialize continuous_position
        # Map binary position to continuous space with noise
        if continuous_init == "zero":
            # Old behavior for backward compatibility, but not recommended
            continuous_position = np.zeros(n_features, dtype=float)
        elif continuous_init == "random":
            continuous_position = np.random.uniform(
                continuous_range[0], continuous_range[1], size=n_features
            )
        elif continuous_init == "from_position":
            # NEW: Initialize from binary position with noise
            # Map: 1 -> ~+2.0, 0 -> ~-2.0 (these give sigmoid ≈ 0.88, 0.12)
            continuous_position = np.where(
                position == 1,
                2.0 + np.random.normal(0, 0.3, size=n_features),  # 1 -> ~2.0 ± noise
                -2.0 + np.random.normal(0, 0.3, size=n_features),  # 0 -> ~-2.0 ± noise
            )
        else:
            raise ValueError(
                f"Invalid continuous_init: {continuous_init}. "
                "Must be 'zero', 'random', or 'from_position'."
            )

        # Component 3: Calculate fitness (THE BOTTLENECK)
        fitness = objective_function(position, **obj_func_kwargs)

        # Count this fitness evaluation
        if termination_criteria is not None:
            termination_criteria.increment_fitness_evals()

        # Create celestial body
        body = CelestialBody(
            position=position, continuous_position=continuous_position, fitness=fitness
        )
        population.append(body)

        # Component 4: Track global best
        if fitness < global_best_fitness:
            global_best_fitness = fitness
            global_best_position = position.copy()  # MUST copy, not reference

        if verbose and (i + 1) % max(1, pop_size // 10) == 0:
            print(
                f"  Initialized {i + 1}/{pop_size} solutions... "
                f"(Best so far: {global_best_fitness:.6f})"
            )

    if verbose:
        n_selected = np.sum(global_best_position)
        print("Initialization complete!")
        print(f"  Best fitness: {global_best_fitness:.6f}")
        print(f"  Best solution: {n_selected}/{n_features} features selected")

    return population, global_best_position, global_best_fitness


def initialize_from_custom_positions(
    positions: List[np.ndarray],
    objective_function: Callable,
    continuous_init: str = "from_position",
    continuous_range: Tuple[float, float] = (-1.0, 1.0),
    verbose: bool = True,
    termination_criteria=None,
    **obj_func_kwargs: Any,
) -> Tuple[List[CelestialBody], np.ndarray, float]:
    """
    Initialize population from custom position vectors.

    Useful for warm-starting the algorithm with prior knowledge or
    solutions from another algorithm.

    Args:
        positions: List of binary position vectors
        objective_function: Function to evaluate fitness
        continuous_init: Initialization strategy for continuous_position:
            - "from_position" (default): Initialize from binary position with noise
            - "zero": Initialize to zeros (not recommended)
            - "random": Random initialization in continuous_range
        continuous_range: Range for random continuous_position initialization
        verbose: Whether to print progress messages
        termination_criteria: Optional TerminationCriteria instance for counting
            evaluations
        **obj_func_kwargs: Additional arguments for objective_function

    Returns:
        Tuple of (population, global_best_position, global_best_fitness)
    """
    if verbose:
        print(f"Initializing {len(positions)} solutions from custom positions...")

    population = []
    global_best_fitness = float("inf")
    global_best_position = None

    for i, position in enumerate(positions):
        # Validate position
        if not np.all((position == 0) | (position == 1)):
            raise ValueError(
                f"Position {i} is not binary (contains values other than 0 or 1)"
            )

        if np.sum(position) == 0:
            raise ValueError(f"Position {i} has no features selected (all zeros)")

        # Initialize continuous_position
        n_features = len(position)
        if continuous_init == "zero":
            continuous_position = np.zeros(n_features, dtype=float)
        elif continuous_init == "random":
            continuous_position = np.random.uniform(
                continuous_range[0], continuous_range[1], size=n_features
            )
        elif continuous_init == "from_position":
            # Initialize from binary position with noise
            continuous_position = np.where(
                position == 1,
                2.0 + np.random.normal(0, 0.3, size=n_features),
                -2.0 + np.random.normal(0, 0.3, size=n_features),
            )
        else:
            raise ValueError(
                f"Invalid continuous_init: {continuous_init}. "
                "Must be 'zero', 'random', or 'from_position'."
            )

        # Calculate fitness
        fitness = objective_function(position, **obj_func_kwargs)

        # Count this fitness evaluation
        if termination_criteria is not None:
            termination_criteria.increment_fitness_evals()

        # Create body
        body = CelestialBody(
            position=position, continuous_position=continuous_position, fitness=fitness
        )
        population.append(body)

        # Track global best
        if fitness < global_best_fitness:
            global_best_fitness = fitness
            global_best_position = position.copy()

    if verbose:
        print(
            f"Custom initialization complete! Best fitness: {global_best_fitness:.6f}"
        )

    return population, global_best_position, global_best_fitness
