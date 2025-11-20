"""
ANN Lab Workflow Reference Functions
=====================================

These functions show you the complete code workflow for each ANN lab.
When you forget what to do next, just call the flow function for your lab
and it will print out all the code you need to copy and run.

Usage:
------
>>> from matplotlab import ann
>>> ann.flowlab1()  # Shows complete Lab 1 workflow
>>> ann.flowlab2()  # Shows complete Lab 2 workflow
>>> ann.flowlab3()  # Shows complete Lab 3 workflow
>>> ann.flowlab4()  # Shows complete Lab 4 workflow
>>> ann.flowlab5()  # Shows complete Lab 5 workflow
>>> ann.flowlab6()  # Shows complete Lab 6 workflow
>>> ann.flowlab7()  # Shows complete Lab 7 workflow
"""


def flowlab1():
    """
    Display complete code workflow for ANN Lab 1 (PyTorch Tensors).
    Shows: Environment setup, tensor creation, operations, gradients, image processing, sensor data.
    """
    code = '''
# ============================================================================
# ANN LAB 1 WORKFLOW - PyTorch Tensor Operations
# ============================================================================

# STEP 1: Import PyTorch
import torch
import matplotlib.pyplot as plt

# STEP 2: Check PyTorch version and device
print(f"PyTorch Version: {torch.__version__}")

if torch.cuda.is_available():
    print(f"PyTorch is using GPU: {torch.cuda.get_device_name(0)}")
else:
    print("PyTorch is using CPU")

# ============================================================================
# IN-LAB TASKS
# ============================================================================

# TASK 1: Create different types of tensors
print("\\nTASK 1: Creating Different Tensor Types")
print("-" * 50)

# Scalar (0-D)
scalar = torch.tensor(1.5)
print(f"Scalar: {scalar}")

# Vector (1-D)
vector = torch.tensor([1, 2, 3, 4, 5])
print(f"Vector: {vector}")

# 3x3 Matrix (2-D)
matrix = torch.rand(3, 3)
print(f"3x3 Matrix:\\n{matrix}")

# 2x3x4 3D Tensor
tensor3d = torch.rand(2, 3, 4)
print(f"3D Tensor shape: {tensor3d.shape}")
print(f"3D Tensor:\\n{tensor3d}")

# TASK 2: Core tensor operations
print("\\nTASK 2: Core Tensor Operations")
print("-" * 50)

# Element-wise addition
tensor_1 = torch.tensor([1, 2, 3])
tensor_2 = torch.tensor([4, 5, 6])
element_wise_add = tensor_1 + tensor_2
print(f"Element-wise add: {element_wise_add}")

# Element-wise multiplication
element_wise_mul = tensor_1 * tensor_2
print(f"Element-wise mul: {element_wise_mul}")

# Matrix multiplication
t1 = torch.rand(2, 3)
t2 = torch.rand(3, 4)
matrix_mul = torch.matmul(t1, t2)
print(f"Matrix multiplication result shape: {matrix_mul.shape}")

# Mean and Sum reductions
reduction_tensor = torch.rand(2, 3)
print(f"\\nOriginal tensor:\\n{reduction_tensor}")
mean_rows = torch.mean(reduction_tensor, dim=1)
sum_cols = torch.sum(reduction_tensor, dim=0)
print(f"Mean across rows (dim=1): {mean_rows}")
print(f"Sum across columns (dim=0): {sum_cols}")

# TASK 3: Reshape operations
print("\\nTASK 3: Reshape Operations")
print("-" * 50)

tensor1d = torch.arange(12)
print(f"Original 1D tensor: {tensor1d}")

tensor_3x4 = tensor1d.reshape(3, 4)
print(f"\\nReshaped to 3x4:\\n{tensor_3x4}")

tensor_2x6 = tensor1d.reshape(2, 6)
print(f"\\nReshaped to 2x6:\\n{tensor_2x6}")

# TASK 4: Compute gradients using autograd
print("\\nTASK 4: Gradient Computation with Autograd")
print("-" * 50)

x = torch.tensor(3.0, requires_grad=True)
y = x**2
y.backward()
print(f"x = {x.item()}, y = x^2 = {y.item()}")
print(f"Gradient dy/dx = {x.grad.item()}")

# ============================================================================
# POST-LAB TASKS
# ============================================================================

# SCENARIO 1: Image Processing
print("\\n" + "=" * 70)
print("POST-LAB SCENARIO 1: Image Processing")
print("=" * 70)

# Task 1: Create sample image
print("\\nTask 1: Creating 5x5 Grayscale Image")
image = torch.randint(0, 256, (5, 5), dtype=torch.float32)
print(f"Original image (pixel values 0-255):\\n{image}")

# Task 2: Normalize pixel values
print("\\nTask 2: Normalizing Pixel Values (0-1 range)")
normalized_image = image / 255.0
print(f"Normalized image:\\n{normalized_image}")

# Task 3: Apply simple filter
print("\\nTask 3: Applying Edge Detection Filter")
kernel = torch.tensor([
    [-1.0, -1.0, -1.0],
    [-1.0,  1.0, -1.0],
    [-1.0, -1.0, -1.0]
])
print(f"3x3 Kernel:\\n{kernel}")

region_of_interest = normalized_image[1:4, 1:4]
filtered_region = region_of_interest * kernel
print(f"\\nFiltered 3x3 region:\\n{filtered_region}")

# Task 4: Calculate average brightness
print("\\nTask 4: Calculating Average Brightness")
average_brightness = torch.mean(normalized_image)
print(f"Average brightness: {average_brightness.item():.4f}")

# SCENARIO 2: Data Analysis (Sensor Data)
print("\\n" + "=" * 70)
print("POST-LAB SCENARIO 2: Sensor Data Analysis")
print("=" * 70)

# Task 1: Create sensor data
print("\\nTask 1: Creating Sensor Data (30 sequential readings)")
sensor_data = torch.arange(30.0)
print(f"Sensor data: {sensor_data}")

# Task 2: Reshape into batches
print("\\nTask 2: Reshaping into 6 Batches of 5 Readings Each")
batched_data = sensor_data.reshape(6, 5)
print(f"Batched data (6 batches x 5 readings):\\n{batched_data}")

# Task 3: Calculate batch averages
print("\\nTask 3: Computing Average for Each Batch")
batch_averages = torch.mean(batched_data, dim=1)
print(f"Batch averages: {batch_averages}")

# Task 4: Reshape for sensor type analysis
print("\\nTask 4: Reshaping for Sensor Type Analysis")
sensor_type_data = sensor_data.reshape(6, 5)
print(f"Data reshaped (6 time steps x 5 sensor types):\\n{sensor_type_data}")

# Task 5: Calculate sensor type averages
print("\\nTask 5: Computing Average for Each Sensor Type")
sensor_type_averages = torch.mean(sensor_type_data, dim=0)
print(f"Sensor type averages: {sensor_type_averages}")

print("\\n" + "=" * 70)
print("LAB 1 COMPLETE - All Tasks Executed Successfully")
print("=" * 70)

# ============================================================================
# END OF LAB 1 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab2():
    """
    Display complete code workflow for ANN Lab 2 (Perceptron).
    Shows: Synthetic dataset, standardization, perceptron training, decision boundaries.
    """
    code = '''
