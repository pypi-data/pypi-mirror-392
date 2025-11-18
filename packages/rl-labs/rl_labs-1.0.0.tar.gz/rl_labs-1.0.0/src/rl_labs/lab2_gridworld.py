import numpy as np

# Grid dimensions from Lab 2
rows, cols = 3, 4

# Define states (excluding wall)
states = [(i, j) for i in range(rows) for j in range(cols)]
wall = (1, 2)
goal = (0, 3)
danger = (2, 3)
states.remove(wall)  # wall is not a valid state

# Define actions
actions = ["UP", "DOWN", "LEFT", "RIGHT"]

def reward(state):
    """
    Lab 2: Reward function for GridWorld
    Returns reward based on state: goal=1.0, danger=-1.0, others=-0.04
    """
    if state == goal:
        return 1.0
    elif state == danger:
        return -1.0
    else:
        return -0.04

def next_state(state, action):
    """
    Lab 2: Deterministic state transition function
    Calculates next state based on action, handles walls and boundaries
    """
    i, j = state
    if action == "UP":
        i = max(i - 1, 0)
    elif action == "DOWN":
        i = min(i + 1, rows - 1)
    elif action == "LEFT":
        j = max(j - 1, 0)
    elif action == "RIGHT":
        j = min(j + 1, cols - 1)
    
    # If move hits wall -> stay in same state
    if (i, j) == wall:
        return state
    return (i, j)

def transition_probabilities(state, action):
    """
    Lab 2: Transition probabilities with 80%-10%-10% slip model
    Returns dictionary of next_state: probability pairs
    """
    if state in [goal, danger]:
        return {state: 1.0}  # Terminal states 100% probability
    
    probs = {}
    intended = next_state(state, action)
    
    # Slips: define left and right turns
    if action == "UP":
        left, right = "LEFT", "RIGHT"
    elif action == "DOWN":
        left, right = "RIGHT", "LEFT"
    elif action == "LEFT":
        left, right = "DOWN", "UP"
    else:  # RIGHT
        left, right = "UP", "DOWN"

    slip_left = next_state(state, left)
    slip_right = next_state(state, right)

    probs[intended] = probs.get(intended, 0) + 0.8
    probs[slip_left] = probs.get(slip_left, 0) + 0.1
    probs[slip_right] = probs.get(slip_right, 0) + 0.1
    
    return probs

def transition_probabilities_mod(state, action):
    """
    Lab 2: Modified transition probabilities with 70%-15%-15% slip model
    Alternative slip probability distribution
    """
    if state in [goal, danger]:
        return {state: 1.0}  # Terminal states 100% probability
    
    probs = {}
    intended = next_state(state, action)
    
    # Slips: define left and right turns
    if action == "UP":
        left, right = "LEFT", "RIGHT"
    elif action == "DOWN":
        left, right = "RIGHT", "LEFT"
    elif action == "LEFT":
        left, right = "DOWN", "UP"
    else:  # RIGHT
        left, right = "UP", "DOWN"

    slip_left = next_state(state, left)
    slip_right = next_state(state, right)

    probs[intended] = probs.get(intended, 0) + 0.7
    probs[slip_left] = probs.get(slip_left, 0) + 0.15
    probs[slip_right] = probs.get(slip_right, 0) + 0.15
    
    return probs