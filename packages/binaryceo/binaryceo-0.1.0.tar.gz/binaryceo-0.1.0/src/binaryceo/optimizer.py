"""
High-level optimizer for the Binary Cosmic Evolution Optimization (BinaryCEO) algorithm.

This module glues together:
    - Initialization (Big Bang)
    - Stellar system partitioning
    - Position update (forces + binarization)
    - Local search (Module 4d)
    - Selection / accept–reject (Module 5)

and provides a single function `run_binary_ceo` that can be used for feature
selection on tabular datasets.
"""

from typing import Any, Dict, Optional

import numpy as np

from .fitness import multi_objective_fitness
from .initialization import initialize_population
from .partitioning import partition_stellar_systems
from .position_update import local_search, update_all_positions
from .selection import selection_step
from .solution import CelestialBody
from .termination import TerminationCriteria


def run_binary_ceo(
    X: np.ndarray,
    y: np.ndarray,
    model: object,
    pop_size: int = 30,
    max_iter: int = 50,
    n_systems: int = 3,
    partition_method: str = "distance_based",
    selection_probability: float = 0.1,
    continuous_init: str = "from_position",
    continuous_range: tuple = (-1.0, 1.0),
    min_features: int = 1,
    accuracy_weight: float = 0.7,
    cv_folds: int = 3,
    local_search_enabled: bool = True,
    local_search_mode: str = "global_best",  # "global_best", "top_k", "all"
    local_search_top_k: int = 3,
    position_update_params: Optional[Dict[str, Any]] = None,
    objective_function=multi_objective_fitness,
    random_state: Optional[int] = None,
    verbose: bool = True,
    # Termination criteria parameters
    fitness_threshold: Optional[float] = None,
    stagnation_iters: Optional[int] = None,
    min_diversity: Optional[float] = None,
    max_fitness_evals: Optional[int] = None,
    time_limit_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run the Binary CEO algorithm end-to-end for feature selection.

    Args:
        X: Feature matrix of shape (n_samples, n_features).
        y: Target vector of shape (n_samples,).
        model: A scikit-learn compatible estimator with fit/predict.
        pop_size: Number of celestial bodies (solutions) in the population.
        max_iter: Number of optimization iterations (generations).
        n_systems: Number of stellar systems for partitioning.
        partition_method: One of {"distance_based", "fitness_based", "random"}.
        selection_probability: Initial probability of selecting each feature.
        continuous_init: Strategy for continuous_position initialization
            ("zero" or "random").
        continuous_range: Bounds for random continuous initialization.
        min_features: Minimum number of features per solution.
        accuracy_weight: Weight given to classification error vs sparsity
            in the multi-objective fitness.
        cv_folds: Number of CV folds used in fitness evaluation.
        local_search_enabled: Whether to run local search (Module 4d).
        local_search_mode: "global_best" (default), "top_k", or "all".
        local_search_top_k: If mode == "top_k", how many top bodies to refine.
        position_update_params: Dictionary with parameters for the position
            update step (e.g., c1, c2, a, W1, lb, ub).
        objective_function: Fitness function, default = multi_objective_fitness.
        random_state: Optional seed for NumPy RNG.
        verbose: If True, prints progress each iteration.
        fitness_threshold: Stop if global best fitness reaches this value.
        stagnation_iters: Stop if no improvement for this many iterations.
        min_diversity: Stop if population diversity falls below this threshold.
        max_fitness_evals: Stop after this many fitness function evaluations.
        time_limit_seconds: Stop after this many seconds.

    Returns:
        Dictionary with:
            - "best_body": CelestialBody (best solution found).
            - "best_position": np.ndarray (binary mask).
            - "best_fitness": float.
            - "history": dict with lists of "best_fitness" and "num_features".
    """
    if random_state is not None:
        np.random.seed(random_state)

    n_features = X.shape[1]

    # Initialize termination criteria
    termination_criteria = TerminationCriteria(
        max_iter=max_iter,
        fitness_threshold=fitness_threshold,
        stagnation_iters=stagnation_iters,
        min_diversity=min_diversity,
        max_fitness_evals=max_fitness_evals,
        time_limit_seconds=time_limit_seconds,
        verbose=verbose,
    )
    termination_criteria.start_timing()

    # Default parameters for position update if not provided
    if position_update_params is None:
        position_update_params = {
            "c1": 0.5,  # local attraction coefficient
            "c2": 0.5,  # global attraction coefficient
            "a": 1.0,  # expansion coefficient
            "W1": 0.1,  # expansion weight
            "lb": continuous_range[0],
            "ub": continuous_range[1],
        }

    # Objective function kwargs shared across all fitness evaluations
    obj_func_kwargs: Dict[str, Any] = {
        "X": X,
        "y": y,
        "model": model,
        "accuracy_weight": accuracy_weight,
        "cv_folds": cv_folds,
    }

    # ------------------------------------------------------------------
    # Step 1: Initialization (Big Bang)
    # ------------------------------------------------------------------
    if verbose:
        print("[BinaryCEO] Initializing population...")

    population, _, _ = initialize_population(
        pop_size=pop_size,
        n_features=n_features,
        objective_function=objective_function,
        selection_probability=selection_probability,
        continuous_init=continuous_init,
        continuous_range=continuous_range,
        min_features=min_features,
        verbose=verbose,
        termination_criteria=termination_criteria,
        **obj_func_kwargs,
    )

    # Determine initial global best body
    global_best_body: CelestialBody = min(
        population,
        key=lambda b: b.fitness if b.fitness is not None else np.inf,
    )

    history = {
        "best_fitness": [],
        "num_features": [],
    }

    # ------------------------------------------------------------------
    # Main optimization loop
    # ------------------------------------------------------------------
    it = 0
    while True:
        if verbose:
            print(f"[BinaryCEO] Iteration {it + 1}")

        # Step 2: Partition into stellar systems
        stellar_systems = partition_stellar_systems(
            population=population,
            n_systems=n_systems,
            method=partition_method,
        )

        # Step 3: Position update (forces + binarization proposal)
        update_all_positions(
            stellar_systems=stellar_systems,
            global_best_body=global_best_body,
            population=population,
            params=position_update_params,
            iteration=it,
            max_iter=max_iter,
        )

        # Step 4: Selection step (accept/reject proposed_binary_position)
        global_best_body = selection_step(
            population=population,
            objective_function=objective_function,
            global_best_body=global_best_body,
            termination_criteria=termination_criteria,
            **obj_func_kwargs,
        )

        # Step 5: Optional local search (Module 4d)
        if local_search_enabled:
            if local_search_mode == "global_best":
                # Refine only the current global best body
                local_search(
                    global_best_body,
                    objective_function=objective_function,
                    termination_criteria=termination_criteria,
                    **obj_func_kwargs,
                )
            elif local_search_mode == "top_k":
                # Refine top-k solutions by fitness
                sorted_pop = sorted(
                    population,
                    key=lambda b: b.fitness if b.fitness is not None else np.inf,
                )
                for body in sorted_pop[: max(1, local_search_top_k)]:
                    local_search(
                        body,
                        objective_function=objective_function,
                        termination_criteria=termination_criteria,
                        **obj_func_kwargs,
                    )
            elif local_search_mode == "all":
                for body in population:
                    local_search(
                        body,
                        objective_function=objective_function,
                        termination_criteria=termination_criteria,
                        **obj_func_kwargs,
                    )
            else:
                raise ValueError(
                    f"Unknown local_search_mode: {local_search_mode}. "
                    "Use 'global_best', 'top_k', or 'all'."
                )

            # After local search, refresh global best from population
            global_best_body = min(
                population,
                key=lambda b: b.fitness if b.fitness is not None else np.inf,
            )

        # Step 6: Log history
        if global_best_body.position is not None:
            n_selected = int(np.sum(global_best_body.position))
        else:
            n_selected = 0

        history["best_fitness"].append(float(global_best_body.fitness))
        history["num_features"].append(n_selected)

        if verbose:
            print(
                f"  -> Best fitness: {global_best_body.fitness:.6f}, "
                f"features selected: {n_selected}/{n_features}"
            )

        # Check termination criteria
        if termination_criteria.should_terminate(
            iteration=it,
            global_best_fitness=global_best_body.fitness,
            population=population,
        ):
            break

        it += 1

    # ------------------------------------------------------------------
    # Final result packaging
    # ------------------------------------------------------------------
    termination_stats = termination_criteria.get_statistics()

    if verbose:
        reason = termination_criteria.get_termination_reason()
        if reason:
            print(f"\n[BinaryCEO] {reason}")
        print(
            f"[BinaryCEO] Total fitness evaluations: "
            f"{termination_stats['fitness_evals']}"
        )

    result = {
        "best_body": global_best_body,
        "best_position": (
            np.array(global_best_body.position, dtype=int)
            if global_best_body.position is not None
            else None
        ),
        "best_fitness": float(global_best_body.fitness),
        "history": history,
        "termination_stats": termination_stats,
        "iterations_completed": it + 1,
    }
    return result