# ============================================================================
# ANN LAB 2 WORKFLOW - Perceptron
# ============================================================================

# STEP 1: Import libraries
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Perceptron
from sklearn.inspection import DecisionBoundaryDisplay
from matplotlib import pyplot as plt
from mlxtend.plotting import plot_decision_regions
import seaborn as sns
import pandas as pd
import numpy as np

print("=" * 70)
print("ANN LAB 2: Perceptron Classification")
print("=" * 70)

# ============================================================================
# TASK 1: Synthetic Dataset (Linearly Separable Case)
# ============================================================================

print("\\nTASK 1: Working with Linearly Separable Synthetic Data")
print("-" * 70)

# Generate 2D synthetic dataset with two clusters
print("\\nStep 1: Generating synthetic dataset with make_blobs...")
X_raw, y_raw = make_blobs(n_samples=300, centers=2, random_state=54)
print(f"Dataset shape: {X_raw.shape}")
print(f"Number of samples: {len(y_raw)}")
print(f"Number of features: {X_raw.shape[1]}")

# Standardize features
print("\\nStep 2: Standardizing features...")
scaler = StandardScaler()
X_prep = scaler.fit_transform(X_raw)
print("Features standardized (mean=0, std=1)")

# Create DataFrame for visualization
data = pd.DataFrame(X_prep, columns=['X1', 'X2'])
data['y'] = y_raw
print("\\nFirst few rows of prepared data:")
print(data.head())

