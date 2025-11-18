"""
Termination criteria module for Binary CEO algorithm.

This module provides various termination conditions to determine when
the optimization algorithm should stop. Multiple criteria can be used
simultaneously to ensure robust stopping behavior.
"""

from typing import Any, Dict, List, Optional

import numpy as np

from .solution import CelestialBody


class TerminationCriteria:
    """
    Manages termination conditions for the Binary CEO algorithm.

    Supports multiple stopping criteria:
    - Maximum iterations
    - Fitness threshold
    - No improvement (stagnation)
    - Convergence (population diversity loss)
    - Maximum fitness evaluations
    - Time limit

    Usage:
        criteria = TerminationCriteria(max_iter=100, stagnation_iters=20)

        for iteration in range(max_iter):
            # ... algorithm logic ...

            if criteria.should_terminate(
                iteration=iteration,
                global_best_fitness=best_fit,
                population=population
            ):
                break
    """

    def __init__(
        self,
        max_iter: int = 100,
        fitness_threshold: Optional[float] = None,
        stagnation_iters: Optional[int] = None,
        min_diversity: Optional[float] = None,
        max_fitness_evals: Optional[int] = None,
        time_limit_seconds: Optional[float] = None,
        verbose: bool = True,
    ):
        """
        Initialize termination criteria.

        Args:
            max_iter: Maximum number of iterations (always checked)
            fitness_threshold: Stop if global best fitness reaches this value
            stagnation_iters: Stop if no improvement for this many iterations
            min_diversity: Stop if population diversity falls below this threshold
            max_fitness_evals: Stop after this many fitness function evaluations
            time_limit_seconds: Stop after this many seconds
            verbose: Whether to print termination messages
        """
        self.max_iter = max_iter
        self.fitness_threshold = fitness_threshold
        self.stagnation_iters = stagnation_iters
        self.min_diversity = min_diversity
        self.max_fitness_evals = max_fitness_evals
        self.time_limit_seconds = time_limit_seconds
        self.verbose = verbose

        # Internal state tracking
        self._best_fitness_history: List[float] = []
        self._last_improvement_iter: int = 0
        self._fitness_eval_count: int = 0
        self._start_time: Optional[float] = None

        # Termination flags
        self._termination_reason: Optional[str] = None

    def reset(self) -> None:
        """Reset the termination criteria state for a new run."""
        self._best_fitness_history = []
        self._last_improvement_iter = 0
        self._fitness_eval_count = 0
        self._start_time = None
        self._termination_reason = None

    def start_timing(self) -> None:
        """Start the timer for time-based termination."""
        import time

        self._start_time = time.time()

    def increment_fitness_evals(self, count: int = 1) -> None:
        """Increment the fitness evaluation counter."""
        self._fitness_eval_count += count

    def should_terminate(
        self,
        iteration: int,
        global_best_fitness: float,
        population: Optional[List[CelestialBody]] = None,
        **kwargs,
    ) -> bool:
        """
        Check if any termination criteria are met.

        Args:
            iteration: Current iteration number
            global_best_fitness: Current best fitness value
            population: Current population (optional, needed for diversity check)
            **kwargs: Additional arguments for custom termination logic

        Returns:
            True if algorithm should terminate, False otherwise
        """
        # Track best fitness history
        self._best_fitness_history.append(global_best_fitness)

        # Check if this is an improvement
        if len(self._best_fitness_history) > 1:
            if global_best_fitness < self._best_fitness_history[-2]:
                self._last_improvement_iter = iteration

        # Check each criterion
        if self._check_max_iterations(iteration):
            return True

        if self._check_fitness_threshold(global_best_fitness):
            return True

        if self._check_stagnation(iteration):
            return True

        if self._check_diversity(population):
            return True

        if self._check_max_fitness_evals():
            return True

        if self._check_time_limit():
            return True

        return False

    def _check_max_iterations(self, iteration: int) -> bool:
        """Check if maximum iterations reached."""
        if iteration >= self.max_iter:
            self._termination_reason = f"Maximum iterations ({self.max_iter}) reached"
            if self.verbose:
                print(f"\n⏹  Termination: {self._termination_reason}")
            return True
        return False

    def _check_fitness_threshold(self, fitness: float) -> bool:
        """Check if fitness threshold reached."""
        if self.fitness_threshold is not None:
            if fitness <= self.fitness_threshold:
                self._termination_reason = (
                    f"Fitness threshold ({self.fitness_threshold:.6f}) reached: "
                    f"current fitness = {fitness:.6f}"
                )
                if self.verbose:
                    print(f"\n🎯 Termination: {self._termination_reason}")
                return True
        return False

    def _check_stagnation(self, iteration: int) -> bool:
        """Check if algorithm has stagnated (no improvement)."""
        if self.stagnation_iters is not None:
            iters_without_improvement = iteration - self._last_improvement_iter
            if iters_without_improvement >= self.stagnation_iters:
                self._termination_reason = (
                    f"Stagnation: No improvement for {self.stagnation_iters} iterations"
                )
                if self.verbose:
                    print(f"\n💤 Termination: {self._termination_reason}")
                return True
        return False

    def _check_diversity(self, population: Optional[List[CelestialBody]]) -> bool:
        """Check if population diversity is too low (convergence)."""
        if self.min_diversity is not None and population is not None:
            diversity = calculate_population_diversity(population)
            if diversity < self.min_diversity:
                self._termination_reason = (
                    f"Low diversity: {diversity:.6f} < {self.min_diversity:.6f}"
                )
                if self.verbose:
                    print(f"\n🔄 Termination: {self._termination_reason}")
                return True
        return False

    def _check_max_fitness_evals(self) -> bool:
        """Check if maximum fitness evaluations reached."""
        if self.max_fitness_evals is not None:
            if self._fitness_eval_count >= self.max_fitness_evals:
                self._termination_reason = (
                    f"Maximum fitness evaluations ({self.max_fitness_evals}) reached"
                )
                if self.verbose:
                    print(f"\n📊 Termination: {self._termination_reason}")
                return True
        return False

    def _check_time_limit(self) -> bool:
        """Check if time limit exceeded."""
        if self.time_limit_seconds is not None and self._start_time is not None:
            import time

            elapsed = time.time() - self._start_time
            if elapsed >= self.time_limit_seconds:
                self._termination_reason = (
                    f"Time limit ({self.time_limit_seconds:.1f}s) exceeded: "
                    f"elapsed = {elapsed:.1f}s"
                )
                if self.verbose:
                    print(f"\n⏱  Termination: {self._termination_reason}")
                return True
        return False

    def get_termination_reason(self) -> Optional[str]:
        """Get the reason for termination."""
        return self._termination_reason

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the termination state.

        Returns:
            Dictionary containing:
            - fitness_evals: Number of fitness evaluations performed
            - best_fitness_history: List of best fitness values per iteration
            - last_improvement_iter: Last iteration with improvement
            - termination_reason: Reason for termination (if terminated)
        """
        stats = {
            "fitness_evals": self._fitness_eval_count,
            "best_fitness_history": self._best_fitness_history.copy(),
            "last_improvement_iter": self._last_improvement_iter,
            "termination_reason": self._termination_reason,
        }

        if self._start_time is not None:
            import time

            stats["elapsed_time"] = time.time() - self._start_time

        return stats


# ============================================================================
# Helper Functions
# ============================================================================


def calculate_population_diversity(population: List[CelestialBody]) -> float:
    """
    Calculate population diversity based on Hamming distances between positions.

    Diversity is measured as the average pairwise Hamming distance between
    all individuals in the population, normalized by the number of features.

    Args:
        population: List of CelestialBody objects

    Returns:
        Diversity value in [0, 1], where:
        - 0 = All individuals identical (no diversity)
        - 1 = Maximum diversity

    Example:
        If all solutions are identical: diversity = 0
        If solutions are maximally different: diversity ≈ 1
    """
    if len(population) < 2:
        return 1.0  # Single individual = full diversity (no comparison)

    n_features = len(population[0].position)
    total_distance = 0.0
    count = 0

    # Calculate pairwise Hamming distances
    for i in range(len(population)):
        for j in range(i + 1, len(population)):
            hamming_dist = np.sum(population[i].position != population[j].position)
            total_distance += hamming_dist
            count += 1

    # Average distance, normalized by number of features
    avg_distance = total_distance / count if count > 0 else 0
    diversity = avg_distance / n_features

    return diversity


def simple_termination_check(
    iteration: int,
    max_iter: int,
    global_best_fitness: float,
    fitness_threshold: Optional[float] = None,
) -> bool:
    """
    Simple termination check for basic use cases.

    This is a lightweight alternative to TerminationCriteria for simple scenarios.

    Args:
        iteration: Current iteration number
        max_iter: Maximum iterations
        global_best_fitness: Current best fitness
        fitness_threshold: Optional fitness threshold to stop early

    Returns:
        True if should terminate, False otherwise
    """
    # Check max iterations
    if iteration >= max_iter:
        return True

    # Check fitness threshold
    if fitness_threshold is not None:
        if global_best_fitness <= fitness_threshold:
            return True

    return False


def early_stopping_check(
    fitness_history: List[float], patience: int = 10, min_delta: float = 1e-6
) -> bool:
    """
    Check for early stopping based on fitness improvement history.

    Similar to early stopping in neural network training - stops if
    no significant improvement is observed for 'patience' iterations.

    Args:
        fitness_history: List of best fitness values (lower is better)
        patience: Number of iterations to wait for improvement
        min_delta: Minimum change to be considered an improvement

    Returns:
        True if should stop (no improvement), False otherwise
    """
    if len(fitness_history) < patience + 1:
        return False

    # Get the best fitness from 'patience' iterations ago
    best_old = fitness_history[-patience - 1]

    # Check if any recent fitness is significantly better
    recent_fitnesses = fitness_history[-patience:]
    for fitness in recent_fitnesses:
        if best_old - fitness > min_delta:  # Improvement found
            return False

    # No significant improvement in 'patience' iterations
    return True
