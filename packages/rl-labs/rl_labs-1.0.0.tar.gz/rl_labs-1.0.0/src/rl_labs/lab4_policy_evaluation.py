import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def value_iteration_loop(env, gamma=0.99, theta=1e-8):
    """
    Lab 4: Value iteration algorithm for FrozenLake
    Iteratively updates state values using Bellman optimality equation
    """
    V = np.zeros(env.observation_space.n)
    P = env.unwrapped.P
    
    while True:
        delta = 0
        for s in range(env.observation_space.n):
            v = V[s]
            q_sa = []
            for a in range(env.action_space.n):
                q = 0
                for prob, next_state, reward, done in P[s][a]:
                    q += prob * (reward + gamma * V[next_state])
                q_sa.append(q)
            V[s] = max(q_sa)
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            break
    return V

def derive_optimal_policy(env, V, gamma=0.99):
    """
    Lab 4: Derive optimal policy from value function
    Creates deterministic policy by selecting best action at each state
    """
    policy = np.zeros((env.observation_space.n, env.action_space.n))
    P = env.unwrapped.P
    
    for s in range(env.observation_space.n):
        q_sa = np.zeros(env.action_space.n)
        for a in range(env.action_space.n):
            for prob, next_state, reward, done in P[s][a]:
                q_sa[a] += prob * (reward + gamma * V[next_state])
        best_action = np.argmax(q_sa)
        policy[s][best_action] = 1.0
        
    return policy

def plot_policy_values(V, policy, env, col_ramp=1, dpi=175, draw_vals=False):
    """
    Lab 4: Visualize policy and state values for FrozenLake
    Shows grid with state values, policy arrows, and special tiles
    """
    plt.rcParams['figure.dpi'] = dpi
    plt.rcParams.update({'axes.edgecolor': (0.32, 0.36, 0.38)})
    plt.rcParams.update({'font.size': 6 if env.unwrapped.nrow == 8 else 8})
    plt.figure(figsize=(3, 3))

    # Use environment layout (map)
    desc = env.unwrapped.desc
    nrow, ncol = desc.shape
    V_sq = V.reshape((nrow, ncol))

    # Set up the plot
    plt.imshow(V_sq, cmap='cool' if col_ramp else 'gray', alpha=0.7)
    ax = plt.gca()

    # Define direction arrows
    arrow_dict = {
        0: '←',  # LEFT
        1: '↓',  # DOWN
        2: '→',  # RIGHT
        3: '↑'   # UP
    }

    # Draw grid lines
    for x in range(ncol + 1):
        ax.axvline(x - 0.5, lw=0.5, color='black')
    for y in range(nrow + 1):
        ax.axhline(y - 0.5, lw=0.5, color='black')

    # Fill each grid cell with value, symbol, and arrow
    for r in range(nrow):
        for c in range(ncol):
            s = r * ncol + c
            val = V[s]

            # Tile text (S, F, H, G)
            tile = desc[r, c].decode('utf-8')
            if tile == 'H':
                color = 'red'
            elif tile == 'G':
                color = 'green'
            elif tile == 'S':
                color = 'blue'
            else:
                color = 'black'

            # Draw tile letter
            plt.text(c, r, tile, ha='center', va='center', color=color, fontsize=10, fontweight='bold')

            # Draw state value
            if draw_vals and tile not in ['H']:
                plt.text(c, r + 0.3, f"{val:.2f}", ha='center', va='center', color='black', fontsize=6)

            # Draw arrow for best action
            if policy is not None:
                best_action = np.argmax(policy[s])
                plt.text(c, r - 0.25, arrow_dict[best_action], ha='center', va='center', color='purple', fontsize=12)

    plt.title("FrozenLake: Policy and State Values")
    plt.axis('off')
    plt.show()

def policy_evaluation(env, policy, discount_factor=1.0, theta=1e-9, draw=False):
    """
    Lab 4: Policy evaluation using Bellman expectation equation
    Computes value function for a given policy
    """
    nS = env.observation_space.n
    nA = env.action_space.n
    V = np.zeros(nS)
    P = env.unwrapped.P

    while True:
        delta = 0
        for s in range(nS):
            v = 0
            for a, action_prob in enumerate(policy[s]):
                for prob, next_state, reward, done in P[s][a]:
                    v += action_prob * prob * (reward + discount_factor * V[next_state])
            delta = max(delta, abs(V[s] - v))
            V[s] = v
        if delta < theta:
            break

    if draw:
        print("Value function after policy evaluation:")
        print(V.reshape(int(np.sqrt(nS)), int(np.sqrt(nS))))
    return V