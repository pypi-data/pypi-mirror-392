"""
Lab Workflow Reference Functions
=================================

These functions show you the complete code workflow for each RL lab.
When you forget what to do next, just call the flow function for your lab
and it will print out all the code you need to copy and run.

Usage:
------
>>> from matplotlab import rl
>>> rl.flowlab1()  # Shows complete Lab 1 workflow
>>> rl.flowlab2()  # Shows complete Lab 2 workflow
>>> rl.flowlab3()  # Shows complete Lab 3 workflow
>>> rl.flowlab4()  # Shows complete Lab 4 workflow
>>> rl.flowlab5()  # Shows complete Lab 5 workflow
>>> rl.flowlab6()  # Shows complete Lab 6 workflow
>>> rl.flowoel()   # Shows complete OEL workflow

Note: Lab 7 is not available (no notebook found)
"""


def flowlab1():
    """
    Display complete code workflow for Lab 1.
    Note: Lab 1 file is in binary format (.bin), so this is a placeholder.
    """
    print("=" * 80)
    print("RL LAB 1 WORKFLOW")
    print("=" * 80)
    print()
    print("WARNING: Lab 1 file (RI_Lab_1.bin) is in binary format.")
    print("    Unable to extract code workflow.")
    print()
    print("    Please refer to your original Lab 1 notebook or PDF manual.")
    print("=" * 80)


def flowlab2():
    """
    Display complete code workflow for Lab 2 (Grid World MDP).
    Shows: Environment setup, transition probabilities, reward function.
    """
    code = '''
# ============================================================================
# RL LAB 2 WORKFLOW - Grid World MDP
# ============================================================================

# STEP 1: Import libraries
import numpy

# STEP 2: Define grid dimensions and states
rows, cols = 3, 4
states = [(i, j) for i in range(rows) for j in range(cols)]
wall = (1, 2)
goal = (0, 3)
danger = (2, 3)
states.remove(wall)  # wall is not a valid state

# STEP 3: Define actions
actions = ["UP", "DOWN", "LEFT", "RIGHT"]

# STEP 4: Define reward function
def reward(state):
    if state == goal:
        return 1.0
    elif state == danger:
        return -1.0
    else:
        return -0.04

# STEP 5: Define next_state function (movement logic)
def next_state(state, action):
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

# STEP 6: Define transition probabilities (80% intended, 10% slip each side)
def transition_probabilities(state, action):
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

# STEP 7: Set discount factor
gamma = 0.9

# STEP 8: Test transition probabilities
# Example 1: From state (2,0), action = UP
state = (2, 0)
action = "UP"
transitions = transition_probabilities(state, action)
print(f"From state {state}, action={action}:")
for next_s, prob in transitions.items():
    print(f" -> {next_s} with P={prob:.2f}, Reward={reward(next_s)}")

# Example 2: From state (0,2), action = RIGHT
state = (0, 2)
action = "RIGHT"
transitions = transition_probabilities(state, action)
print(f"\\nFrom state {state}, action={action}:")
for next_s, prob in transitions.items():
    print(f" -> {next_s} with P={prob:.2f}, Reward={reward(next_s)}")

# BASIC TASKS:

# Task 1: Print all states, actions, and rewards
print("States:", states)
print("Actions:", actions)
print("Rewards:", reward(goal), reward(danger))

# Task 2: Calculate transition probabilities for state (2,1), action UP
temp_state = (2, 1)
temp_action = "UP"
print(transition_probabilities(temp_state, temp_action))

# Task 3: Calculate transition probabilities for state (0,2), action LEFT
temp_state = (0, 2)
temp_action = "LEFT"
print(transition_probabilities(temp_state, temp_action))

# ============================================================================
# END OF LAB 2 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab3():
    """
    Display complete code workflow for Lab 3 (Monte Carlo Methods).
    Shows: Episode sampling, return computation, value estimation.
    """
    code = '''
