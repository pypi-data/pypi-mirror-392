"""
Reinforcement Learning Labs Library

A comprehensive collection of RL implementations from Labs 1-7.
Includes agent-environment interactions, MRP, Monte Carlo methods,
policy evaluation/improvement, value iteration, and TD learning.
"""

__version__ = "1.0.0"
__author__ = "Sameer Rizwan"

from .lab1_agent_environment import *
from .lab2_gridworld import *
from .lab3_mrp_monte_carlo import *
from .lab4_policy_evaluation import *
from .lab5_policy_improvement import *
from .lab6_value_iteration import *
from .lab7_td_learning import *
from .utils import *

__all__ = [
    # Lab 1
    "explore_environment", "basic_interaction_loop", "visualize_path", "track_cumulative_rewards",
    # Lab 2  
    "GridWorld", "reward", "next_state", "transition_probabilities", "transition_probabilities_mod",
    # Lab 3
    "sample_episode", "monte_carlo_estimation", "exact_value_calculation",
    # Lab 4
    "value_iteration_loop", "derive_optimal_policy", "plot_policy_values", "policy_evaluation",
    # Lab 5
    "q_from_v", "policy_improvement", "policy_iteration", "SimpleMDP", "simple_policy_improvement",
    # Lab 6
    "value_iteration", "evaluate_policy", "value_iteration_with_delta", "ToughTaxi",
    # Lab 7
    "mc_prediction", "td_prediction", "plot_convergence", "mc_prediction_with_rewards",
    "td_prediction_with_rewards", "plot_average_rewards", "td_lambda"
]