# Visualize data
print("\\nStep 3: Visualizing the dataset...")
sns.scatterplot(data=data, x='X1', y='X2', hue='y')
plt.title("Linearly Separable Dataset")
plt.xlabel("Feature X1")
plt.ylabel("Feature X2")
plt.show()

# Train base perceptron
print("\\nStep 4: Training perceptron...")
base_perceptron = Perceptron()
base_perceptron.fit(X_prep, y_raw)
print("Perceptron training complete!")
print(f"Number of iterations: {base_perceptron.n_iter_}")

# Plot decision boundary
print("\\nStep 5: Plotting decision boundary...")
plot = DecisionBoundaryDisplay.from_estimator(
    base_perceptron, X_prep, response_method='predict'
)
plot.ax_.scatter(X_prep[:, 0], X_prep[:, 1], c=y_raw, edgecolor='k')
plt.title("Perceptron Decision Boundary")
plt.xlabel("Feature X1")
plt.ylabel("Feature X2")
plt.show()

# Compare different max_iter values
print("\\nStep 6: Comparing different max_iter values...")
increased_max_iter_perceptron = Perceptron(random_state=53, max_iter=100)
decreased_max_iter_perceptron = Perceptron(random_state=42, max_iter=1)

increased_max_iter_perceptron.fit(X_prep, y_raw)
decreased_max_iter_perceptron.fit(X_prep, y_raw)

print(f"High max_iter (100): Converged in {increased_max_iter_perceptron.n_iter_} iterations")
print(f"Low max_iter (1): Stopped at {decreased_max_iter_perceptron.n_iter_} iteration(s)")

# Visualize decision regions
print("\\nStep 7: Visualizing decision regions with mlxtend...")
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plot_decision_regions(X_prep, y_raw, clf=increased_max_iter_perceptron)
plt.title("Decision Regions (max_iter=100)")
plt.xlabel("Feature X1")
plt.ylabel("Feature X2")

plt.subplot(1, 2, 2)
plot_decision_regions(X_prep, y_raw, clf=decreased_max_iter_perceptron)
plt.title("Decision Regions (max_iter=1)")
plt.xlabel("Feature X1")
plt.ylabel("Feature X2")

plt.tight_layout()
plt.show()

# ============================================================================
# TASK 2: Raw vs Preprocessed Data Comparison
# ============================================================================

print("\\n" + "=" * 70)
print("TASK 2: Comparing Raw vs Standardized Data")
print("=" * 70)

# Train on raw data
print("\\nTraining perceptron on raw (unstandardized) data...")
raw_perceptron = Perceptron(random_state=53)
raw_perceptron.fit(X_raw, y_raw)
print(f"Raw data - Iterations: {raw_perceptron.n_iter_}")

# Train on standardized data
print("\\nTraining perceptron on standardized data...")
prep_perceptron = Perceptron(random_state=53)
prep_perceptron.fit(X_prep, y_raw)
print(f"Standardized data - Iterations: {prep_perceptron.n_iter_}")

# Visualize comparison
print("\\nVisualizing decision boundaries comparison...")
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plot_decision_regions(X_raw, y_raw, clf=raw_perceptron)
plt.title("Raw Data (Unstandardized)")
plt.xlabel("Feature 1 (Raw Scale)")
plt.ylabel("Feature 2 (Raw Scale)")

plt.subplot(1, 2, 2)
plot_decision_regions(X_prep, y_raw, clf=prep_perceptron)
plt.title("Standardized Data")
plt.xlabel("Feature 1 (Standardized)")
plt.ylabel("Feature 2 (Standardized)")

plt.tight_layout()
plt.show()

print("\\n" + "=" * 70)
print("Why is this dataset linearly separable?")
print("The make_blobs function generates clusters that are well-separated")
print("in the feature space, guaranteeing a straight-line separator exists.")
print("=" * 70)

print("\\nLAB 2 COMPLETE - Perceptron Successfully Trained and Evaluated!")