# ============================================================================
# RL LAB 3 WORKFLOW - Monte Carlo Methods
# ============================================================================

# STEP 1: Import libraries
import numpy as np
from matplotlib import pyplot as plt

# STEP 2: Define states and rewards
S = ['c1', 'c2', 'c3', 'pass', 'rest', 'tv', 'sleep']
R = np.array([-2, -2, -2, +10, +1, -1, 0])

# STEP 3: Define transition probability matrix
P = np.array([
    [0.0, 0.5, 0.0, 0.0, 0.0, 0.5, 0.0],
    [0.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.2],
    [0.0, 0.0, 0.0, 0.6, 0.4, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    [0.2, 0.4, 0.4, 0.0, 0.0, 0.0, 0.0],
    [0.1, 0.0, 0.0, 0.0, 0.0, 0.9, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
])

# STEP 4: Set discount factor
gamma = 0.5

# STEP 5: Verify probabilities sum to 1
assert(np.all(np.sum(P, axis=1) == 1))

# STEP 6: Define episode sampling function
def sample_episode(P, s=0, log=True):
    print_str = S[s] + ', '
    episode = [s]

    while(S[episode[-1]] != 'sleep'):
        episode.append(np.random.choice(len(P), 1, p=P[episode[-1]])[0])
        print_str += str(S[episode[-1]]) + ', '
    if log:
        print(print_str)
    return np.array(episode)

# STEP 7: Generate sample episodes
print('first sample: ')
episode = sample_episode(P, s=0)
print('\\nsecond sample: ')
episode = sample_episode(P, s=0)
print('\\nthird sample: ')
episode = sample_episode(P, s=0)

# STEP 8: Compute return for one episode
episode = sample_episode(P, s=0)
episode_reward = R[episode]
G_t = 0

for k in range(0, len(episode)):
    G_t += gamma**k * episode_reward[k]
    print("G_t = {:.4f}, gamma^k = {:.4f}".format(G_t, gamma**k))

# STEP 9: Monte Carlo value estimation (2000 episodes)
V = np.zeros(len(P))
num_episodes = 2000

for i in range(num_episodes):
    for s in range(len(P)):
        episode = sample_episode(P, s, log=False)
        episode_reward = R[episode]
        G_t = 0
        for k in range(0, len(episode)):
            G_t += gamma**k * episode_reward[k]
        V[s] += G_t
    if (i+1) % 100 == 0:
        np.set_printoptions(precision=2)
        print(V / (i + 1))

V = V / num_episodes
print(V)

# STEP 10: Analytical solution (Bellman equation)
I = np.identity(len(P))
V = np.linalg.solve(I - gamma * P, R)
print(V)

# STUDENT TASKS:

# Task 1: Change gamma to 0.9 and note the change in V(s)
gamma = 0.9
V = np.zeros(len(P))
num_episodes = 2000

for i in range(num_episodes):
    for s in range(len(P)):
        episode = sample_episode(P, s, log=False)
        episode_reward = R[episode]
        G_t = 0
        for k in range(0, len(episode)):
            G_t += gamma**k * episode_reward[k]
        V[s] += G_t
    if (i+1) % 100 == 0:
        np.set_printoptions(precision=2)
        print(V / (i + 1))

V = V / num_episodes
print(V)

# Analytical solution with gamma=0.9
I = np.identity(len(P))
V = np.linalg.solve(I - gamma * P, R)
print(V)

# Task 2: Increase the reward of 'tv' from -1 to +2 and compare results
R = np.array([-2, -2, -2, +10, +1, +2, 0])

episode = sample_episode(P, s=0)
episode_reward = R[episode]
G_t = 0

for k in range(0, len(episode)):
    G_t += gamma**k * episode_reward[k]
    print("G_t = {:.4f}, gamma^k = {:.4f}".format(G_t, gamma**k))

# ============================================================================
# END OF LAB 3 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab4():
    """
    Display complete code workflow for Lab 4 (Value Iteration & Policy Evaluation).
    Shows: FrozenLake environment, value iteration, policy extraction, visualization.
    """
    code = '''
# ============================================================================
# RL LAB 4 WORKFLOW - Value Iteration & Policy Evaluation
# ============================================================================

# STEP 1: Import libraries
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

# STEP 2: Create FrozenLake environment
env = gym.make('FrozenLake-v1', is_slippery=True, render_mode='ansi')
env.reset()

# STEP 3: Set hyperparameters
gamma = 0.99
theta = 1e-8
V = np.zeros(env.observation_space.n)

# STEP 4: Get transition probabilities
P = env.unwrapped.P

# STEP 5: Examine environment properties
print(f'The environments observation space: {env.observation_space}')
print(f'The environments actions space: {env.action_space}')
print(f'The environments reward range: {env.unwrapped.reward_range}')

# STEP 6: Render initial environment state
print(env.render())

# STEP 7: Value Iteration algorithm
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

# STEP 8: Extract policy from value function
policy = np.zeros((env.observation_space.n, env.action_space.n))
for s in range(env.observation_space.n):
    q_sa = np.zeros(env.action_space.n)
    for a in range(env.action_space.n):
        for prob, next_state, reward, done in P[s][a]:
            q_sa[a] += prob * (reward + gamma * V[next_state])
    best_action = np.argmax(q_sa)
    policy[s][best_action] = 1.0

# STEP 9: Define visualization function
def plot(V, policy, col_ramp=1, dpi=175, draw_vals=False):
    plt.rcParams['figure.dpi'] = dpi
    plt.rcParams.update({'axes.edgecolor': (0.32, 0.36, 0.38)})
    plt.rcParams.update({'font.size': 6 if env.unwrapped.nrow == 8 else 8})
    plt.figure(figsize=(3, 3))

    desc = env.unwrapped.desc
    nrow, ncol = desc.shape
    V_sq = V.reshape((nrow, ncol))

    plt.imshow(V_sq, cmap='cool' if col_ramp else 'gray', alpha=0.7)
    ax = plt.gca()

    arrow_dict = {0: '<-', 1: 'v', 2: '->', 3: '^'}

    for x in range(ncol + 1):
        ax.axvline(x - 0.5, lw=0.5, color='black')
    for y in range(nrow + 1):
        ax.axhline(y - 0.5, lw=0.5, color='black')

    for r in range(nrow):
        for c in range(ncol):
            s = r * ncol + c
            val = V[s]
            tile = desc[r, c].decode('utf-8')
            
            if tile == 'H':
                color = 'red'
            elif tile == 'G':
                color = 'green'
            elif tile == 'S':
                color = 'blue'
            else:
                color = 'black'

            plt.text(c, r, tile, ha='center', va='center', color=color, 
                    fontsize=10, fontweight='bold')

            if draw_vals and tile not in ['H']:
                plt.text(c, r + 0.3, f"{val:.2f}", ha='center', va='center', 
                        color='black', fontsize=6)

            if policy is not None:
                best_action = np.argmax(policy[s])
                plt.text(c, r - 0.25, arrow_dict[best_action], ha='center', 
                        va='center', color='purple', fontsize=12)

    plt.title("FrozenLake: Policy and State Values")
    plt.axis('off')
    plt.show()

# STEP 10: Visualize results
plot(V, policy, draw_vals=True)

# STEP 11: Random Policy Initialization
nS = env.observation_space.n
nA = env.action_space.n
policy = np.ones([nS, nA]) / nA
print("Policy shape:", policy.shape)

# STEP 12: Policy Evaluation function
def policy_evaluation(env, policy, discount_factor=1.0, theta=1e-9, draw=False):
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

# STEP 13: Evaluate the random policy
V_evaluated = policy_evaluation(env, policy, discount_factor=0.99, draw=True)

# ============================================================================
# END OF LAB 4 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab5():
    """
    Display complete code workflow for Lab 5 (Policy Iteration).
    Shows: Policy evaluation, Q-value computation, policy improvement, full iteration.
    """
    code = '''
# ============================================================================
# RL LAB 5 WORKFLOW - Policy Iteration
# ============================================================================

# STEP 1: Import libraries
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

# STEP 2: Create FrozenLake environment
env = gym.make('FrozenLake-v1', is_slippery=True, render_mode='ansi')

# STEP 3: Get environment properties
nS = env.observation_space.n  # Number of states (16 for 4x4)
nA = env.action_space.n        # Number of actions (4: Left, Down, Right, Up)

# STEP 4: Policy Evaluation function
def policy_evaluation(env, policy, gamma=1.0, theta=1e-8):
    V = np.zeros(nS)
    while True:
        delta = 0
        for s in range(nS):
            v_old = V[s]
            v_new = 0
            for a in range(nA):
                action_prob = policy[s][a]
                if action_prob > 0:
                    for prob, next_state, reward, done in env.unwrapped.P[s][a]:
                        v_new += action_prob * prob * (reward + gamma * V[next_state])
            V[s] = v_new
            delta = max(delta, np.abs(v_old - V[s]))
        if delta < theta:
            break
    return V

# STEP 5: Q-value computation function
def q_from_v(env, V, s, gamma=1.0):
    q = np.zeros(nA)
    for a in range(nA):
        for prob, next_state, reward, done in env.unwrapped.P[s][a]:
            q[a] += prob * (reward + gamma * V[next_state])
    return q

# STEP 6: Policy Improvement function
def policy_improvement(env, V, discount_factor=1.0):
    policy = np.zeros([nS, nA])
    for s in range(nS):
        Q = q_from_v(env, V, s, discount_factor)
        best_action = np.argmax(Q)
        policy[s, best_action] = 1.0
    return policy

# STEP 7: Visualization function
def plot(V, policy, title_suffix="Initial Policy", draw_vals=True):
    nrow = env.unwrapped.nrow
    ncol = env.unwrapped.ncol
    arrow_symbols = {0: '<-', 1: 'v', 2: '->', 3: '^'}

    best_actions = np.argmax(policy, axis=1)
    grid = np.reshape(V, (nrow, ncol))

    plt.figure(figsize=(6, 6))
    plt.imshow(grid, cmap='cool', interpolation='none')

    for s in range(nrow * ncol):
        row, col = divmod(s, ncol)

        if draw_vals:
            plt.text(col, row, f'{V[s]:.2f}', ha='center', va='center', 
                    color='black', fontsize=10)
        else:
            plt.text(col, row, arrow_symbols[best_actions[s]], ha='center', 
                    va='center', color='white', fontsize=16)

    plt.title(("Value Function (" + title_suffix + ")") if draw_vals 
              else ("Policy (" + title_suffix + ")"))
    plt.axis('off')
    plt.colorbar(label='State Value')
    plt.show()

# STEP 8: Test Policy Improvement with random values
print("--- Task 3: Policy Improvement on Random Values ---")

V_random = np.random.rand(nS)
initial_policy = np.full([nS, nA], 1/nA)

plot(V_random, initial_policy, "Random V (Before Improvement)", draw_vals=True)
plot(V_random, initial_policy, "Uniform Policy (Before Improvement)", draw_vals=False)

new_policy_greedy = policy_improvement(env, V_random)
V_improved = policy_evaluation(env, new_policy_greedy)

plot(V_improved, new_policy_greedy, "Improved Policy V", draw_vals=True)
plot(V_improved, new_policy_greedy, "Greedy Policy (After Improvement)", draw_vals=False)

# STEP 9: Full Policy Iteration
print("\\n--- Task 4: Policy Iteration to Find Optimal Policy ---")

def policy_iteration(env, gamma=1.0, theta=1e-8):
    policy = np.full([nS, nA], 1/nA)
    iteration_count = 0
    
    while True:
        V = policy_evaluation(env, policy, gamma, theta)
        new_policy = policy_improvement(env, V, gamma)
        policy_stable = np.array_equal(policy, new_policy)
        policy = new_policy
        iteration_count += 1
        
        if policy_stable:
            break
    
    return V, policy, iteration_count

V_optimal, policy_optimal, iterations = policy_iteration(env, gamma=0.9)
print(f"Policy Iteration converged in {iterations} iterations.")

plot(V_optimal, policy_optimal, f"Optimal V (Converged in {iterations} iters)", 
     draw_vals=True)
plot(V_optimal, policy_optimal, f"Optimal Policy (Converged in {iterations} iters)", 
     draw_vals=False)

# ============================================================================
# END OF LAB 5 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab6():
    """
    Display complete code workflow for Lab 6 (Value Iteration - Taxi Environment).
    Shows: Taxi-v3 environment, value iteration, policy extraction, evaluation.
    """
    code = '''
# ============================================================================
# RL LAB 6 WORKFLOW - Value Iteration (Taxi-v3)
# ============================================================================

# STEP 1: Import libraries
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

# STEP 2: Create Taxi environment
env = gym.make('Taxi-v3', render_mode='ansi')

# STEP 3: Value Iteration function
def value_iteration(env, discount_factor=0.99, theta=1e-6, max_iterations=10000):
    nS = env.observation_space.n
    nA = env.action_space.n
    P = env.unwrapped.P
    V = np.zeros(nS)

    for i in range(max_iterations):
        delta = 0
        for s in range(nS):
            q_sa = np.zeros(nA)
            for a in range(nA):
                for prob, next_state, reward, done in P[s][a]:
                    q_sa[a] += prob * (reward + discount_factor * V[next_state])
            new_v = np.max(q_sa)
            delta = max(delta, np.abs(new_v - V[s]))
            V[s] = new_v

        if delta < theta:
            break

    policy = extract_policy_from_v(env, V, discount_factor)
    return V, policy, i + 1

# STEP 4: Extract policy from value function
def extract_policy_from_v(env, V, discount_factor=0.99):
    nS = env.observation_space.n
    nA = env.action_space.n
    P = env.unwrapped.P
    policy = np.zeros((nS, nA))

    for s in range(nS):
        q_sa = np.zeros(nA)
        for a in range(nA):
            for prob, next_state, reward, done in P[s][a]:
                q_sa[a] += prob * (reward + discount_factor * V[next_state])
        best_a = np.argmax(q_sa)
        policy[s] = np.eye(nA)[best_a]

    return policy

# STEP 5: Visualization functions
def plot_values(env, V):
    plt.figure(figsize=(10, 4))
    plt.plot(V)
    plt.title("Value Function for Taxi-v3")
    plt.xlabel("State (0–499)")
    plt.ylabel("Value")
    plt.grid(True)
    plt.show()

def plot_policy(env, policy):
    nS = env.observation_space.n
    actions = np.argmax(policy, axis=1)
    plt.figure(figsize=(10, 4))
    plt.bar(np.arange(nS), actions)
    plt.title("Greedy Policy (Best Action per State)")
    plt.xlabel("State")
    plt.ylabel("Action (0=South, 1=North, 2=East, 3=West, 4=Pickup, 5=Dropoff)")
    plt.show()

# STEP 6: Run value iteration
env = gym.make('Taxi-v3')
gamma = 0.99
V_opt, policy_opt, iterations = value_iteration(env, discount_factor=gamma)
print(f"Converged in {iterations} iterations.")

# STEP 7: Visualize results
plot_values(env, V_opt)
plot_policy(env, policy_opt)

# STEP 8: Policy evaluation function
def evaluate_policy(env, policy, n_episodes=1000):
    success = 0
    for _ in range(n_episodes):
        obs, _ = env.reset()
        done = False
        while not done:
            action = np.argmax(policy[obs])
            obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            if reward > 0:
                success += 1
    return success / n_episodes

# STEP 9: Evaluate policy
rate = evaluate_policy(env, policy_opt)
print(f"Success Rate: {rate * 100:.2f}%")

# TASK 4: Enhanced policy evaluation (success + avg steps)
def evaluate_policy_enhanced(env, policy, n_episodes=1000):
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
            if r == 20:
                wins += 1
                win_steps += steps
                break
        total_steps += steps

    rate = wins / n_episodes
    avg = win_steps / wins if wins else 0
    return rate, avg

# TASK 3: Test different discount factors
discounts = [0.6, 0.9, 0.99]
summary = []

for g in discounts:
    taxi = gym.make('Taxi-v3')
    V_star, pi_star, it = value_iteration(taxi, discount_factor=g)
    win_rate, steps = evaluate_policy_enhanced(taxi, pi_star)
    summary.append((g, it, win_rate, steps))
    print(f"gamma={g:.2f} -> {it} iters | {win_rate:.1%} success | {steps:.1f} avg steps")

# STUDENT TASK 3: Record Delta per iteration and plot
def value_iteration_with_delta(env, gamma=0.99, eps=1e-6):
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
            new_v = np.max(q)
            delta = max(delta, abs(new_v - V[s]))
            V[s] = new_v
        deltas.append(delta)
        if delta < eps:
            break

    pi = extract_policy_from_v(env, V, gamma)
    return V, pi, len(deltas), deltas

# Plot convergence
env = gym.make('Taxi-v3')
_, _, _, dlist = value_iteration_with_delta(env, gamma=0.99)
plt.figure(figsize=(8,4))
plt.plot(dlist, marker='.')
plt.yscale('log')
plt.title('Maximum Delta-V per iteration')
plt.xlabel('Iteration')
plt.ylabel('Delta-V (log)')
plt.grid(True, alpha=0.4)
plt.show()

# ============================================================================
# END OF LAB 6 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab7():
    """
    Display complete code workflow for Lab 7.
    Note: Lab 7 notebook not found in workspace.
    """
    print("=" * 80)
    print("RL LAB 7 WORKFLOW")
    print("=" * 80)
    print()
    print("WARNING: Lab 7 notebook file not found in workspace.")
    print()
    print("    Available labs: 1, 2, 3, 4, 5, 6, OEL")
    print()
    print("    Please check your Lab 7 PDF manual or notebook file.")
    print("=" * 80)


def flowoel():
    """
    Display complete code workflow for OEL (Open Ended Lab).
    Shows: FrozenLake MDP analysis, policy iteration implementation.
    """
    code = '''
# ============================================================================
# RL OEL WORKFLOW - Policy Iteration on FrozenLake
# ============================================================================

# STEP 1: Import libraries
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

# STEP 2: Policy Evaluation function
def policy_evaluation(env, policy, V, gamma=1.0, theta=1e-8):
    state_func_ave = []

    while True:
        delta = 0
        for s in range(env.observation_space.n):
            v = 0
            for a, action_prob in enumerate(policy[s]):
                for prob, next_state, reward, done in P[s][a]:
                    v += action_prob * prob * (reward + gamma * V[next_state])
            delta = max(delta, abs(v - V[s]))
            V[s] = v

        if delta < theta:
            break

        state_func_ave.append(np.mean(V))

    return V, state_func_ave

# STEP 3: Q-value from V function
def q_from_v(env, V, s, gamma=1):
    q = np.zeros(env.action_space.n)
    for a in range(env.action_space.n):
        for prob, next_state, reward, done in P[s][a]:
            q[a] += prob * (reward + gamma * V[next_state])
    return q

# STEP 4: Policy Improvement function
def policy_improvement(env, V, discount_factor=1.0):
    nS = env.observation_space.n
    nA = env.action_space.n
    policy = np.zeros([nS, nA])

    for s in range(nS):
        Q = q_from_v(env, V, s, discount_factor)
        best_action = np.argmax(Q)
        policy[s] = np.eye(nA)[best_action]

    return policy

# STEP 5: Full Policy Iteration function
def policy_iteration(env, gamma=1.0, theta=1e-8):
    nS = env.observation_space.n
    nA = env.action_space.n

    policy = np.ones([nS, nA]) / nA
    V = np.zeros(nS)

    iteration = 0
    policy_stable = False

    while not policy_stable:
        iteration += 1

        V, _ = policy_evaluation(env, policy, V, gamma, theta)

        policy_stable = True
        for s in range(nS):
            old_action = np.argmax(policy[s])

            Q = q_from_v(env, V, s, gamma)
            best_action = np.argmax(Q)

            new_policy_s = np.eye(nA)[best_action]

            if not np.array_equal(policy[s], new_policy_s):
                policy_stable = False
                policy[s] = new_policy_s

    return policy, V, iteration

# STEP 6: Simple plot function
def simple_plot(value_function_list, policy=None):
    total_rows = total_columns = int(np.sqrt(len(value_function_list)))
    value_function_matrix = value_function_list.reshape((total_rows, total_columns))
    figure, axes = plt.subplots()
    colored_axes = axes.matshow(value_function_matrix, cmap='cool')
    figure.colorbar(colored_axes)

    description = env.unwrapped.desc
    arrows = {0: '<-', 1: 'v', 2: '->', 3: '^'}

    for i in range(total_rows):
        for j in range(total_columns):
            state_index = i * total_columns + j
            tile = description[i, j].decode('utf-8')
            text = tile

            if policy is not None:
                best_action = np.argmax(policy[state_index])
                text += '\\n' + arrows[best_action]
                axes.text(j, i, text, ha='center', va='center', color='black')
                axes.text(j, i + 0.3, f"{value_function_list[state_index]:.2f}", 
                         ha='center', va='center', color='black', fontsize=8)

    plt.title("FrozenLake Values")
    plt.show()

# ============================================================================
# TASK 1: ENVIRONMENT SETUP
# ============================================================================

# Initialize FrozenLake environment
env = gym.make('FrozenLake-v1', is_slippery=True, render_mode='ansi')
env.reset()
P = env.unwrapped.P

# Display environment properties
print(f'The environments observation space: {env.observation_space}')
print(f'The environments actions space: {env.action_space}')
print(f'The environments reward range: {env.unwrapped.reward_range}')

# Render environment
print(env.render())

# Print transition probabilities
pprint(P)

# ============================================================================
# TASK 2: POLICY EVALUATION
# ============================================================================

# Initialize a random policy
nS = env.observation_space.n
nA = env.action_space.n
random_policy = np.ones([nS, nA]) / nA
gamma = 1.0

# Evaluate random policy
V = np.zeros(env.observation_space.n)
V_random_evaluated, V_average_list = policy_evaluation(env, random_policy, V, gamma=gamma)

# Plot convergence
plt.plot(V_average_list)
plt.title("Average Value Function per Iteration")
plt.xlabel("Iteration")
plt.ylabel("Average Value Function")
plt.show()

# ============================================================================
# TASK 3: POLICY IMPROVEMENT & ITERATION
# ============================================================================

# Run full policy iteration
optimal_policy, optimal_V, iterations = policy_iteration(env, gamma=0.9, theta=1e-8)
print(f'Convergence occured in {iterations} steps.')
simple_plot(optimal_V, optimal_policy)

# ============================================================================
# TASK 4: EXPERIMENTAL ANALYSIS
# ============================================================================

# Test on non-slippery environment
env_slippery = gym.make('FrozenLake-v1', is_slippery=False, render_mode='ansi')

optimal_policy_slippery, optimal_V_slippery, iterations_slippery = \\
    policy_iteration(env_slippery, gamma=0.9, theta=1e-8)
print(f'Convergence with non-slippery environment occured in {iterations_slippery} steps.')
simple_plot(optimal_V_slippery, optimal_policy_slippery)

# ============================================================================
# END OF OEL WORKFLOW
# ============================================================================
'''
    print(code)
