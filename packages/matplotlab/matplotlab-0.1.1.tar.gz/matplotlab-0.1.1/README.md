# Matplotlab

Extended plotting and machine learning utilities library for educational purposes.

A comprehensive Python library providing:
- **Reinforcement Learning (RL)** - Monte Carlo, TD Learning, Policy/Value Iteration, Dynamic Programming
- **Artificial Neural Networks (ANN)** - Deep Learning implementations with PyTorch and TensorFlow
- **Visualization Tools** - Enhanced plotting capabilities for ML workflows

## Installation

```bash
# Install from PyPI
pip install matplotlab

# Or install from source
git clone https://github.com/Sohail-Creates/matplotlab.git
cd matplotlab
pip install -e .
```

## Quick Start

### Reinforcement Learning
```python
from matplotlab import rl

# Create environment and find optimal policy
env = rl.create_frozenlake_env()
policy, V, iterations = rl.policy_iteration(env, gamma=0.99)
print(f"Converged in {iterations} iterations")

# Visualize results
rl.plot_value_heatmap(V)
rl.plot_grid_policy(policy)
```

### Artificial Neural Networks
```python
from matplotlab import ann
import torch.nn as nn

# Create simple MLP model
model = ann.create_mlp_model(input_size=10, hidden_sizes=[16, 8], output_size=1)

# Or create CNN
cnn_model = ann.create_fashion_cnn()

# Training is straightforward
for epoch in range(50):
    y_pred = model(X_train)
    loss = loss_fn(y_pred, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```
## Features

### ✅ Reinforcement Learning Module (35 functions)
- **Environments**: FrozenLake, Custom GridWorld
- **Algorithms**: Monte Carlo, TD Learning, Policy Iteration, Value Iteration
- **MDP Utilities**: State transitions, reward functions, probability computations
- **Visualization**: Heatmaps, policy arrows, convergence plots

### ✅ Artificial Neural Networks Module (76 functions)
- **Tensor Operations**: PyTorch basics, autograd
- **Perceptron**: sklearn implementation
- **ADALINE**: Manual and PyTorch versions
- **MLP**: Multi-layer perceptron for classification and regression
- **CNN**: Convolutional neural networks (simple nn.Sequential style)
- **Filters**: Custom CNN filters with TensorFlow
- **Transfer Learning**: Pre-trained model fine-tuning

## Requirements

- Python >= 3.7
- NumPy >= 1.21.0
- Matplotlib >= 3.4.0
- PyTorch >= 1.10.0 (for ANN module)
- TensorFlow >= 2.8.0 (for CNN filters)
- Scikit-learn >= 1.0.0 (for perceptron)
- Gymnasium >= 0.28.0 (for RL module)

## Key Design Philosophy

**Simple, Beginner-Friendly Code:**
- Uses `nn.Sequential()` for neural networks (no complex classes)
- Clear variable names: `X_train`, `y_train`, `model`, `loss_fn`
- Simple for loops and if-else statements
- No lambda functions or advanced Python features
- Easy to understand and modify

## Documentation

- **111 total functions** (35 RL + 76 ANN)
- Complete docstrings for every function
- Usage examples included
- See documentation files for details

## License

MIT License - Free for educational use

## Links

- PyPI: https://pypi.org/project/matplotlab/
- GitHub: https://github.com/Sohail-Creates/matplotlab/

---

**For educational purposes** | ML/RL implementations made simple
