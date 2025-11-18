import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def value_iteration(env, discount_factor=0.99, theta=1e-6):
    """
    Lab 6: Value iteration algorithm
    Directly computes optimal value function using Bellman optimality equation
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    V = np.zeros(nS)
    P = env.unwrapped.P
    
    while True:
        delta = 0
        for s in range(nS):
            v = V[s]
            q_sa = []
            for a in range(nA):
                q = 0
                for prob, next_state, reward, done in P[s][a]:
                    q += prob * (reward + discount_factor * V[next_state])
                q_sa.append(q)
            V[s] = max(q_sa)
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            break
            
    return V

def evaluate_policy(env, policy, n_episodes=1000):
    """
    Lab 6: Evaluate policy performance
    Measures success rate and average steps per successful episode
    """
    wins = 0
    total_steps = 0
    win_steps = 0

    for _ in range(n_episodes):
        s, _ = env.reset()
        steps = 0
        finished = False
        while not finished:
            a = np.argmax(policy[s])
            s, r, term, trunc, _ = env.step(a)
            steps += 1
            finished = term or trunc
            if r == 20:  # Taxi success reward
                wins += 1
                win_steps += steps
                break
        total_steps += steps

    rate = wins / n_episodes
    avg = win_steps / wins if wins else 0
    return rate, avg

def value_iteration_with_delta(env, gamma=0.99, eps=1e-6):
    """
    Lab 6: Value iteration with delta tracking
    Records maximum value change per iteration for convergence analysis
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    P = env.unwrapped.P
    V = np.zeros(nS)
    deltas = []
    
    for _ in range(10000):
        delta = 0
        for s in range(nS):
            q = np.zeros(nA)
            for a in range(nA):
                for pr, ns, rw, _ in P[s][a]:
                    q[a] += pr * (rw + gamma * V[ns])
            new_V = np.max(q)
            delta = max(delta, abs(new_V - V[s]))
            V[s] = new_V
        deltas.append(delta)
        if delta < eps:
            break
            
    pi = extract_policy_from_v(env, V, gamma)
    return V, pi, len(deltas), deltas

def extract_policy_from_v(env, V, gamma):
    """
    Lab 6: Extract policy from value function
    Creates greedy policy based on optimal value function
    """
    policy = np.zeros([env.observation_space.n, env.action_space.n])
    for s in range(env.observation_space.n):
        Q = q_from_v(env, V, s, gamma)
        best_action = np.argmax(Q)
        policy[s, best_action] = 1.0
    return policy

class ToughTaxi(gym.Wrapper):
    """
    Lab 6: Modified Taxi environment with harsher penalties
    Demonstrates effect of reward structure on learning
    """
    def step(self, action):
        obs, rew, done, trunc, info = self.env.step(action)
        if rew == -1:  # time penalty
            rew = -2   # harsher time penalty
        if rew == -10:  # illegal penalty
            rew = -30   # harsher illegal penalty
        return obs, rew, done, trunc, info