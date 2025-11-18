import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def q_from_v(env, V, s, gamma=1):
    """
    Lab 5: Compute Q-values from value function
    Calculates expected return for each action in a given state
    """
    q = np.zeros(env.unwrapped.action_space.n)  # Access unwrapped env
    for a in range(env.unwrapped.action_space.n):  # Access unwrapped env
        for prob, next_state, reward, done in env.unwrapped.P[s][a]:
            q[a] += prob * (reward + gamma * V[next_state])
    return q

def policy_improvement(env, V, discount_factor=1.0):
    """
    Lab 5: Policy improvement algorithm
    Creates improved policy by selecting greedy actions based on value function
    """
    nS = env.observation_space.n
    nA = env.unwrapped.action_space.n  # Access unwrapped env
    policy = np.zeros([nS, nA])
    
    for s in range(nS):
        Q = q_from_v(env, V, s, discount_factor)
        best_action = np.argmax(Q)
        policy[s] = np.eye(nA)[best_action]
        
    return policy

class SimpleMDP:
    """
    Lab 5: Simple 3-state MDP for manual policy improvement demonstration
    """
    def __init__(self):
        self.n_states = 3
        self.n_actions = 2
        self.states = ['A', 'B', 'C']
        self.actions = ['Left', 'Right']

    def get_transitions(self, state, action):
        """
        Lab 5: Get transition probabilities for state-action pair
        Returns list of (probability, next_state, reward) tuples
        """
        transitions = {
            ('A', 'Left'): [(1.0, 'A', 0)],
            ('A', 'Right'): [(1.0, 'B', 1)],
            ('B', 'Left'): [(1.0, 'A', 0)],
            ('B', 'Right'): [(1.0, 'C', 5)],
            ('C', 'Left'): [(1.0, 'B', 0)],
            ('C', 'Right'): [(1.0, 'C', 10)],
        }
        return transitions.get((state, action), [])

def simple_policy_improvement(mdp, V, gamma=0.9):
    """
    Lab 5: Simple policy improvement for demonstration MDP
    Shows manual policy improvement process step by step
    """
    old_policy = {s: 'Right' for s in mdp.states}
    new_policy = {}

    print("\nPolicy Improvement Process:")
    for s in mdp.states:
        s_idx = mdp.states.index(s)
        Q_values = {}

        for a in mdp.actions:
            Q = 0
            for prob, next_s, reward in mdp.get_transitions(s, a):
                next_idx = mdp.states.index(next_s)
                Q += prob * (reward + gamma * V[next_idx])
            Q_values[a] = Q

        best_action = max(Q_values, key=Q_values.get)
        new_policy[s] = best_action

        print(f" State {s}: Q(Left)={Q_values['Left']:.2f}, "
              f"Q(Right)={Q_values['Right']:.2f} → Best: {best_action}")

    print(f"\nOld Policy: {old_policy}")
    print(f"New Policy: {new_policy}")
    return new_policy

def policy_iteration(env, gamma=0.99, theta=1e-8):
    """
    Lab 5: Complete policy iteration algorithm
    Alternates between policy evaluation and improvement until convergence
    """
    nS = env.observation_space.n
    nA = env.unwrapped.action_space.n  # Access unwrapped env

    policy = np.ones([nS, nA]) / nA

    iteration_count = 0
    evaluation_iterations = []
    
    print("\nRunning Policy Iteration...")
    while True:
        iteration_count += 1

        V, eval_iters = policy_evaluation(env, policy, gamma, theta)
        evaluation_iterations.append(eval_iters)

        policy_stable = True
        for s in range(nS):
            old_action = np.argmax(policy[s])
            Q = q_from_v(env, V, s, gamma)
            best_action = np.argmax(Q)

            if old_action != best_action:
                policy_stable = False

            policy[s] = np.eye(nA)[best_action]

        print(f" Iteration {iteration_count}: Policy Evaluation took {eval_iters} iterations")

        if policy_stable:
            print(f"\nPolicy converged after {iteration_count} iterations!")
            break

    return policy, V, iteration_count, evaluation_iterations