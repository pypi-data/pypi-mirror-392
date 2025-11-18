"""
Position update module for Binary CEO algorithm.

This module contains the main orchestrator for updating all celestial body positions
in one iteration, along with force generators and helper translation functions.
"""

from typing import Dict, List

import numpy as np

from .solution import CelestialBody

# ============================================================================
# Local Search (Module 4d) configuration
# ============================================================================

# Maximum number of neighbors to evaluate around a body in local search
LOCAL_SEARCH_MAX_NEIGHBORS = 10

# Maximum number of bits to flip when generating a single neighbor
LOCAL_SEARCH_MAX_BIT_FLIPS = 2


# ============================================================================
# Main Orchestrator
# ============================================================================


def update_all_positions(
    stellar_systems: List[List[CelestialBody]],
    global_best_body: CelestialBody,
    population: List[CelestialBody],
    params: Dict,
    iteration: int,
    max_iter: int,
) -> List[CelestialBody]:
    """
    Update positions for all celestial bodies in the population for one iteration.

    This is the main orchestrator function that manages the entire position update
    process. It calculates forces, updates continuous positions, and generates
    binary proposals for each follower body in each stellar system.

    Args:
        stellar_systems: List of stellar systems (each system is a List[CelestialBody])
        global_best_body: The best solution found so far (copy)
        population: The entire population list
        params: Dictionary of hyperparameters including:
            - c1: Local attraction coefficient
            - c2: Global attraction coefficient
            - a: Expansion force coefficient
            - W1: Expansion force weight
            - lb: Lower bound for clamping continuous_position
            - ub: Upper bound for clamping continuous_position
        iteration: Current iteration number (t)
        max_iter: Maximum iterations (T)

    Returns:
        The modified population list (modified in-place, but returned for convenience)

    Notes:
        - This function modifies bodies in-place
        - Each follower body will have its continuous_position updated
        - Each follower body will have a new proposed_binary_position attribute
        - Leaders are not updated (they guide followers)
    """

    # Safety check for empty population
    if not population:
        return population

    # Determine dimensions of the problem
    n_features = len(population[0].continuous_position)
    # Pre-calculate population center for expansion force
    # Average of all continuous positions in the population
    # (Currently unused but may be needed for future enhancements)
    _ = np.array([body.continuous_position for body in population])
    _ = np.mean([body.continuous_position for body in population], axis=0)

    # Loop 1: Iterate through each stellar system
    for system in stellar_systems:
        if len(system) == 0:
            continue

        # Identify the leader (first body in the system, best fitness)
        leader = system[0]

        # Loop 2: Iterate through each follower in the system
        for body in system[1:]:  # Skip the leader
            # Calculate the three force components

            # Force A: Local gravitational pull toward system leader
            force_a = _calculate_gravity_F(body, leader, params)

            # Force B: Global gravitational pull toward global best
            force_b = _calculate_gravity_A(
                body, global_best_body, params, iteration, max_iter
            )

            # Force C: Expansion force (exploration pressure)
            force_c = _calculate_expansion_force(
                params, iteration, max_iter, n_features
            )

            # Sum all forces to get total force
            total_force = force_a + force_b + force_c

            # Apply update equation (Eq. 14): new_pos = old_pos + total_force
            new_continuous_pos = body.continuous_position + total_force

            # Clamp vector to prevent extreme values
            # This is critical to prevent the "natural brake" from failing
            lb = params.get("lb", -6.0)
            ub = params.get("ub", 6.0)
            new_continuous_pos = np.clip(new_continuous_pos, lb, ub)

            # Store the new continuous state
            body.continuous_position = new_continuous_pos

            # Generate binary proposal for selection module to test
            body.proposed_binary_position = _generate_binary_proposal(
                body.continuous_position
            )

    return population


# ============================================================================
# Force Generators (Sub-modules 4a, 4b, 4c)
# ============================================================================


def _calculate_gravity_F(
    body: CelestialBody, leader: CelestialBody, params: Dict
) -> np.ndarray:
    """
    Calculate local gravitational pull toward system leader (Module 4a).

    This implements a simplified version of the "Comprehensive Force" F(t).
    It creates a strong pull toward the local leader, with a "natural brake"
    that automatically weakens as the body gets closer to the leader.

    Args:
        body: The follower celestial body
        leader: The leader of the stellar system
        params: Dictionary containing 'c1' (local attraction coefficient)

    Returns:
        Force vector (continuous) pointing toward leader

    Notes:
        - The "natural brake": As body approaches leader, direction shrinks,
          and the force automatically weakens
        - Random component adds stochasticity for exploration
    """
    c1 = params["c1"]  # e.g., 0.5

    # Calculate direction vector from body to leader
    direction = leader.continuous_position - body.continuous_position

    # Apply force with random component
    # The closer the body is to the leader, the smaller the direction vector,
    # creating an automatic "braking" effect
    force = c1 * np.random.rand() * direction

    return force


