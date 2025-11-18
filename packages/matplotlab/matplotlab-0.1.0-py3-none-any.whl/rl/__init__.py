"""
Reinforcement Learning Module
==============================

Implementations from RL Labs 1-7 and OEL covering:
- Monte Carlo Methods (Lab 3, 7)
- Temporal Difference Learning (Lab 7)
- Policy Evaluation (Lab 4)
- Policy Iteration (Lab 5, OEL1)
- Value Iteration (Lab 6)
- Custom Environments (Lab 1, 2)
- MDP Utilities (Lab 2)
- Visualization Tools (All labs)

Author: Sohail
Source: University RL Coursework 2025
"""

__version__ = "0.1.0"

# Environment utilities
from .environments import (
    create_frozenlake_env,
    random_agent_episode,
    visualize_path,
    GridWorld,
)

# MDP utilities
from .mdp import (
    next_state,
    transition_probabilities,
    reward,
    define_states_actions,
)

# Monte Carlo methods
from .monte_carlo import (
    sample_episode,
    mc_value_estimation_mdp,
    compute_return,
    analytical_solution,
    mc_prediction,
)

# Policy evaluation
from .policy_eval import (
    policy_evaluation,
    bellman_expectation_backup,
)

# Policy iteration
from .policy_iter import (
    q_from_v,
    policy_improvement,
    policy_iteration,
)

# Value iteration
from .value_iter import (
    value_iteration,
    extract_policy_from_v,
    evaluate_policy,
    value_iteration_with_delta,
)

# Temporal difference learning
from .td_learning import (
    td_prediction,
)

# Visualization
from .visualization import (
    plot_episode_rewards,
    plot_grid_policy,
    plot_value_heatmap,
    plot,
    plot_convergence_delta,
    plot_values,
    plot_policy,
    simple_plot,
    plot_convergence,
    compare_mc_td_convergence,
)

# Utility functions
from ._utils import query

# Import code inspector and wrap all functions with .show() capability
from ._code_inspector import ShowableFunction


def list_functions():
    """
    Display all available RL functions organized by category.
    
    After seeing the list, use help(rl.function_name) to see parameters.
    
    Example:
    --------
    >>> import sohail_mlsuite.rl as rl
    >>> rl.list_functions()  # See all functions
    >>> help(rl.policy_iteration)  # See parameters for specific function
    """
    categories = {
        "ENVIRONMENTS (3 functions)": [
            "create_frozenlake_env",
            "random_agent_episode", 
            "visualize_path",
        ],
        "MDP UTILITIES (4 functions)": [
            "define_states_actions",
            "next_state",
            "transition_probabilities",
            "reward",
        ],
        "MONTE CARLO (5 functions)": [
            "sample_episode",
            "mc_value_estimation_mdp",
            "compute_return",
            "analytical_solution",
            "mc_prediction",
        ],
        "POLICY EVALUATION (2 functions)": [
            "policy_evaluation",
            "bellman_expectation_backup",
        ],
        "POLICY ITERATION (3 functions)": [
            "q_from_v",
            "policy_improvement",
            "policy_iteration",
        ],
        "VALUE ITERATION (4 functions)": [
            "value_iteration",
            "extract_policy_from_v",
            "evaluate_policy",
            "value_iteration_with_delta",
        ],
        "TD LEARNING (1 function)": [
            "td_prediction",
        ],
        "VISUALIZATION (10 functions)": [
            "plot_episode_rewards",
            "plot_grid_policy",
            "plot_value_heatmap",
            "plot",
            "plot_convergence_delta",
            "plot_values",
            "plot_policy",
            "simple_plot",
            "plot_convergence",
            "compare_mc_td_convergence",
        ],
        "UTILITY (1 function)": [
            "query",
        ],
    }
    
    print("=" * 70)
    print("MATPLOTLAB RL MODULE - ALL FUNCTIONS")
    print("=" * 70)
    print()
    
    total = 0
    for category, funcs in categories.items():
        print(f"{category}")
        print("-" * 70)
        for func in funcs:
            print(f"  - {func}")
            total += 1
        print()
    
    print("=" * 70)
    print(f"TOTAL: {total} functions available")
    print()
    print("HOW TO USE:")
    print("  1. Choose a function from above")
    print("  2. See parameters: help(rl.function_name)")
    print("  3. See code: rl.function_name.show()")
    print("=" * 70)


