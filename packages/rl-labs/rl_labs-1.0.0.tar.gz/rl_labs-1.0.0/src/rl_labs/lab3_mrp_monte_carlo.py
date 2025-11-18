import numpy as np
import matplotlib.pyplot as plt

# Lab 3: MRP and Monte Carlo Estimation
S = ['c1', 'c2', 'c3', 'pass', 'rest', 'tv', 'sleep']
R = np.array([-2, -2, -2, +10, +1, -1, 0])
P = np.array([
    [0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0],
    [0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.2],
    [0.0, 0.0, 0.0, 0.6, 0.4, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    [0.2, 0.4, 0.4, 0.0, 0.0, 0.0, 0.0],
    [0.1, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
])

def sample_episode(P, s=0, log=True):
    """
    Lab 3: Sample a complete episode from the MRP
    Generates state sequence until terminal state 'sleep' is reached
    """
    print_str = S[s] + ','
    episode = [s]
    while(S[episode[-1]] != 'sleep'):
        episode.append(np.random.choice(len(P), 1, p=P[episode[-1]])[0])
        print_str += str(S[episode[-1]]) + ','
    if log:
        print(print_str)
    return np.array(episode)

def monte_carlo_estimation(P, R, gamma=0.5, num_episodes=2000):
    """
    Lab 3: Monte Carlo estimation of state values
    Estimates V(s) by averaging returns from sampled episodes
    """
    V = np.zeros(len(P))
    
    for i in range(num_episodes):
        for s in range(len(P)):
            episode = sample_episode(P, s, log=False)
            episode_reward = R[episode]
            G_t = 0
            for k in range(0, len(episode)):
                G_t += gamma**k * episode_reward[k]
            V[s] += G_t
            
        if (i+1) % 200 == 0:
            np.set_printoptions(precision=2)
            print(V / (i + 1))
            
    V = V/num_episodes
    return V

def exact_value_calculation(P, R, gamma=0.5):
    """
    Lab 3: Exact value calculation using linear algebra
    Solves V = R + gamma * P * V directly
    """
    I = np.identity(len(P))
    V = np.linalg.solve(I - gamma * P, R)
    return V

def plot_monte_carlo_values(P, R, gamma=0.5, num_episodes=2000):
    """
    Lab 3: Plot Monte Carlo value estimates as bar chart
    Visualizes estimated values for each state
    """
    V = monte_carlo_estimation(P, R, gamma, num_episodes)
    
    plt.figure(figsize=(10, 6))
    plt.bar(S, V)
    plt.xlabel('State')
    plt.ylabel('Estimated Value')
    plt.title('Monte Carlo Value Estimates')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    return V