def _calculate_gravity_A(
    body: CelestialBody,
    global_best_body: CelestialBody,
    params: Dict,
    iteration: int,
    max_iter: int,
) -> np.ndarray:
    """
    Calculate global gravitational pull toward global best (Module 4b).

    This force pulls bodies toward the globally best solution found so far.
    The force magnitude is modulated to increase over iterations,
    strengthening exploitation as the search progresses.

    Args:
        body: The celestial body being updated
        global_best_body: The global best solution
        params: Dictionary containing 'c2' (global attraction coefficient)
        iteration: Current iteration number (t)
        max_iter: Maximum iterations (T)

    Returns:
        Force vector (continuous) pointing toward global best
    """
    # --- START OF NEW IMPLEMENTATION (Module 4b) ---

    # Get global attraction coefficient from params
    c2 = params["c2"]

    # Calculate the direction vector toward the global best solution
    direction = global_best_body.continuous_position - body.continuous_position

    # Calculate the adaptive weight.
    # This value scales from 0 (at iteration 0) to 1 (at max_iter),
    # making the pull toward the global best (exploitation) stronger over time.
    adaptive_weight = iteration / max_iter if max_iter > 0 else 0

    # Get a random component for stochasticity, just like local gravity
    r = np.random.rand()

    # Calculate the final force
    # force = c2 * adaptive_weight * r * (X_gbest - X_body)
    force = c2 * adaptive_weight * r * direction

    return force


def _calculate_expansion_force(
    params: Dict, iteration: int, max_iter: int, n_features: int
) -> np.ndarray:
    """
    Calculate expansion force for exploration (Module 4c).

    This force encourages exploration of the search space, particularly
    in early iterations. It typically decreases over time to allow
    convergence in later iterations.

    Args:
        params: Dictionary containing:
            - 'a': Expansion coefficient
            - 'W1': Expansion weight
            - Additional parameters as needed
        iteration: Current iteration number (t)
        max_iter: Maximum iterations (T)

    Returns:
        Force vector (continuous) for expansion

    TODO: Implement this function with:
        - Time-decaying expansion magnitude
        - Random direction generation
        - Proper scaling with iteration progress
    """

    # 1. Extract parameters
    W1 = params.get("W1", 0.1)  # Default weight if not provided
    lb = params.get("lb", -6.0)
    ub = params.get("ub", 6.0)

    t = iteration
    T = max_iter if max_iter > 0 else 1  # Prevent division by zero

    # 2. Calculate the decay rate (Eq. 3)
    # The force is strong initially (exploration) and weak later (convergence)
    decay_rate = W1 * (1 - 0.001 * (t / T)) * np.exp(-4 * (t / T))

    # 3. Calculate bounds range
    bounds_range = ub - lb

    # 4. Calculate final force (Eq. 14 logic)
    # Uses random normal distribution (randn) for direction
    force = decay_rate * np.random.randn(n_features) * bounds_range

    return force


# ============================================================================
# Helper Functions (Translation Tools)
# ============================================================================


def _generate_binary_proposal(continuous_vector: np.ndarray) -> np.ndarray:
    """
    Generate a binary position proposal from a continuous vector.

    This is the main translation function that converts the continuous
    representation into a binary solution that can be evaluated.

    Args:
        continuous_vector: Continuous position vector (e.g., [2.1, -1.5, 0.1])

    Returns:
        Binary vector (e.g., [1, 0, 1])

    Process:
        1. Apply sigmoid to get probabilities: [2.1, -1.5, 0.1] -> [0.89, 0.18, 0.52]
        2. Stochastic binarization: [0.89, 0.18, 0.52] -> [1, 0, 1]
    """
    # Step 1: Convert continuous values to probabilities using sigmoid
    prob_vector = _sigmoid(continuous_vector)

    # Step 2: Stochastically convert probabilities to binary
    binary_vector = _stochastic_binarize(prob_vector)

    return binary_vector


def _sigmoid(x: np.ndarray) -> np.ndarray:
    """
    Apply sigmoid function to convert continuous values to probabilities.

    Args:
        x: Continuous vector

    Returns:
        Probability vector in range [0, 1]

    Notes:
        - Uses clipping to prevent overflow in exp calculation
        - Sigmoid: σ(x) = 1 / (1 + e^(-x))
    """
    # Clip x to prevent overflow in exp calculation
    # Typical range: [-500, 500] is safe for most systems
    x_clipped = np.clip(x, -500, 500)

    # Apply sigmoid function
    return 1.0 / (1.0 + np.exp(-x_clipped))


