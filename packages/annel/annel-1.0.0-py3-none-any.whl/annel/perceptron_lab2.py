"""
Perceptron Implementation from Lab 2
Usage:
from perceptron_lab2 import plot_decision_boundary

# Train perceptron
p = Perceptron(random_state=42)
p.fit(X_train, y_train)

# Plot decision boundary
plot_decision_boundary(X, y, p, "Perceptron Decision Boundary")
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

# Example usage
if __name__ == "__main__":
    # Step 1: Generate a 2D synthetic dataset
    X, y = make_blobs(n_samples=500, centers=2, random_state=42, cluster_std=1.5)

    plt.figure(figsize=(8, 6))
    plt.scatter(X[:, 0], X[:, 1], c=y, edgecolors='k', marker='o')
    plt.xlabel('CGPA')
    plt.ylabel('Resume Score')
    plt.title('Placement Data')
    plt.show()

    # Step 2: Train a perceptron classifier
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    p = Perceptron(random_state=42)
    p.fit(X_train, y_train)

    pre = p.predict(X_test)

    # Step 3: Plot decision boundary and samples
    plot_decision_boundary(X, y, p, "Perceptron Decision Boundary")

    accuracy = p.score(X_test, y_test)
    print(f"Accuracy: {accuracy}")

    # Confusion matrix
    cm = confusion_matrix(y_test, pre)
    plt.figure(figsize=(8,8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                xticklabels=['Predicted 0','Predicted 1'],
                yticklabels=['Actual 0','Actual 1'])
    plt.xlabel('Predicted')
    plt.ylabel('Truth')
    plt.title('Confusion Matrix')
    plt.show()