"""
BinaryCEO - Binary Cosmic Evolution Algorithm

A binary version of the Cosmic Evolution Algorithm (CEO) for optimization problems.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# --- Import in a safe order ---

# 3. Import fitness functions, which are self-contained
from .fitness import classification_fitness, multi_objective_fitness

# 2. Import initialization, which depends on solution
from .initialization import (
    create_sparse_binary_vector,
    initialize_from_custom_positions,
    initialize_population,
)

# 6. Import the main optimizer function
from .optimizer import run_binary_ceo
from .partitioning import partition_stellar_systems

# 4. Import position update functions
from .position_update import local_search, update_all_positions

# 1. Import the solution class first, as everything depends on it
from .solution import CelestialBody

# 5. Import termination functions
from .termination import (
    TerminationCriteria,
    calculate_population_diversity,
    early_stopping_check,
    simple_termination_check,
)

# --- Define what is public ---
__all__ = [
    "__version__",
    # from solution.py
    "CelestialBody",
    # from initialization.py
    "initialize_population",
    "initialize_from_custom_positions",
    "create_sparse_binary_vector",
    # from fitness.py
    "classification_fitness",
    "multi_objective_fitness",
    # from partitioning.py
    "partition_stellar_systems",
    # from position_update.py
    "update_all_positions",
    "local_search",
    # from termination.py
    "TerminationCriteria",
    "calculate_population_diversity",
    "simple_termination_check",
    "early_stopping_check",
    # from optimizer.py
    "run_binary_ceo",
]