def _stochastic_binarize(prob_vector: np.ndarray) -> np.ndarray:
    """
    Stochastically convert probability vector to binary vector.

    For each element, generate a random number and compare it to the
    probability. If random < probability, set to 1, else set to 0.

    Args:
        prob_vector: Vector of probabilities in range [0, 1]

    Returns:
        Binary vector (0s and 1s)

    Example:
        prob_vector = [0.9, 0.2, 0.5]
        random_vec = [0.3, 0.8, 0.4]  (generated internally)
        result = [1, 0, 1]  (0.3 < 0.9: yes, 0.8 < 0.2: no, 0.4 < 0.5: yes)
    """
    # Generate random values for each feature
    random_vec = np.random.rand(len(prob_vector))

    # Compare and binarize: 1 if random < probability, else 0
    binary_vector = np.where(random_vec < prob_vector, 1, 0)

    return binary_vector


# ============================================================================
# Local Search Function
# ============================================================================


def local_search(
    body: CelestialBody,
    objective_function,
    termination_criteria=None,
    **obj_func_kwargs,
) -> CelestialBody:
    """
    Local search (Celestial Resonance) around a given celestial body (Module 4d).

    This function refines a single celestial body's position by exploring
    a small neighborhood in the binary search space. It is intended to be
    used after the main position update step to locally polish solutions.

    Strategy (best-improvement hill climbing with random neighbors):
    - Define a neighborhood by flipping a small number of bits in the
      current binary position.
    - Sample up to LOCAL_SEARCH_MAX_NEIGHBORS neighbors.
    - Evaluate neighbors with the objective function.
    - Move the body to the best neighbor if an improvement is found.
      (Minimization is assumed.)

    Notes:
        - Ensures we do not evaluate all-zero vectors (no selected features),
          as these typically break the fitness evaluation for feature selection.
        - Does NOT modify continuous_position; it will be updated again by
          the main position update operator in the next iteration.

    Args:
        body: The celestial body to improve via local search
        objective_function: Fitness evaluation function. It must accept a
            binary numpy array of shape (n_features,) as the first argument
        termination_criteria: Optional TerminationCriteria instance for counting
            evaluations
        **obj_func_kwargs: Additional keyword arguments for the objective
            function (e.g., X, y, accuracy_weight, etc)

    Returns:
        CelestialBody: The same body instance, possibly with improved
        position and fitness
    """
    # Safety checks and current state
    # ------------------------------------------------------------------
    if body.position is None:
        # Nothing to refine
        return body

    current_pos = np.array(body.position, dtype=int)
    n_features = current_pos.shape[0]

    if n_features == 0:
        # Degenerate edge case: no features
        return body

    # If fitness is unknown, evaluate it once
    if body.fitness is None:
        current_fit = objective_function(current_pos, **obj_func_kwargs)
        # Count this fitness evaluation
        if termination_criteria is not None:
            termination_criteria.increment_fitness_evals()
    else:
        current_fit = body.fitness

    best_pos = current_pos.copy()
    best_fit = current_fit

    # ------------------------------------------------------------------
    # Neighborhood exploration
    # ------------------------------------------------------------------
    n_neighbors = min(LOCAL_SEARCH_MAX_NEIGHBORS, n_features)
    max_bit_flips = max(1, min(LOCAL_SEARCH_MAX_BIT_FLIPS, n_features))

    for _ in range(n_neighbors):
        # Randomly choose how many bits to flip in this neighbor
        if n_features == 1:
            k = 1
        else:
            k = np.random.randint(1, max_bit_flips + 1)

        # Choose distinct indices to flip
        flip_indices = np.random.choice(n_features, size=k, replace=False)

        neighbor = best_pos.copy()
        neighbor[flip_indices] = 1 - neighbor[flip_indices]  # bit-flip

        # Avoid all-zero vectors (no feature selected)
        if neighbor.sum() == 0:
            continue

        # Evaluate neighbor
        nb_fit = objective_function(neighbor, **obj_func_kwargs)
        # Count this fitness evaluation
        if termination_criteria is not None:
            termination_criteria.increment_fitness_evals()

        # Minimization: keep strictly better neighbor
        if nb_fit < best_fit:
            best_fit = nb_fit
            best_pos = neighbor

    # ------------------------------------------------------------------
    # Update body if an improvement was found
    # ------------------------------------------------------------------
    if best_fit < current_fit:
        body.position = best_pos
        body.fitness = best_fit
        # We deliberately do not touch continuous_position here.
        # The main position-update step (forces) will adjust it in
        # subsequent iterations.

    return body
