"""
ADALINE Implementation - Adaptive Linear Neuron for binary classification

USAGE:
import tensar
from tensar.adaline import ADALINE

# Generate data
X, y = tensar.adaline.generate_synthetic_data()

# Or use directly
X, y = generate_synthetic_data()
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

class ADALINE:
    def __init__(self, lr=0.01, epochs=50):
        self.lr = lr
        self.epochs = epochs
        self.w = None
        self.b = 0.0
        self.sse_history_ = []
    
    def fit(self, X, y_pm1):
        x = np.asarray(X, dtype=float)
        n_features = X.shape[1]
        self.w = np.random.randn(n_features) * 0.01
        self.b = 0.0
        self.sse_history_ = []
        for _ in range(self.epochs):
            sse = 0.0
            for xi, yi in zip(X, y_pm1):
                z = np.dot(self.w, xi) + self.b
                a = z
                e = yi - a

                self.w += self.lr * e * xi
                self.b += self.lr * e
                sse += e**2
            self.sse_history_.append(sse)
        return self
    
    def net_input(self, X):
        X = np.asarray(X, dtype=float)
        return X @ self.w + self.b

    def predict_linear(self, X):
        return self.net_input(X)

    def predict_labels(self, X):
        z = self.net_input(X)
        return np.where(z >= 0.0, 1, -1)

def to01(y_pm1):
    y_pm1 = np.asarray(y_pm1).ravel()
    return ((y_pm1 + 1) / 2).astype(int)

def from01(y01):
    y01 = np.asarray(y01).ravel()
    return np.where(y01 == 1, 1, -1)

def print_metrics(y_true, y_pred, split_name="Dataset"):
    y_true_01 = to01(y_true)
    y_pred_01 = to01(y_pred)
    
    acc = accuracy_score(y_true_01, y_pred_01)
    cm = confusion_matrix(y_true_01, y_pred_01)
    prec = precision_score(y_true_01, y_pred_01, zero_division=0)
    rec = recall_score(y_true_01, y_pred_01, zero_division=0)
    f1 = f1_score(y_true_01, y_pred_01, zero_division=0)
    
    print(f"=== {split_name} Metrics ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"Confusion Matrix:\n{cm}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")

def plot_decision_boundary_2d(model, X, y, title="Decision Boundary"):
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                        np.linspace(y_min, y_max, 200))
    
    Z = model.predict_labels(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
    plt.contourf(xx, yy, Z, alpha=0.8)
    plt.scatter(X[:, 0], X[:, 1], c=to01(y), edgecolors='k', marker='o')
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.title(title)
    plt.show()

def generate_synthetic_data(n_per_class=128, random_state=42):
    rng = np.random.default_rng(random_state)
    X0 = rng.multivariate_normal([0.0, 0.0], [[0.25, 0.00],[0.00, 0.25]], size=n_per_class)
    X1 = rng.multivariate_normal([2.0, 2.0], [[0.25, 0.00],[0.00, 0.25]], size=n_per_class)
    X = np.vstack([X0, X1])
    y01 = np.hstack([np.zeros(n_per_class, dtype=int), np.ones(n_per_class, dtype=int)])
    return X, y01