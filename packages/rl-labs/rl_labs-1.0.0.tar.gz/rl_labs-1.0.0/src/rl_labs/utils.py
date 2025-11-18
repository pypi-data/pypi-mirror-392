import numpy as np
import matplotlib.pyplot as plt

def plot(V, policy, discount_factor=1.0, draw_vals=True):
    """
    Utility function: Plot value function or policy
    Can display either numerical values or policy arrows
    """
    nrow = 4  # Default for FrozenLake
    ncol = 4
    nA = 4
    arrow_symbols = {0: '←', 1: '↓', 2: '→', 3: '↑'}
    grid = np.reshape(V, (nrow, ncol))
    
    plt.figure(figsize=(6, 6))
    plt.imshow(grid, cmap='cool', interpolation='none')
    
    for s in range(nrow * ncol):
        row, col = divmod(s, ncol)
        best_action = np.argmax(policy[s])
        
        if draw_vals:
            plt.text(col, row, f'{V[s]:.2f}', ha='center', va='center', color='white', fontsize=10)
        else:
            plt.text(col, row, arrow_symbols[best_action], ha='center', va='center', color='white', fontsize=14)

    plt.title("Value Function" if draw_vals else "Policy")
    plt.axis('off')
    plt.show()