# ============================================================================
# END OF LAB 2 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab3():
    """
    Display complete code workflow for ANN Lab 3 (ADALINE Delta Rule).
    Shows: Manual, semi-manual, automatic ADALINE with Iris dataset.
    """
    code = '''
# ============================================================================
# ANN LAB 3 WORKFLOW - ADALINE (Delta Rule)
# ============================================================================

# STEP 1: Import libraries
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from torch.autograd import grad
import torch.nn as nn
import torch

print("=" * 70)
print("ANN LAB 3: ADALINE (Adaptive Linear Neuron)")
print("=" * 70)

# STEP 2: Load and prepare Iris dataset
print("\\nStep 1: Loading Iris dataset...")
df = pd.DataFrame(data=load_iris().data, columns=['x1', 'x2', 'x3', 'x4'])
df['y'] = load_iris().target
df = df.iloc[50:150]
df['y'] = df['y'].apply(lambda x: 0 if x == 1 else 1)
print("Dataset loaded: Versicolor vs Virginica (100 samples)")
print(df.head())

# Extract features and target
X = torch.tensor(df[['x2', 'x3']].values, dtype=torch.float32)
y = torch.tensor(df['y'].values, dtype=torch.int32)

# Shuffle and split data
torch.manual_seed(53)
shuffle_idx = torch.randperm(len(y), dtype=torch.int32)
X, y = X[shuffle_idx], y[shuffle_idx]

split_point = int(len(shuffle_idx) * 0.7)
X_train, X_test = X[:split_point], X[split_point:]
y_train, y_test = y[:split_point], y[split_point:]

print(f"\\nTrain set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")

# Standardize features
mu, sigma = torch.mean(X_train, dim=0), torch.std(X_train, dim=0)
X_train_prep = (X_train - mu) / sigma
X_test_prep = (X_test - mu) / sigma
print("Features standardized")

# ============================================================================
# TASK 1: Manual ADALINE Implementation
# ============================================================================

print("\\n" + "=" * 70)
print("TASK 1: Manual ADALINE (Gradients Computed Manually)")
print("=" * 70)

class manual_ADALINE:
    def __init__(self, num_features):
        self.num_features = num_features
        self.weights = torch.zeros(num_features, 1, dtype=torch.float32)
        self.biases = torch.zeros(1, dtype=torch.float32)

    def forward(self, x):
        return torch.mm(x, self.weights) + self.biases

    def backward(self, x, yhat, y):
        grad_loss = (yhat.view(-1, 1) - y.view(-1, 1))
        grad_loss_weights = torch.mm(x.t(), grad_loss) / len(y)
        grad_loss_biases = torch.sum(grad_loss) / len(y)
        return grad_loss_weights, grad_loss_biases

def loss_function(yhat, y):
    return torch.mean((yhat - y) ** 2)

def train_manual(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    cost = []
    torch.manual_seed(seed)

    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)

        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch].view(-1, 1)
            yhat = model.forward(xb)
            loss = loss_function(yhat, yb)
            gradient_W, gradient_B = model.backward(xb, yhat, yb)

            with torch.no_grad():
                model.weights -= lr * gradient_W
                model.biases -= lr * gradient_B

        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = loss_function(yhat_full, y.view(-1, 1))
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())

    return cost

print("\\nTraining Manual ADALINE...")
model_manual = manual_ADALINE(num_features=X_train.size(1))
cost_manual = train_manual(model_manual, X_train, y_train.float(), total_epochs=20, lr=0.01, batch_size=16)

plt.plot(range(len(cost_manual)), cost_manual)
plt.ylabel('Mean Squared Error')
plt.xlabel('Epoch')
plt.title('Manual ADALINE Training Loss')
plt.grid(True)
plt.show()

# Evaluate manual ADALINE
train_ones = torch.ones(y_train.size())
train_zeroes = torch.zeros(y_train.size())
train_predictions = model_manual.forward(X_train)
train_accuracy = torch.mean((torch.where(train_predictions > 0.5, train_ones, train_zeroes).int() == y_train).float())

test_ones = torch.ones(y_test.size())
test_zeroes = torch.zeros(y_test.size())
test_predictions = model_manual.forward(X_test)
test_accuracy = torch.mean((torch.where(test_predictions > 0.5, test_ones, test_zeroes).int() == y_test).float())

print(f'\\nManual ADALINE - Training Accuracy: {train_accuracy * 100:.2f}%')
print(f'Manual ADALINE - Test Accuracy: {test_accuracy * 100:.2f}%')

# ============================================================================
# TASK 2: Semi-Manual ADALINE Implementation
# ============================================================================

print("\\n" + "=" * 70)
print("TASK 2: Semi-Manual ADALINE (Using Autograd)")
print("=" * 70)

class semi_ADALINE:
    def __init__(self, num_features):
        self.num_features = num_features
        self.weights = torch.zeros(num_features, 1, dtype=torch.float32, requires_grad=True)
        self.bias = torch.zeros(1, dtype=torch.float32, requires_grad=True)

    def forward(self, x):
        return torch.mm(x, self.weights) + self.bias

def train_semi(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    cost = []
    torch.manual_seed(seed)

    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)

        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch]
            yhat = model.forward(xb)
            loss = loss_function(yhat, yb)

            gradient_W = grad(loss, model.weights, retain_graph=True)[0]
            gradient_B = grad(loss, model.bias)[0]

            with torch.no_grad():
                model.weights -= lr * gradient_W
                model.bias -= lr * gradient_B

        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = loss_function(yhat_full, y)
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())

    return cost

print("\\nTraining Semi-Manual ADALINE...")
model_semi = semi_ADALINE(num_features=X_train.size(1))
cost_semi = train_semi(model_semi, X_train, y_train.float(), total_epochs=20, lr=0.01, batch_size=16)

plt.plot(range(len(cost_semi)), cost_semi)
plt.ylabel('Mean Squared Error')
plt.xlabel('Epoch')
plt.title('Semi-Manual ADALINE Training Loss')
plt.grid(True)
plt.show()

# ============================================================================
# TASK 3: Automatic ADALINE Implementation
# ============================================================================

print("\\n" + "=" * 70)
print("TASK 3: Automatic ADALINE (nn.Module + Optimizer)")
print("=" * 70)

class automatic_ADALINE(nn.Module):
    def __init__(self, num_features):
        super(automatic_ADALINE, self).__init__()
        self.linear = nn.Linear(num_features, 1)
    
    def forward(self, x):
        return self.linear(x)

def train_automatic(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    cost = []
    torch.manual_seed(seed)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)

        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch].view(-1, 1)
            yhat = model(xb)
            loss = criterion(yhat, yb)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        with torch.no_grad():
            yhat_full = model(x)
            curr_loss = criterion(yhat_full, y.view(-1, 1))
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())

    return cost

print("\\nTraining Automatic ADALINE...")
model_auto = automatic_ADALINE(num_features=X_train.size(1))
cost_auto = train_automatic(model_auto, X_train, y_train.float(), total_epochs=20, lr=0.01, batch_size=16)

plt.plot(range(len(cost_auto)), cost_auto)
plt.ylabel('Mean Squared Error')
plt.xlabel('Epoch')
plt.title('Automatic ADALINE Training Loss')
plt.grid(True)
plt.show()

# Evaluate automatic ADALINE
with torch.no_grad():
    train_predictions = model_auto(X_train)
    train_accuracy = torch.mean((torch.where(train_predictions > 0.5, train_ones, train_zeroes).int() == y_train).float())
    
    test_predictions = model_auto(X_test)
    test_accuracy = torch.mean((torch.where(test_predictions > 0.5, test_ones, test_zeroes).int() == y_test).float())

print(f'\\nAutomatic ADALINE - Training Accuracy: {train_accuracy * 100:.2f}%')
print(f'Automatic ADALINE - Test Accuracy: {test_accuracy * 100:.2f}%')

print("\\n" + "=" * 70)
print("LAB 3 COMPLETE - All 3 ADALINE Implementations Trained Successfully!")
print("=" * 70)

# ============================================================================
# END OF LAB 3 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab4():
    """
    Display complete code workflow for ANN Lab 4 (Multi-Layer Perceptron).
    Shows: XOR with manual backprop, XOR with PyTorch, student performance classification.
    """
    code = '''
