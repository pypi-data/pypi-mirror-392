import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def mc_prediction(env, policy, episodes=1000, gamma=0.99):
    """
    Lab 7: Monte Carlo prediction for value function estimation
    Estimates V(s) by averaging returns from complete episodes
    """
    V = np.zeros(env.observation_space.n)
    returns = {s: [] for s in range(env.observation_space.n)}
    V_track = []

    for ep in range(episodes):
        episode = []
        state, _ = env.reset()
        done = False

        while not done:
            action = policy[state]
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            episode.append((state, reward))
            state = next_state
            
        G = 0
        visited_states = set()
        for s, r in reversed(episode):
            G = gamma * G + r
            if s not in visited_states:
                returns[s].append(G)
                V[s] = np.mean(returns[s])
                visited_states.add(s)
        V_track.append(V.copy())
        
    return V, V_track

def td_prediction(env, policy, episodes=1000, alpha=0.1, gamma=0.99):
    """
    Lab 7: Temporal Difference (TD(0)) prediction
    Updates value estimates incrementally after each step using bootstrapping
    """
    V = np.zeros(env.observation_space.n)
    V_track = []
    
    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        
        while not done:
            action = policy[state]
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            V[state] = V[state] + alpha * (reward + gamma * V[next_state] - V[state])
            state = next_state
            
        V_track.append(V.copy())
        
    return V, V_track

def plot_convergence(V_track, title):
    """
    Lab 7: Plot value function convergence over episodes
    Shows how value estimates evolve during learning
    """
    plt.figure(figsize=(10, 6))
    for s in range(len(V_track[0])):
        values = [v[s] for v in V_track]
        plt.plot(values, label=f"state {s}")
    plt.title(title)
    plt.xlabel("Episodes")
    plt.ylabel("Value Estimate V(s)")
    plt.legend()
    plt.grid(True)
    plt.show()

def mc_prediction_with_rewards(env, policy, episodes=10000, gamma=0.99):
    """
    Lab 7: Monte Carlo prediction with reward tracking
    Extends MC prediction to also track episode rewards
    """
    V = np.zeros(env.observation_space.n)
    returns = {s: [] for s in range(env.observation_space.n)}
    V_track = []
    rewards = []

    for ep in range(episodes):
        episode = []
        state, _ = env.reset()
        done = False
        total_reward = 0

        while not done:
            action = policy[state]
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            episode.append((state, reward))
            total_reward += reward
            state = next_state

        rewards.append(total_reward)

        G = 0
        visited = set()
        for s, r in reversed(episode):
            G = gamma * G + r
            if s not in visited:
                returns[s].append(G)
                V[s] = np.mean(returns[s])
                visited.add(s)
        V_track.append(V.copy())

    return V, V_track, rewards

def td_prediction_with_rewards(env, policy, episodes=10000, alpha=0.1, gamma=0.99):
    """
    Lab 7: TD prediction with reward tracking
    Extends TD prediction to also track episode rewards
    """
    V = np.zeros(env.observation_space.n)
    V_track = []
    rewards = []

    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        total_reward = 0

        while not done:
            action = policy[state]
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            total_reward += reward
            V[state] += alpha * (reward + gamma * V[next_state] - V[state])
            state = next_state

        V_track.append(V.copy())
        rewards.append(total_reward)

    return V, V_track, rewards

def plot_average_rewards(rewards_mc, rewards_td, window=100):
    """
    Lab 7: Plot average rewards over time for MC vs TD
    Compares learning performance using moving average
    """
    avg_mc = np.convolve(rewards_mc, np.ones(window)/window, mode='valid')
    avg_td = np.convolve(rewards_td, np.ones(window)/window, mode='valid')

    plt.figure(figsize=(8, 5))
    plt.plot(avg_mc, label="Monte Carlo")
    plt.plot(avg_td, label="TD(0)")
    plt.title("Average Episode Reward Over Time")
    plt.xlabel("Episodes")
    plt.ylabel("Average Reward")
    plt.legend()
    plt.grid(True)
    plt.show()

def td_lambda(env, policy, episodes=5000, alpha=0.1, gamma=0.99, lam=0.9):
    """
    Lab 7: TD(λ) algorithm with eligibility traces
    Combines TD and MC approaches using trace decay parameter λ
    """
    V = np.zeros(env.observation_space.n)
    V_track = []
    
    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        E = np.zeros(env.observation_space.n)  # eligibility traces

        while not done:
            action = policy[state]
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            td_error = reward + gamma * V[next_state] - V[state]
            E[state] += 1  # accumulate trace

            # Update all state values with decay
            V += alpha * td_error * E
            E *= gamma * lam

            state = next_state

        V_track.append(V.copy())
        
    return V, V_track