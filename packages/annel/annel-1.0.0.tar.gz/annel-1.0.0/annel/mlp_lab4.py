"""
MLP Implementation from Lab 4
Usage:
from mlp_lab4 import MLP_2_2_1

# XOR problem
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

mlp = MLP_2_2_1()
mlp.train(X, y, epochs=10000, learning_rate=0.1)

predictions = mlp.predict(X)
print("Predictions:", predictions)
"""

import numpy as np
import matplotlib.pyplot as plt

class MLP_2_2_1:
    def __init__(self):
        # Define weights and biases for a 2->2->1 MLP
        self.weights_input_hidden = np.random.randn(2, 2)
        self.bias_hidden = np.zeros((1, 2))
        self.weights_hidden_output = np.random.randn(2, 1)
        self.bias_output = np.zeros((1, 1))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        # Compute z1 (hidden layer input)
        self.z1 = np.dot(X, self.weights_input_hidden) + self.bias_hidden

        # Compute a1 (hidden layer output)
        self.a1 = self.sigmoid(self.z1)

        # Compute z2 (output layer input)
        self.z2 = np.dot(self.a1, self.weights_hidden_output) + self.bias_output

        # Compute ŷ (output layer output)
        self.ŷ = self.sigmoid(self.z2)
        return self.ŷ

    def backward(self, X, y, output, learning_rate):
        # Compute the error (E) at the output layer
        output_error = output - y

        # Compute the gradient for the output layer weights and biases
        delta_output = output_error * self.sigmoid_derivative(output)
        d_weights_hidden_output = np.dot(self.a1.T, delta_output)
        d_bias_output = np.sum(delta_output, axis=0, keepdims=True)

        # Compute the error at the hidden layer
        hidden_error = np.dot(delta_output, self.weights_hidden_output.T) * self.sigmoid_derivative(self.a1)

        # Compute the gradient for the hidden layer weights and biases
        d_weights_input_hidden = np.dot(X.T, hidden_error)
        d_bias_hidden = np.sum(hidden_error, axis=0, keepdims=True)

        # Update weights and biases
        self.weights_hidden_output -= learning_rate * d_weights_hidden_output
        self.bias_output -= learning_rate * d_bias_output
        self.weights_input_hidden -= learning_rate * d_weights_input_hidden
        self.bias_hidden -= learning_rate * d_bias_hidden

    def train(self, X, y, epochs, learning_rate):
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, output, learning_rate)
            if (epoch+1) % 1000 == 0:
                # Compute and print the Mean Squared Error (MSE)
                loss = np.mean((y - output)**2)
                print(f'Epoch {epoch+1}, Loss: {loss:.4f}')

    def predict(self, X):
        return self.forward(X)

# Example usage
if __name__ == "__main__":
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([[0], [1], [1], [0]])

    mlp = MLP_2_2_1()

    epochs = 10000
    learning_rate = 0.1
    mlp.train(X, y, epochs, learning_rate)

    predictions = mlp.predict(X)
    print("\nPredictions after training:")
    print(predictions)

    print("\nValidation (comparing predicted output with actual output):")
    print(np.round(predictions))