# ============================================================================
# ANN LAB 4 WORKFLOW - Multi-Layer Perceptron (MLP)
# ============================================================================

# STEP 1: Import libraries
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from torch.utils.data import TensorDataset, random_split, DataLoader
import torch
import torch.nn as nn

print("=" * 70)
print("ANN LAB 4: Multi-Layer Perceptron (MLP)")
print("=" * 70)

# ============================================================================
# TASK 1: MLP on XOR (Manual Backpropagation using NumPy)
# ============================================================================

print("\\nTASK 1: XOR Problem with Manual Backpropagation (NumPy)")
print("-" * 70)

# XOR dataset
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

print("XOR Dataset:")
for i in range(len(X)):
    print(f"Input: {X[i]}, Output: {y[i][0]}")

# Initialize weights and biases
np.random.seed(42)
W1 = np.random.randn(2, 2) * 0.01
b1 = np.zeros((1, 2))
W2 = np.random.randn(2, 1) * 0.01
b2 = np.zeros((1, 1))
lr = 0.5
epochs = 10000

# Activation functions
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

print(f"\\nTraining MLP (2->2->1) for {epochs} epochs...")
print("Architecture: Input(2) -> Hidden(2) -> Output(1)")

# Training loop
for epoch in range(epochs):
    # Forward pass
    z1 = np.dot(X, W1) + b1
    a1 = sigmoid(z1)
    z2 = np.dot(a1, W2) + b2
    y_pred = sigmoid(z2)
    loss = 0.5 * np.mean((y - y_pred) ** 2)

    # Backward pass
    delta2 = (y_pred - y) * sigmoid_derivative(y_pred)
    dW2 = np.dot(a1.T, delta2)
    db2 = np.sum(delta2, axis=0, keepdims=True)
    delta1 = np.dot(delta2, W2.T) * sigmoid_derivative(a1)
    dW1 = np.dot(X.T, delta1)
    db1 = np.sum(delta1, axis=0, keepdims=True)

    # Update weights
    W2 -= lr * dW2
    b2 -= lr * db2
    W1 -= lr * dW1
    b1 -= lr * db1

    if (epoch + 1) % 2000 == 0:
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss:.6f}")

