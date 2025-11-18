from typing import Callable, List, Optional

import numpy as np

from .solution import CelestialBody


def selection_step(
    population: List[CelestialBody],
    objective_function: Callable,
    global_best_body: Optional[CelestialBody] = None,
    termination_criteria=None,
    **obj_func_kwargs,
) -> CelestialBody:
    """
    Module 5: Solution Selection (Accept–Reject Step)

    Goes through each body in the population, evaluates any proposed
    binary positions (generated during the position update step), and
    decides whether to accept or reject them based on fitness.

    Assumptions:
        - Minimization problem: lower fitness is better.
        - Each CelestialBody may or may not have an attribute
          'proposed_binary_position' (np.ndarray of 0/1).
        - If 'proposed_binary_position' is missing or None, the body
          is left unchanged.
        - If body.fitness is None, it will be evaluated using its
          current position before comparison.

    Args:
        population: List of CelestialBody objects (current population).
        objective_function: Function used to evaluate fitness. It must
            accept a binary numpy array as its first argument, plus any
            additional keyword arguments (**obj_func_kwargs).
        global_best_body: Current global best CelestialBody. May be None
            on the very first call.
        termination_criteria: Optional TerminationCriteria instance for counting
            evaluations.
        **obj_func_kwargs: Extra arguments passed to the objective
            function (e.g., X, y, accuracy_weight, etc.).

    Returns:
        Updated global_best_body after processing the entire population.
    """
    # ------------------------------------------------------------------
    # Ensure global_best_body is a valid CelestialBody reference
    # ------------------------------------------------------------------
    if global_best_body is None and len(population) > 0:
        # Initialize global best as the best in current population
        # (after making sure each has a valid fitness value).
        best_candidate = None
        best_fit = None

        for body in population:
            # If fitness is unknown, evaluate it once
            if body.fitness is None and body.position is not None:
                body.fitness = objective_function(
                    np.array(body.position, dtype=int),
                    **obj_func_kwargs,
                )
                # Count this fitness evaluation
                if termination_criteria is not None:
                    termination_criteria.increment_fitness_evals()

            if body.fitness is None:
                continue

            if best_fit is None or body.fitness < best_fit:
                best_fit = body.fitness
                best_candidate = body

        if best_candidate is not None:
            global_best_body = best_candidate

    # If still None (e.g., empty population), just return
    if global_best_body is None:
        return global_best_body

    # ------------------------------------------------------------------
    # Process each body: accept or reject proposed positions
    # ------------------------------------------------------------------
    for body in population:
        # Ensure current fitness is known
        if body.position is not None and body.fitness is None:
            body.fitness = objective_function(
                np.array(body.position, dtype=int),
                **obj_func_kwargs,
            )
            # Count this fitness evaluation
            if termination_criteria is not None:
                termination_criteria.increment_fitness_evals()

        # If no proposed position, nothing to do for this body
        proposed = getattr(body, "proposed_binary_position", None)
        if proposed is None:
            continue

        proposed = np.array(proposed, dtype=int)

        # Ignore degenerate all-zero masks (no selected features)
        if proposed.size == 0 or proposed.sum() == 0:
            # Clear proposal and move on
            body.proposed_binary_position = None
            continue

        # Evaluate the proposed solution
        proposed_fitness = objective_function(
            proposed,
            **obj_func_kwargs,
        )
        # Count this fitness evaluation
        if termination_criteria is not None:
            termination_criteria.increment_fitness_evals()

        # If body had no fitness yet, treat any valid proposed fitness
        # as a current baseline
        if body.fitness is None or proposed_fitness < body.fitness:
            # Accept the proposed solution
            body.position = proposed
            body.fitness = proposed_fitness

        # Clear proposal after decision
        body.proposed_binary_position = None

        # Update global best if this body is now the best
        if global_best_body.fitness is None or body.fitness < global_best_body.fitness:
            global_best_body = body

    return global_best_body
