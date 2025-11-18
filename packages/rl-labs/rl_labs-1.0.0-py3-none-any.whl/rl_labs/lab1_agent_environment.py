import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def explore_environment():
    """
    Lab 1: Explore FrozenLake environment properties
    Shows initial state, action space, observation space
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)  # Deterministic environment
    state = env.reset()
    print("Initial State:", state)
    print("Action Space:", env.action_space)
    print("Observation Space:", env.observation_space)
    return env, state

def basic_interaction_loop():
    """
    Lab 1: Implement basic agent-environment interaction loop
    Runs multiple episodes with random actions and tracks rewards
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)
    num_episodes = 100
    prime_run = []
    
    for episode in range(num_episodes):
        state, info = env.reset()
        terminated = False
        truncated = False
        step_count = 0
        total_reward = 0
        
        while not (terminated or truncated):
            action = env.action_space.sample()  # random action
            next_state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            print(f"Step {step_count}: State={state}, Action={action}, Reward={reward}, NextState={next_state}")
            state = next_state
            step_count += 1
            
        print(f"Episode {episode+1} ended with total reward: {total_reward}\n")
        if total_reward == 1:
            prime_run.append(episode)
            
    print(f"Successful Runs: {prime_run}")
    return prime_run

def visualize_path(path, size=4):
    """
    Lab 1: Visualize agent's path through the environment
    Creates a grid showing the sequence of states visited
    """
    grid = np.full((size, size), '-')
    for step, state in enumerate(path):
        row, col = divmod(state, size)
        grid[row, col] = str(step)
    print(grid)
    return grid

def track_cumulative_rewards():
    """
    Lab 1: Track and plot cumulative rewards across episodes
    Shows performance of random policy over time
    """
    env = gym.make('FrozenLake-v1', is_slippery=False)
    rewards = []
    
    for episode in range(10):
        state, info = env.reset()
        terminated = False
        truncated = False
        total_reward = 0
        
        while not (terminated or truncated):
            action = env.action_space.sample()
            state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
        rewards.append(total_reward)

    plt.plot(rewards)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("Random Policy Reward per Episode")
    plt.show()
    return rewards