print("\\nFinal predictions:")
for i in range(len(X)):
    print(f"Input: {X[i]}, Predicted: {y_pred[i][0]:.4f}, Actual: {y[i][0]}")

# ============================================================================
# TASK 2: MLP for XOR Classification (PyTorch)
# ============================================================================

print("\\n" + "=" * 70)
print("TASK 2: XOR Problem with PyTorch")
print("=" * 70)

# Convert to PyTorch tensors
X_torch = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32)
y_torch = torch.tensor([[0], [1], [1], [0]], dtype=torch.float32)

# Create MLP model
model = nn.Sequential(
    nn.Linear(2, 2),
    nn.Sigmoid(),
    nn.Linear(2, 1),
    nn.Sigmoid()
)

criterion = nn.BCELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.5)

print("\\nTraining PyTorch MLP...")
losses = []
epochs = 1000
for epoch in range(epochs):
    outputs = model(X_torch)
    loss = criterion(outputs, y_torch)
    losses.append(loss.item())
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 200 == 0:
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item():.4f}")

# Plot loss curve
plt.plot(losses)
plt.title("Loss Curve - XOR Problem")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.grid(True)
plt.show()

# Test predictions
print("\\nFinal predictions:")
with torch.no_grad():
    predictions = model(X_torch)
    for i in range(len(X_torch)):
        print(f"Input: {X_torch[i].numpy()}, Predicted: {predictions[i][0]:.4f}, Actual: {y_torch[i][0]:.0f}")

# ============================================================================
# TASK 3: Student Performance Classification
# ============================================================================

print("\\n" + "=" * 70)
print("TASK 3: Predicting Student Performance (Pass/Fail)")
print("=" * 70)

# NOTE: This uses synthetic data if student_dataset.csv is not available
# In actual lab, load: df = pd.read_csv('student_dataset.csv')

print("\\nGenerating synthetic student data...")
np.random.seed(42)
n_samples = 500
student_data = pd.DataFrame({
    'Age': np.random.randint(18, 25, n_samples),
    'distance to university (km)': np.random.uniform(0, 50, n_samples),
    'Percent Attended': np.random.uniform(40, 100, n_samples),
    'Study Hours': np.random.uniform(0, 10, n_samples),
    'Previous Grade': np.random.uniform(40, 100, n_samples),
})

# Generate target based on features
student_data['Pass'] = ((student_data['Percent Attended'] > 70) & 
                        (student_data['Study Hours'] > 3) & 
                        (student_data['Previous Grade'] > 50)).astype(int)

print(f"Dataset shape: {student_data.shape}")
print("\\nFirst few rows:")
print(student_data.head())

# Drop any missing values
student_data = student_data.dropna()

# Normalize features
numeric_columns = ['Age', 'distance to university (km)', 'Percent Attended', 
                   'Study Hours', 'Previous Grade']
student_data[numeric_columns] = ((student_data[numeric_columns] - 
                                  student_data[numeric_columns].mean()) / 
                                 student_data[numeric_columns].std())

