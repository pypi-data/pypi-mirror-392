"""
PyTorch Basics from Lab 1
Usage:
from torch_basics_lab1 import create_tensors, basic_operations, reshape_tensor, compute_gradients

# Create tensors
tensors = create_tensors()

# Basic operations
results = basic_operations()

# Reshape tensor
reshaped = reshape_tensor()

# Compute gradients
grad = compute_gradients()
"""

import torch
from torch.autograd import grad
import matplotlib.pyplot as plt
import numpy as np

def create_tensors():
    """Create different types of tensors"""
    print("\nCreating Tensors")
    
    # Scalar
    t1 = torch.tensor(3)
    print("\nScaler Tensor:", t1)
    
    # Vector
    t2 = torch.tensor([1, 2, 3, 4])
    print("\nVector Tensor:", t2)
    
    # 3x3 Matrix
    t3 = torch.rand(3, 3)
    print("\n3x3 Matrix Tensor:", t3)
    
    # 3D Tensor (2x3x4)
    t4 = torch.rand(2, 3, 4)
    print("\n3D Tensor (2x3x4):\n", t4)
    
    return {'scalar': t1, 'vector': t2, 'matrix': t3, '3d_tensor': t4}

def basic_operations():
    """Perform basic tensor operations"""
    a = torch.tensor([[1., 2.], [4., 5.]])
    b = torch.tensor([[7., 8.], [10., 11.]])
    
    # Addition
    sum_result = a + b
    print("Addition:\n", sum_result)
    
    # Multiplication
    mul_result = a * b
    print("Multiplication:\n", mul_result)
    
    # Matrix Multiplication
    matmul_result = torch.matmul(a, b)
    print("Matrix Multiplication:\n", matmul_result)
    
    # Mean
    mean_a = torch.mean(a)
    print("Mean 1st:\n", mean_a)
    
    mean_b = torch.mean(b)
    print("Mean 2nd:\n", mean_b)
    
    # Sum
    sum_a = torch.sum(a)
    print("Matrix Sum 1st:\n", sum_a)
    
    sum_b = torch.sum(b)
    print("Matrix Sum 2nd:\n", sum_b)
    
    return {
        'addition': sum_result,
        'multiplication': mul_result, 
        'matrix_mul': matmul_result,
        'mean_a': mean_a,
        'mean_b': mean_b,
        'sum_a': sum_a,
        'sum_b': sum_b
    }

def reshape_tensor():
    """Reshape a 1D tensor into different shapes"""
    print("\n--- Reshaping Tensors ---")
    tensor_1d = torch.arange(12)
    print("Original 1D tensor (12 elements):", tensor_1d)
    
    # Reshape to 3x4
    reshaped_3x4 = tensor_1d.reshape(3, 4)
    print("Reshaped to 3x4:\n", reshaped_3x4)
    
    # Reshape to 2x6
    reshaped_2x6 = tensor_1d.reshape(2, 6)
    print("Reshaped to 2x6:\n", reshaped_2x6)
    
    return {
        'original': tensor_1d,
        '3x4': reshaped_3x4,
        '2x6': reshaped_2x6
    }

def compute_gradients():
    """Compute gradients using autograd"""
    print("\n--- Computing Gradients (Autograd) ---")
    
    # PyTorch Autograd
    x_pt = torch.tensor(3.0, requires_grad=True)
    y_pt = x_pt**2
    y_pt.backward()  # Compute gradient
    
    gradient = x_pt.grad.item()
    print(f"PyTorch: Gradient of y = x^2 at x = {x_pt.item()} is dy/dx = {gradient}")
    
    return gradient

def check_gpu():
    """Check if GPU is available"""
    if torch.cuda.is_available():
        print("GPU is available.")
        return True
    else:
        print("GPU is not available.")
        return False

# Example usage
if __name__ == "__main__":
    # Check PyTorch version and GPU
    print("Pytorch Version:", torch.__version__)
    check_gpu()
    
    # Create tensors
    tensors = create_tensors()
    
    # Basic operations
    operations = basic_operations()
    
    # Reshape tensor
    reshaped = reshape_tensor()
    
    # Compute gradients
    gradient = compute_gradients()