def show_lib():
    """
    Display all required library imports for RL labs.
    
    Shows the complete list of imports needed across all 7 RL labs
    with correct syntax. Use this when you forget import statements.
    
    Example:
    --------
    >>> import sohail_mlsuite.rl as rl
    >>> rl.show_lib()  # See all required imports
    """
    print("=" * 70)
    print("REQUIRED LIBRARIES FOR RL MODULE (All 7 Labs)")
    print("=" * 70)
    print()
    
    print("# Core Libraries")
    print("-" * 70)
    print("import numpy as np")
    print("import matplotlib.pyplot as plt")
    print()
    
    print("# Gymnasium (OpenAI Gym)")
    print("-" * 70)
    print("import gymnasium as gym")
    print()
    
    print("# Python Standard Library")
    print("-" * 70)
    print("from pprint import pprint")
    print()
    
    print("=" * 70)
    print("INSTALLATION COMMANDS")
    print("=" * 70)
    print()
    print("pip install numpy matplotlib gymnasium pygame")
    print()
    print("=" * 70)
    print()
    print("NOTES:")
    print("  - numpy: Array operations and mathematical computations")
    print("  - matplotlib: Plotting and visualization")
    print("  - gymnasium: RL environments (FrozenLake, Taxi, etc.)")
    print("  - pygame: Required for gymnasium rendering")
    print("  - pprint: Pretty printing for debugging")
    print("=" * 70)


# Wrap all imported functions to add .show() method
_functions_to_wrap = [
    # Environments
    create_frozenlake_env,
    random_agent_episode,
    visualize_path,
    # MDP
    next_state,
    transition_probabilities,
    reward,
    define_states_actions,
    # Monte Carlo
    sample_episode,
    mc_value_estimation_mdp,
    compute_return,
    analytical_solution,
    mc_prediction,
    # Policy Evaluation
    policy_evaluation,
    bellman_expectation_backup,
    # Policy Iteration
    q_from_v,
    policy_improvement,
    policy_iteration,
    # Value Iteration
    value_iteration,
    extract_policy_from_v,
    evaluate_policy,
    value_iteration_with_delta,
    # TD Learning
    td_prediction,
    # Visualization
    plot_episode_rewards,
    plot_grid_policy,
    plot_value_heatmap,
    plot,
    plot_convergence_delta,
    plot_values,
    plot_policy,
    simple_plot,
    plot_convergence,
    compare_mc_td_convergence,
]

# Apply ShowableFunction wrapper to all functions
for func in _functions_to_wrap:
    wrapped = ShowableFunction(func)
    globals()[func.__name__] = wrapped

__all__ = [
    # Environments
    "create_frozenlake_env",
    "random_agent_episode",
    "visualize_path",
    "GridWorld",
    "define_states_actions",
    # MDP
    "next_state",
    "transition_probabilities",
    "reward",
    # Monte Carlo
    "sample_episode",
    "mc_value_estimation_mdp",
    "compute_return",
    "analytical_solution",
    "mc_prediction",
    # Policy Evaluation
    "policy_evaluation",
    "bellman_expectation_backup",
    # Policy Iteration
    "q_from_v",
    "policy_improvement",
    "policy_iteration",
    # Value Iteration
    "value_iteration",
    "extract_policy_from_v",
    "evaluate_policy",
    "value_iteration_with_delta",
    # TD Learning
    "td_prediction",
    # Visualization
    "plot_episode_rewards",
    "plot_grid_policy",
    "plot_value_heatmap",
    "plot",
    "plot_convergence_delta",
    "plot_values",
    "plot_policy",
    "simple_plot",
    "plot_convergence",
    "compare_mc_td_convergence",
    # Utility
    "query",
    "list_functions",
    "show_lib",
]