print("\\nData normalized (mean=0, std=1)")

# Prepare tensors
data_array = student_data.values
tensor_data = torch.from_numpy(data_array).float()
X, y = tensor_data[:, :-1], tensor_data[:, -1]
tensor_dataset = TensorDataset(X, y)

# Split data
total_size = len(tensor_dataset)
train_size = int(0.8 * total_size)
test_size = total_size - train_size

train_dataset, test_dataset = random_split(
    tensor_dataset,
    [train_size, test_size],
    generator=torch.Generator().manual_seed(53)
)

print(f'\\nTotal dataset: {total_size}, Train: {train_size}, Test: {test_size}')

# Create data loaders
batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# Create MLP model
model = nn.Sequential(
    nn.Linear(5, 4),
    nn.ReLU(),
    nn.Linear(4, 3),
    nn.ReLU(),
    nn.Linear(3, 1),
    nn.Sigmoid()
)

criterion = nn.BCELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

print("\\nTraining student performance classifier...")
print("Architecture: Input(5) -> Hidden(4) -> Hidden(3) -> Output(1)")

# Training
epochs = 50
model.train()
for epoch in range(epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        outputs = model(data).flatten()
        loss = criterion(outputs, target)
        loss.backward()
        optimizer.step()
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch + 1}/{epochs} completed")

# Evaluation
model.eval()
with torch.no_grad():
    total_correct = 0
    total_samples = 0
    test_loss = 0

    for data, target in test_loader:
        outputs = model(data).flatten()
        loss = criterion(outputs, target)
        test_loss += loss.item()

        pred = (outputs > 0.5).float()
        total_correct += pred.eq(target).sum().item()
        total_samples += target.size(0)

    test_loss /= len(test_loader)
    accuracy = 100.0 * total_correct / total_samples

    print(f'\\nTest Set: Average Loss: {test_loss:.4f}, Accuracy: {accuracy:.2f}%')

print("\\n" + "=" * 70)
print("LAB 4 COMPLETE - All MLP Tasks Completed Successfully!")
print("=" * 70)

# ============================================================================
# END OF LAB 4 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab5():
    """
    Display complete code workflow for ANN Lab 5 (CNN - Fashion MNIST).
    Shows: CNN architecture, training, evaluation, visualization.
    """
    code = '''
# ============================================================================
# ANN LAB 5 WORKFLOW - Convolutional Neural Networks (CNN)
# ============================================================================

# STEP 1: Import libraries
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

# STEP 2: Load Fashion MNIST dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

train_dataset = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# STEP 3: Define CNN model
model = nn.Sequential(
    nn.Conv2d(1, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32, 64, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(64 * 7 * 7, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)

# STEP 4: Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# STEP 5: Training loop
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

epochs = 5
train_losses = []

for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    
    avg_loss = running_loss / len(train_loader)
    train_losses.append(avg_loss)
    print(f'Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}')

# STEP 6: Plot training loss
plt.plot(train_losses)
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('CNN Training Loss')
plt.show()

# STEP 7: Evaluation
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        predictions = torch.argmax(outputs, dim=1)
        total += labels.size(0)
        correct += (predictions == labels).sum().item()

accuracy = 100 * correct / total
print(f'Test Accuracy: {accuracy:.2f}%')

# STEP 8: Visualize predictions
class_names = ['T-shirt', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

model.eval()
images, labels = next(iter(test_loader))
images, labels = images.to(device), labels.to(device)

with torch.no_grad():
    outputs = model(images)
    predictions = torch.argmax(outputs, dim=1)

fig, axes = plt.subplots(2, 5, figsize=(12, 6))
for i, ax in enumerate(axes.flat):
    img = images[i].cpu().squeeze()
    ax.imshow(img, cmap='gray')
    ax.set_title(f'Pred: {class_names[predictions[i]]}\nTrue: {class_names[labels[i]]}')
    ax.axis('off')
plt.tight_layout()
plt.show()

# ============================================================================
# END OF LAB 5 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab6():
    """
    Display complete code workflow for ANN Lab 6 (CNN Custom Filters).
    Shows: Custom kernels, edge detection, image filtering with TensorFlow.
    """
    code = '''
# ============================================================================
# ANN LAB 6 WORKFLOW - CNN Custom Filters
# ============================================================================

