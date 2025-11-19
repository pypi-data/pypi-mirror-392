"""
MLP Implementation - Multi-Layer Perceptron for XOR problem

USAGE:
import tensar
from tensar.mlp import MLP_2_2_1
"""

import numpy as np
import matplotlib.pyplot as plt

class MLP_2_2_1:
    def __init__(self):
        self.weights_input_hidden = np.random.randn(2, 2)
        self.bias_hidden = np.zeros((1, 2))
        self.weights_hidden_output = np.random.randn(2, 1)
        self.bias_output = np.zeros((1, 1))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        self.z1 = np.dot(X, self.weights_input_hidden) + self.bias_hidden
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.weights_hidden_output) + self.bias_output
        self.ŷ = self.sigmoid(self.z2)
        return self.ŷ

    def backward(self, X, y, output, learning_rate):
        output_error = output - y
        delta_output = output_error * self.sigmoid_derivative(output)
        d_weights_hidden_output = np.dot(self.a1.T, delta_output)
        d_bias_output = np.sum(delta_output, axis=0, keepdims=True)
        hidden_error = np.dot(delta_output, self.weights_hidden_output.T) * self.sigmoid_derivative(self.a1)
        d_weights_input_hidden = np.dot(X.T, hidden_error)
        d_bias_hidden = np.sum(hidden_error, axis=0, keepdims=True)
        self.weights_hidden_output -= learning_rate * d_weights_hidden_output
        self.bias_output -= learning_rate * d_bias_output
        self.weights_input_hidden -= learning_rate * d_weights_input_hidden
        self.bias_hidden -= learning_rate * d_bias_hidden

    def train(self, X, y, epochs, learning_rate):
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, output, learning_rate)
            if (epoch+1) % 1000 == 0:
                loss = np.mean((y - output)**2)
                print(f'Epoch {epoch+1}, Loss: {loss:.4f}')

    def predict(self, X):
        return self.forward(X)