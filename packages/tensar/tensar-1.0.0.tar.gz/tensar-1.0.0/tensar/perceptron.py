"""
Perceptron Implementation - Decision boundary visualization

USAGE:
import tensar
from tensar.perceptron import plot_decision_boundary
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics import confusion_matrix

def plot_decision_boundary(X, y, model, title):
    """
    Plot decision boundary for 2D classification problems
    
    USAGE:
    plot_decision_boundary(X, y, perceptron_model, "Perceptron Decision Boundary")
    """
    plt.figure(figsize=(8, 6))

    # Plot the points
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.bwr, edgecolors='k')

    # Create grid for decision boundary using the original data range
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                        np.linspace(y_min, y_max, 200))

    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.contourf(xx, yy, Z, alpha=0.2, cmap=plt.cm.bwr)
    plt.title(title)
    plt.show()