# STEP 1: Import libraries
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# STEP 2: Load and prepare image
image_path = 'your_image.jpg'
img = Image.open(image_path).convert('L')
img = img.resize((224, 224))
img_array = np.array(img) / 255.0
img_array = img_array.reshape(1, 224, 224, 1)

# STEP 3: Visualize original image
plt.imshow(img, cmap='gray')
plt.title('Original Image')
plt.axis('off')
plt.show()

# STEP 4: Define custom filters
edge_detection_kernel = np.array([
    [-1, -1, -1],
    [-1,  8, -1],
    [-1, -1, -1]
], dtype=np.float32).reshape(3, 3, 1, 1)

sharpen_kernel = np.array([
    [ 0, -1,  0],
    [-1,  5, -1],
    [ 0, -1,  0]
], dtype=np.float32).reshape(3, 3, 1, 1)

blur_kernel = np.array([
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1]
], dtype=np.float32).reshape(3, 3, 1, 1) / 9.0

# STEP 5: Create model with custom filter
model = models.Sequential([
    layers.Conv2D(1, (3, 3), padding='same', input_shape=(224, 224, 1))
])

# STEP 6: Apply edge detection
model.layers[0].set_weights([edge_detection_kernel, np.zeros(1)])
edge_output = model.predict(img_array)

plt.imshow(edge_output[0, :, :, 0], cmap='gray')
plt.title('Edge Detection Filter')
plt.axis('off')
plt.show()

# STEP 7: Apply sharpen filter
model.layers[0].set_weights([sharpen_kernel, np.zeros(1)])
sharpen_output = model.predict(img_array)

plt.imshow(sharpen_output[0, :, :, 0], cmap='gray')
plt.title('Sharpen Filter')
plt.axis('off')
plt.show()

# STEP 8: Apply blur filter
model.layers[0].set_weights([blur_kernel, np.zeros(1)])
blur_output = model.predict(img_array)

plt.imshow(blur_output[0, :, :, 0], cmap='gray')
plt.title('Blur Filter')
plt.axis('off')
plt.show()

# STEP 9: Compare all filters
fig, axes = plt.subplots(2, 2, figsize=(10, 10))

axes[0, 0].imshow(img, cmap='gray')
axes[0, 0].set_title('Original')
axes[0, 0].axis('off')

axes[0, 1].imshow(edge_output[0, :, :, 0], cmap='gray')
axes[0, 1].set_title('Edge Detection')
axes[0, 1].axis('off')

axes[1, 0].imshow(sharpen_output[0, :, :, 0], cmap='gray')
axes[1, 0].set_title('Sharpen')
axes[1, 0].axis('off')

axes[1, 1].imshow(blur_output[0, :, :, 0], cmap='gray')
axes[1, 1].set_title('Blur')
axes[1, 1].axis('off')

plt.tight_layout()
plt.show()

# ============================================================================
# END OF LAB 6 WORKFLOW
# ============================================================================
'''
    print(code)


def flowlab7():
    """
    Display complete code workflow for ANN Lab 7 (Transfer Learning).
    Shows: Pre-trained model loading, fine-tuning, Fashion MNIST classification.
    """
    code = '''
# ============================================================================
# ANN LAB 7 WORKFLOW - Transfer Learning
# ============================================================================

# STEP 1: Import libraries
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

# STEP 2: Load pre-trained ResNet model
model = models.resnet18(pretrained=True)

# STEP 3: Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# STEP 4: Replace final layer for Fashion MNIST (10 classes)
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 10)

# STEP 5: Prepare Fashion MNIST dataset
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

train_dataset = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# STEP 6: Loss and optimizer (only train final layer)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)

# STEP 7: Training loop
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

epochs = 5
train_losses = []

for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    
    avg_loss = running_loss / len(train_loader)
    train_losses.append(avg_loss)
    print(f'Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}')

# STEP 8: Plot training loss
plt.plot(train_losses)
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Transfer Learning Training Loss')
plt.show()

# STEP 9: Evaluation
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        predictions = torch.argmax(outputs, dim=1)
        total += labels.size(0)
        correct += (predictions == labels).sum().item()

accuracy = 100 * correct / total
print(f'Test Accuracy: {accuracy:.2f}%')

# STEP 10: Save fine-tuned model
torch.save(model.state_dict(), 'fashion_mnist_transfer_learning.pth')
print('Model saved successfully')

# ============================================================================
# END OF LAB 7 WORKFLOW
# ============================================================================
'''
    print(code)
