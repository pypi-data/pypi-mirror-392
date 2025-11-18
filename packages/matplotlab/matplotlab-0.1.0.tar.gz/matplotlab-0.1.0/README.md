# Sohail ML Suite

A comprehensive Machine Learning library containing implementations from university coursework covering:
- **Reinforcement Learning (RL)** - Monte Carlo, TD Learning, Policy/Value Iteration
- **Artificial Neural Networks (ANN)** - Deep Learning implementations
- **Speech Processing (SP)** - Audio signal processing and analysis

## Installation

### Option 1: Install Only What You Need (Recommended)

```bash
# For Reinforcement Learning only (installs numpy, matplotlib, gymnasium)
pip install -e .[rl]

# For Artificial Neural Networks only (installs numpy, matplotlib, + ANN deps)
pip install -e .[ann]

# For Speech Processing only (installs numpy, matplotlib, + Speech deps)
pip install -e .[speech]

# Install everything (all modules)
pip install -e .[all]
```

### Option 2: Minimal Installation (Only numpy)

```bash
# Just the base package with numpy
pip install -e .
```

## Quick Start

### Reinforcement Learning
```python
from sohail_mlsuite.rl import policy_iteration
import gymnasium as gym

env = gym.make('FrozenLake-v1')
policy, V, iterations = policy_iteration(env, gamma=0.9)
print(f"Converged in {iterations} iterations")
```

### Artificial Neural Networks
```python
# Coming soon
```

### Speech Processing
```python
# Coming soon
```

## Modules

### 1. Reinforcement Learning (`rl`)
- **Environments**: GridWorld, FrozenLake, Taxi
- **Algorithms**: Monte Carlo, TD(0), Policy Iteration, Value Iteration
- **Visualization**: Convergence plots, policy visualization

### 2. Artificial Neural Networks (`ann`)
- Coming soon

### 3. Speech Processing (`speech`)
- Coming soon

## Requirements

- Python >= 3.7
- NumPy >= 1.21.0
- Matplotlib >= 3.4.0
- Gymnasium >= 0.28.0 (for RL module)

## License

MIT License - Educational purposes

## Author

Sohail - University Coursework 2025
