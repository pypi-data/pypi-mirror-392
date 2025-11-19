EXPERIMENTS = {
    1: """# Experiment 1: Hello World
print("Hello, World!")
""",

    2: """# Experiment 2: Naive Bayes on Iris Dataset
import numpy as np
from math import sqrt, pi, exp
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Gaussian PDF
def gaussian_pdf(x, mean, var):
    exponent = exp(-((x - mean) ** 2) / (2 * var))
    return (1 / sqrt(2 * pi * var)) * exponent

# Summarize dataset by class
def summarize_by_class(X, y):
    separated = {}
    for features, label in zip(X, y):
        separated.setdefault(label, []).append(features)

    summaries = {}
    for label, rows in separated.items():
        rows = np.array(rows)
        means = rows.mean(axis=0)
        variances = rows.var(axis=0)
        prior = len(rows) / len(X)
        summaries[label] = (means, variances, prior)
    return summaries

# Calculate class probabilities
def calculate_class_probabilities(summaries, input_vector):
    probabilities = {}
    for label, (means, variances, prior) in summaries.items():
        prob = prior
        for i in range(len(means)):
            prob *= gaussian_pdf(input_vector[i], means[i], variances[i])
        probabilities[label] = prob
    return probabilities

# Predict one instance
def predict(summaries, input_vector):
    probabilities = calculate_class_probabilities(summaries, input_vector)
    return max(probabilities, key=probabilities.get)

# Predict multiple instances
def get_predictions(summaries, X_test):
    return [predict(summaries, x) for x in X_test]

# Custom accuracy
def accuracy_score(y_true, y_pred):
    return sum(y_t == y_p for y_t, y_p in zip(y_true, y_pred)) / len(y_true)

# Load dataset
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.3, random_state=42
)

# Train model
summaries = summarize_by_class(X_train, y_train)

# Predict
predictions = get_predictions(summaries, X_test)

# Evaluate
accuracy = accuracy_score(y_test, predictions)
print("Accuracy:", accuracy)

# Show classifications
print("\nSample classifications (True vs Predicted):")
for i in range(10):
    print(f"True: {y_test[i]}, Predicted: {predictions[i]}")
""",

    3: """# Experiment 3: Logistic Regression Decision Boundary using Gradient Descent
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load dataset
data = pd.read_csv(r"C:\\Users\\LENOVA\\Desktop\\Sem-VII\\Practical\\Deep Learning\\Home Material\\linearly_separable_data_custom.csv")
X = data[['Feature1', 'Feature2']].values
y = data['Class'].values

# Normalize features
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_norm = (X - X_mean) / X_std

# Add bias column
X_bias = np.c_[np.ones(X_norm.shape[0]), X_norm]

# Initialize weights
np.random.seed(42)
weights = np.random.randn(X_bias.shape[1])
print("Initial weights:", weights)

# Sigmoid function
def sigmoid(z):
    z = np.clip(z, -250, 250)
    return 1 / (1 + np.exp(-z))

# Predict probabilities
def predict_proba(X, weights):
    return sigmoid(np.dot(X, weights))

# Predict class
def predict_class(X, weights):
    return predict_proba(X, weights) >= 0.5

# Plot decision boundary
def plot_decision_boundary(weights, color, linestyle, label):
    x1s = np.linspace(X_norm[:, 0].min(), X_norm[:, 0].max(), 100)
    x2s = -(weights[0] + weights[1] * x1s) / weights[2]
    plt.plot(x1s, x2s, color=color, linestyle=linestyle, label=label, linewidth=2)

# Gradient descent settings
learning_rate = 0.1
epochs = 5000

weight_history = [weights.copy()]
iteration_points = [1, 500, 2500, epochs]

# Gradient descent loop
for epoch in range(1, epochs + 1):
    predictions = predict_proba(X_bias, weights)
    errors = predictions - y
    gradients = np.dot(X_bias.T, errors) / X_bias.shape[0]
    weights -= learning_rate * gradients

    if epoch in iteration_points:
        weight_history.append(weights.copy())

# Final accuracy
final_predictions = predict_class(X_bias, weights).astype(int)
accuracy = np.mean(final_predictions == y) * 100

# Plot evolution
plt.figure(figsize=(12, 8))
plt.scatter(X_norm[y == 0][:, 0], X_norm[y == 0][:, 1], c='blue', marker='o', s=50, label='Class 0', edgecolor='black')
plt.scatter(X_norm[y == 1][:, 0], X_norm[y == 1][:, 1], c='red', marker='s', s=50, label='Class 1', edgecolor='black')

colors = ['green', 'orange', 'purple', 'black']
linestyles = ['--', '-.', '-', '-']
labels = ['Initial Weights', 'Epoch 1', 'Epoch 500', 'Epoch 2500', 'Final Epoch 5000']

for w, color, ls, label in zip(weight_history, colors + [colors[-1]], linestyles + [linestyles[-1]], labels):
    plot_decision_boundary(w, color, ls, label)

plt.xlabel('Normalized Feature 1')
plt.ylabel('Normalized Feature 2')
plt.title('Perceptron Learning Algorithm using Gradient Descent')
plt.legend()
plt.grid(True)
plt.show()

print(f"Final accuracy after {epochs} epochs: {accuracy:.2f}%")
print("Final weights:", weights)
""",
    4: """# Experiment 4: Linearly Separable Data using Multivariate Gaussian Distribution for Binary Classification visualize the data and decision boundary using the discriminant function, and analyze how different parameters affect the boundary
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# 1. ISOTROPIC GAUSSIAN CASE
# ---------------------------

np.random.seed(42)
num_samples = 100
common_var = 1

# Class 0 data
mean0_iso = np.array([-2, -2])
cov0_iso = np.array([[common_var, 0], [0, common_var]])
X0_iso = np.random.multivariate_normal(mean0_iso, cov0_iso, num_samples)
y0_iso = np.zeros(num_samples)

# Class 1 data
mean1_iso = np.array([2, 2])
cov1_iso = np.array([[common_var, 0], [0, common_var]])
X1_iso = np.random.multivariate_normal(mean1_iso, cov1_iso, num_samples)
y1_iso = np.ones(num_samples)

# Combine data
X_iso = np.vstack([X0_iso, X1_iso])
y_iso = np.hstack([y0_iso, y1_iso])

# Simplified LDA for isotropic covariance (σ²I)
def simplified_lda(X, y):
    X0, X1 = X[y == 0], X[y == 1]
    mean0, mean1 = np.mean(X0, axis=0), np.mean(X1, axis=0)
    total_var = np.var(X, axis=0).mean()
    w = (mean1 - mean0) / total_var
    b = -0.5 * (np.dot(mean1, mean1) - np.dot(mean0, mean0)) / total_var
    return w, b, mean0, mean1

w_iso, b_iso, m0_iso, m1_iso = simplified_lda(X_iso, y_iso)

# Plot isotropic case
plt.figure(figsize=(8, 6))
plt.scatter(X0_iso[:, 0], X0_iso[:, 1], color='blue', label='Class 0', edgecolor='k', s=70)
plt.scatter(X1_iso[:, 0], X1_iso[:, 1], color='orange', label='Class 1', edgecolor='k', s=70)
x_vals = np.linspace(-5, 5, 100)
y_vals = (-w_iso[0] * x_vals - b_iso) / w_iso[1]
plt.plot(x_vals, y_vals, 'r--', linewidth=2, label='Isotropic Boundary')
plt.plot([m0_iso[0], m1_iso[0]], [m0_iso[1], m1_iso[1]], 'go-', linewidth=2, label='Means Connection')
plt.title('Linear Decision Boundary (Isotropic: Σ = σ²I)')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.grid(True)
plt.legend()
plt.show()

print("Isotropic Case:")
print("Weight vector (w):", w_iso)
print("Bias term (b):", b_iso)
print()

# ---------------------------
# 2. SPHERICAL GAUSSIAN CASE
# ---------------------------

np.random.seed(42)
common_var = 1

mean0_sph = np.array([-4, -4])
cov0_sph = np.array([[common_var, 0], [0, common_var]])
X0_sph = np.random.multivariate_normal(mean0_sph, cov0_sph, num_samples)
y0_sph = np.zeros(num_samples)

mean1_sph = np.array([4, 4])
cov1_sph = np.array([[common_var, 0], [0, common_var]])
X1_sph = np.random.multivariate_normal(mean1_sph, cov1_sph, num_samples)
y1_sph = np.ones(num_samples)

X_sph = np.vstack([X0_sph, X1_sph])
y_sph = np.hstack([y0_sph, y1_sph])

def calculate_spherical_boundary(X, y):
    mean0, mean1 = np.mean(X[y == 0], axis=0), np.mean(X[y == 1], axis=0)
    w = mean1 - mean0
    midpoint = (mean0 + mean1) / 2
    b = -np.dot(w, midpoint)
    return w, b, mean0, mean1

w_sph, b_sph, m0_sph, m1_sph = calculate_spherical_boundary(X_sph, y_sph)

plt.figure(figsize=(8, 6))
plt.scatter(X_sph[y_sph == 0][:, 0], X_sph[y_sph == 0][:, 1], color='blue', label='Class 0', edgecolor='k', s=70)
plt.scatter(X_sph[y_sph == 1][:, 0], X_sph[y_sph == 1][:, 1], color='orange', label='Class 1', edgecolor='k', s=70)
y_plot_sph = (-w_sph[0] * x_vals - b_sph) / w_sph[1]
plt.plot(x_vals, y_plot_sph, 'r--', linewidth=2, label='Spherical Boundary')
plt.plot([m0_sph[0], m1_sph[0]], [m0_sph[1], m1_sph[1]], 'go-', linewidth=2, label='Means Connection')
plt.title('Decision Boundary (Spherical Covariance)')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.grid(True)
plt.legend()
plt.show()

print("Spherical Case:")
print("Weight vector (w):", w_sph)
print("Bias term (b):", b_sph)
print()

# -------------------------------
# 3. NON-SPHERICAL GAUSSIAN CASE
# -------------------------------

np.random.seed(42)
mean0_ns = np.array([-2, -2])
mean1_ns = np.array([2, 2])
cov_ns = np.array([[2.5, 1.0], [1.0, 1.5]])

X0_ns = np.random.multivariate_normal(mean0_ns, cov_ns, num_samples)
X1_ns = np.random.multivariate_normal(mean1_ns, cov_ns, num_samples)
y0_ns = np.zeros(num_samples)
y1_ns = np.ones(num_samples)

X_ns = np.vstack([X0_ns, X1_ns])
y_ns = np.hstack([y0_ns, y1_ns])

def calculate_non_spherical_boundary(X, y):
    X0, X1 = X[y == 0], X[y == 1]
    mean0, mean1 = np.mean(X0, axis=0), np.mean(X1, axis=0)
    Sw0 = (X0 - mean0).T @ (X0 - mean0)
    Sw1 = (X1 - mean1).T @ (X1 - mean1)
    pooled_cov = (Sw0 + Sw1) / (len(X0) + len(X1) - 2)
    inv_cov = np.linalg.inv(pooled_cov)
    w = inv_cov @ (mean1 - mean0)
    b = -0.5 * (mean1.T @ inv_cov @ mean1 - mean0.T @ inv_cov @ mean0)
    return w, b, mean0, mean1

w_ns, b_ns, m0_ns, m1_ns = calculate_non_spherical_boundary(X_ns, y_ns)

plt.figure(figsize=(8, 6))
plt.scatter(X_ns[y_ns == 0][:, 0], X_ns[y_ns == 0][:, 1], color='blue', label='Class 0', edgecolor='k', s=70)
plt.scatter(X_ns[y_ns == 1][:, 0], X_ns[y_ns == 1][:, 1], color='orange', label='Class 1', edgecolor='k', s=70)
y_plot_ns = (-w_ns[0] * x_vals - b_ns) / w_ns[1]
plt.plot(x_vals, y_plot_ns, 'r--', linewidth=2, label='Non-Spherical Boundary')
plt.plot([m0_ns[0], m1_ns[0]], [m0_ns[1], m1_ns[1]], 'go-', linewidth=2, label='Means Connection')
plt.title('Decision Boundary (Shared Non-Spherical Covariance)')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.grid(True)
plt.legend()
plt.show()

print("Non-Spherical Case:")
print("Weight vector (w):", w_ns)
print("Bias term (b):", b_ns)
""",
        5: """# Experiment 5: Multiple Linear Regression using Housing Dataset with Gradient Descent
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv(r"C:\\Users\\LENOVA\\Desktop\\Sem-VII\\Practical\\Deep Learning\\Home Material\\Housing.csv")

# Convert binary categorical columns 'yes'/'no' to 1/0
binary_columns = ['mainroad', 'guestroom', 'basement', 'hotwaterheating',
                  'airconditioning', 'prefarea']

for col in binary_columns:
    df[col] = df[col].map({'yes': 1, 'no': 0})

# One-hot encode furnishingstatus
furnishing_dummies = pd.get_dummies(df['furnishingstatus'], prefix='furnishing')
df = pd.concat([df, furnishing_dummies], axis=1)
df.drop('furnishingstatus', axis=1, inplace=True)

# Prepare features and target
X = df.drop('price', axis=1)
y = df['price'].values
X_values = X.values.astype(float)

# Normalize features and target
X_mean = X_values.mean(axis=0)
X_std = X_values.std(axis=0)
X_scaled = (X_values - X_mean) / X_std

y_mean = y.mean()
y_std = y.std()
y_scaled = (y - y_mean) / y_std

# Add intercept term
X_b = np.c_[np.ones((X_scaled.shape[0], 1)), X_scaled]

# Hyperparameters
alpha = 0.001
n_iter = 10000

# Initialize parameters
theta = np.zeros(X_b.shape[1])

# Select 10 epochs evenly spaced
checkpoints = np.linspace(1, n_iter, 10, dtype=int).tolist()
theta_history = {}

# Gradient Descent Loop
for epoch in range(n_iter + 1):
    predictions = X_b.dot(theta)
    errors = predictions - y_scaled
    gradients = X_b.T.dot(errors) / len(y_scaled)
    theta -= alpha * gradients

    if epoch in checkpoints:
        theta_history[epoch] = theta.copy()
        mse = np.mean(errors ** 2)
        print(f"Epoch {epoch}: MSE (scaled) = {mse:.6f}")

# Prediction function
def predict(X_raw, theta):
    X_s = (X_raw - X_mean) / X_std
    X_b = np.c_[np.ones((X_s.shape[0], 1)), X_s]
    preds_scaled = X_b.dot(theta)
    return preds_scaled * y_std + y_mean

# Visualization: Regression Line over 'area'
area_idx = X.columns.get_loc('area')
X_mean_values = X.mean(axis=0).values
area_range = np.linspace(df['area'].min(), df['area'].max(), 100)
X_line = np.tile(X_mean_values, (100, 1))

plt.figure(figsize=(12, 7))
plt.scatter(df['area'], y, color='blue', alpha=0.5, label='Actual Prices')

for ep in checkpoints:
    X_line[:, area_idx] = area_range
    predicted_line = predict(X_line, theta_history[ep])
    plt.plot(area_range, predicted_line, label=f'Epoch {ep}')

plt.xlabel('Area')
plt.ylabel('Price')
plt.title('Regression Line on Area at Selected Epochs')
plt.legend()
plt.show()

# Evaluate final model
last_epoch = checkpoints[-1]
predicted_prices = predict(X_values, theta_history[last_epoch])
errors = y - predicted_prices

df['predicted_price'] = predicted_prices
df['error'] = errors

print(df[['price', 'predicted_price', 'error']].head(10))
""",
    6: """# Experiment 6: Polynomial Logistic Regression (Degree-2) with Manual Decision Boundary (No Meshgrid)
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import accuracy_score, confusion_matrix

# LOAD DATA
data = load_breast_cancer()
X = data.data[:, :2]
y = data.target

# NORMALIZE FEATURES
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X = (X - X_mean) / X_std

# POLYNOMIAL FEATURES (DEGREE 2)
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
X_b = np.c_[np.ones((X_poly.shape[0], 1)), X_poly]

# INITIALIZE MODEL
theta = np.zeros(X_b.shape[1])
alpha = 0.1
epochs = 5000

# SIGMOID
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# TRAINING LOOP
for _ in range(epochs):
    z = X_b @ theta
    preds = sigmoid(z)
    errors = preds - y
    gradient = (X_b.T @ errors) / len(y)
    theta -= alpha * gradient

# ACCURACY CHECK
final_preds = (sigmoid(X_b @ theta) >= 0.5).astype(int)
print("Accuracy:", accuracy_score(y, final_preds))
print("Confusion Matrix:\\n", confusion_matrix(y, final_preds))

# DECISION BOUNDARY (NO MESHGRID)
w = theta
x_vals = np.linspace(X[:,0].min()-1, X[:,0].max()+1, 400)
curve_x, curve_y = [], []

for x in x_vals:
    A = w[5]
    B = w[2] + w[4]*x
    C = w[0] + w[1]*x + w[3]*x*x
    disc = B*B - 4*A*C

    if disc >= 0:
        y1 = (-B + np.sqrt(disc)) / (2*A)
        y2 = (-B - np.sqrt(disc)) / (2*A)
        curve_x.append(x); curve_y.append(y1)
        curve_x.append(x); curve_y.append(y2)

# PLOT
plt.scatter(X[:,0], X[:,1], c=y, cmap='bwr', edgecolor='k')
plt.scatter(curve_x, curve_y, s=1, c='black')
plt.title("Polynomial Logistic Regression Decision Boundary (No Meshgrid)")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()""",
    7: """# Experiment 7: Linear vs Sigmoid Neuron on 2-Class Gaussian Data (Decision Boundary Without Meshgrid)
import numpy as np
import matplotlib.pyplot as plt

# Generate 2-class Gaussian Data
np.random.seed(0)
N = 100
mean0 = [-2, -2]
mean1 = [2, 2]
cov = [[1, 0], [0, 1]]

X0 = np.random.multivariate_normal(mean0, cov, N//2)
X1 = np.random.multivariate_normal(mean1, cov, N//2)
X = np.vstack([X0, X1])
y = np.array([0]*(N//2) + [1]*(N//2)).reshape(-1, 1)

# Add bias term
Xb = np.hstack([X, np.ones((N, 1))])

# Sigmoid + derivative
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoid_deriv(a):
    return a * (1 - a)

# Initialize weights
w_lin = np.random.randn(3, 1)
w_sig = np.random.randn(3, 1)

lr = 0.1
epochs = 2000

# Train Linear Neuron
for _ in range(epochs):
    z = Xb @ w_lin
    error = y - z
    grad = (2/N) * (Xb.T @ error)
    w_lin += lr * grad

# Train Sigmoid Neuron
for _ in range(epochs):
    z = Xb @ w_sig
    out = sigmoid(z)
    error = y - out
    delta = error * sigmoid_deriv(out)
    grad = (Xb.T @ delta) / N
    w_sig += lr * grad

# Accuracy Check
lin_pred = (Xb @ w_lin >= 0.5).astype(int)
sig_pred = (sigmoid(Xb @ w_sig) >= 0.5).astype(int)

print("Linear neuron accuracy:", np.mean(lin_pred == y) * 100)
print("Sigmoid neuron accuracy:", np.mean(sig_pred == y) * 100)

# Decision Boundary Without Meshgrid
def plot_boundary_no_mesh(w, title, use_sigmoid=False):
    plt.scatter(X[:,0], X[:,1], c=y.ravel(), cmap='bwr', edgecolor='k')

    w1 = w[0][0]
    w2 = w[1][0]
    b  = w[2][0]

    x_vals = np.linspace(X[:,0].min()-1, X[:,0].max()+1, 200)
    threshold = 0 if use_sigmoid else 0.5

    y_vals = -(w1 * x_vals + b - threshold) / w2
    plt.plot(x_vals, y_vals, 'k--', linewidth=2)

    plt.title(title)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.show()

# Plot Both Boundaries
plot_boundary_no_mesh(w_lin, "Decision Boundary - Linear Neuron")
plot_boundary_no_mesh(w_sig, "Decision Boundary - Sigmoid Neuron", use_sigmoid=True)""",
    8: """# Experiment 8: MNIST Classification using Single-Layer Neural Network (Softmax Classifier)
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

tf.random.set_seed(42)
np.random.seed(42)

# ------------------------------
# 1. Load Data
# ------------------------------
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

x_train = x_train.astype("float32") / 255.0
x_test  = x_test.astype("float32") / 255.0

# ------------------------------
# 2. Build Model
# ------------------------------
model = keras.Sequential([
    layers.Flatten(input_shape=(28, 28)),
    layers.Dense(10, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# ------------------------------
# 3. Train Model
# ------------------------------
history = model.fit(
    x_train, y_train,
    epochs=10,
    batch_size=64,
    validation_data=(x_test, y_test),
    verbose=2
)

# ------------------------------
# 4. Evaluate
# ------------------------------
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print("Test Accuracy:", test_acc)

# ------------------------------
# 5. Plot Accuracy & Loss
# ------------------------------
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(history.history["accuracy"], label="Train Acc")
plt.plot(history.history["val_accuracy"], label="Val Acc")
plt.legend()
plt.title("Accuracy")

plt.subplot(1, 2, 2)
plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Val Loss")
plt.legend()
plt.title("Loss")

plt.tight_layout()
plt.show()

# ------------------------------
# 6. Predictions & Report
# ------------------------------
y_pred = np.argmax(model.predict(x_test), axis=1)
print(classification_report(y_test, y_pred))

# ------------------------------
# 7. Confusion Matrix
# ------------------------------
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.show()

# ------------------------------
# 8. Show Misclassified Images
# ------------------------------
mis_idx = np.where(y_pred != y_test)[0]

plt.figure(figsize=(12, 12))
for i, idx in enumerate(mis_idx[:25]):
    plt.subplot(5, 5, i + 1)
    plt.imshow(x_test[idx], cmap="gray")
    plt.title(f"T:{y_test[idx]}  P:{y_pred[idx]}")
    plt.axis("off")
plt.tight_layout()
plt.show()

# ------------------------------
# 9. Visualize Weights (10 Digits)
# ------------------------------
weights, biases = model.layers[1].get_weights()

plt.figure(figsize=(12, 6))
for i in range(10):
    plt.subplot(2, 5, i + 1)
    plt.imshow(weights[:, i].reshape(28, 28), cmap="coolwarm")
    plt.title(f"Digit {i}")
    plt.axis("off")
plt.tight_layout()
plt.show()""",
    9: """# Experiment 9: Ablation Study on MNIST using Multiple Hidden Layer Architectures

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------
# 1. Load and Preprocess Data
# ------------------------------------------------
def load_data():
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

    x_train = x_train.reshape(-1, 784).astype("float32") / 255.0
    x_test  = x_test.reshape(-1, 784).astype("float32") / 255.0

    y_train = keras.utils.to_categorical(y_train, 10)
    y_test  = keras.utils.to_categorical(y_test, 10)

    return x_train, y_train, x_test, y_test


# ------------------------------------------------
# 2. Create Model
# ------------------------------------------------
def create_model(layers_config):
    model = keras.Sequential()
    model.add(layers.Input(shape=(784,)))

    for units in layers_config:
        model.add(layers.Dense(units, activation="relu"))

    model.add(layers.Dense(10, activation="softmax"))

    model.compile(optimizer="adam",
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
    return model


# ------------------------------------------------
# 3. Run Ablation Experiment
# ------------------------------------------------
def run_experiment():

    x_train, y_train, x_test, y_test = load_data()

    architectures = {
        "0-Layer (Logistic Regression)": [],
        "1-Layer (128)": [128],
        "2-Layer (128, 64)": [128, 64],
        "3-Layer (128, 64, 32)": [128, 64, 32],
        "4-Layer (128, 128, 64, 32)": [128, 128, 64, 32]
    }

    results = {}
    histories = {}
    EPOCHS = 10
    BATCH_SIZE = 128

    for name, config in architectures.items():
        print(f"\\nTraining: {name}")

        model = create_model(config)
        history = model.fit(
            x_train, y_train,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            validation_data=(x_test, y_test),
            verbose=1
        )

        train_acc = model.evaluate(x_train, y_train, verbose=0)[1]
        test_acc  = model.evaluate(x_test,  y_test,  verbose=0)[1]

        results[name] = {
            "Train Accuracy": train_acc,
            "Test Accuracy": test_acc,
            "Generalization Gap": train_acc - test_acc
        }

        histories[name] = history.history

    print("\\n=== Ablation Study Results ===")
    for name, m in results.items():
        print(f"{name}:  Train={m['Train Accuracy']:.4f},  Test={m['Test Accuracy']:.4f},  Gap={m['Generalization Gap']:.4f}")

    plot_results(histories)


# ------------------------------------------------
# 4. Plot Accuracy & Loss
# ------------------------------------------------
def plot_results(histories):

    plt.figure(figsize=(11, 6))
    for name, h in histories.items():
        plt.plot(h['val_accuracy'], label=name)
    plt.title("Validation Accuracy Comparison")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid()
    plt.show()

    plt.figure(figsize=(11, 6))
    for name, h in histories.items():
        plt.plot(h['val_loss'], label=name)
    plt.title("Validation Loss Comparison")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid()
    plt.show()


# ------------------------------------------------
# Main
# ------------------------------------------------
if __name__ == "__main__":
    run_experiment()

""",
    10: """# Experiment 10: CNN on Fashion-MNIST with Evaluation & Visualization

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

tf.random.set_seed(42)
np.random.set_seed(42)

# ------------------------------------------------
# 1. Load & Preprocess Data
# ------------------------------------------------
(x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()

x_train = x_train.astype("float32") / 255.0
x_test  = x_test.astype("float32") / 255.0

x_train = np.expand_dims(x_train, -1)
x_test  = np.expand_dims(x_test, -1)

# ------------------------------------------------
# 2. Build CNN Model
# ------------------------------------------------
model = keras.Sequential([
    layers.Conv2D(32, 3, activation="relu", input_shape=(28,28,1)),
    layers.BatchNormalization(),
    layers.Conv2D(32, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Dropout(0.25),

    layers.Conv2D(64, 3, activation="relu"),
    layers.BatchNormalization(),
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Dropout(0.25),

    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.BatchNormalization(),
    layers.Dropout(0.4),

    layers.Dense(10, activation="softmax")
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# ------------------------------------------------
# 3. Train Model
# ------------------------------------------------
history = model.fit(
    x_train, y_train,
    epochs=15,
    batch_size=128,
    validation_split=0.1,
    verbose=2
)

# ------------------------------------------------
# 4. Model Evaluation
# ------------------------------------------------
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
print(f"Test accuracy: {test_acc:.4f}")

# ------------------------------------------------
# 5. Plot Accuracy & Loss
# ------------------------------------------------
plt.figure(figsize=(12,4))

plt.subplot(1,2,1)
plt.plot(history.history["accuracy"], label="train")
plt.plot(history.history["val_accuracy"], label="val")
plt.title("Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True)

plt.subplot(1,2,2)
plt.plot(history.history["loss"], label="train")
plt.plot(history.history["val_loss"], label="val")
plt.title("Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.show()

# ------------------------------------------------
# 6. Confusion Matrix & Classification Report
# ------------------------------------------------
y_pred = np.argmax(model.predict(x_test), axis=1)

print(classification_report(y_test, y_pred, digits=4))

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=range(10), yticklabels=range(10))
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix")
plt.show()

# ------------------------------------------------
# 7. Display Sample Predictions
# ------------------------------------------------
class_names = [
    "Tshirt/top","Trouser","Pullover","Dress","Coat",
    "Sandal","Shirt","Sneaker","Bag","Ankle boot"
]

plt.figure(figsize=(12,6))
for i in range(12):
    idx = np.random.randint(0, x_test.shape[0])
    plt.subplot(3,4,i+1)
    plt.imshow(x_test[idx].squeeze(), cmap="gray")
    plt.title(f"True: {class_names[y_test[idx]]}\\nPred: {class_names[y_pred[idx]]}")
    plt.axis("off")

plt.tight_layout()
plt.show()

""",
11: """# Experiment 11: Perform dimensionality reduction on the MNIST dataset using PCA and Autoencoders to compare their ability to compress, reconstruct, and preserve essential features of image data for further analysis 

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

tf.random.set_seed(42)
np.random.seed(42)

(x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
x_train = np.expand_dims(x_train, -1)
x_test = np.expand_dims(x_test, -1)

model = keras.Sequential([
    layers.Conv2D(32, 3, activation="relu", input_shape=(28,28,1)),
    layers.BatchNormalization(),
    layers.Conv2D(32, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Dropout(0.25),

    layers.Conv2D(64, 3, activation="relu"),
    layers.BatchNormalization(),
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Dropout(0.25),

    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.BatchNormalization(),
    layers.Dropout(0.4),
    layers.Dense(10, activation="softmax")
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history = model.fit(
    x_train, y_train,
    epochs=15,
    batch_size=128,
    validation_split=0.1,
    verbose=2
)

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
print(f"Test accuracy: {test_acc:.4f}")

plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(history.history["accuracy"], label="train")
plt.plot(history.history["val_accuracy"], label="val")
plt.title("Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True)

plt.subplot(1,2,2)
plt.plot(history.history["loss"], label="train")
plt.plot(history.history["val_loss"], label="val")
plt.title("Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.show()

y_pred = np.argmax(model.predict(x_test), axis=1)
print(classification_report(y_test, y_pred, digits=4))

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=range(10), yticklabels=range(10))
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix")
plt.show()

class_names = ["Tshirt/top","Trouser","Pullover","Dress","Coat",
               "Sandal","Shirt","Sneaker","Bag","Ankle boot"]

plt.figure(figsize=(12,6))
for i in range(12):
    idx = np.random.randint(0, x_test.shape[0])
    plt.subplot(3,4,i+1)
    plt.imshow(x_test[idx].squeeze(), cmap="gray")
    plt.title(f"True: {class_names[y_test[idx]]}\\nPred: {class_names[y_pred[idx]]}")
    plt.axis("off")

plt.tight_layout()
plt.show()
"""



}

def list_experiments():
    return [f"{num}: {code.splitlines()[0]}" for num, code in EXPERIMENTS.items()]

def get_experiment(num: int) -> str:
    return EXPERIMENTS.get(num, "Experiment not found.")
