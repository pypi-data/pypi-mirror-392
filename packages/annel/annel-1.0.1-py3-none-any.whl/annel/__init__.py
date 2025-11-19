"""
ANN & DL Labs - A collection of neural network implementations from lab assignments
"""

__version__ = "1.0.1"
__author__ = "Sameer Rizwan"
__email__ = "xie19113@gmail.com"

# Import all modules so they can be accessed directly
from . import adaline_lab3
from . import mlp_lab4
from . import cnn_lab5
from . import perceptron_lab2
from . import filters_lab6
from . import torch_basics_lab1

# Also import main functions for convenience
from .adaline_lab3 import ADALINE, from01, to01, print_metrics, plot_decision_boundary_2d, generate_synthetic_data
from .mlp_lab4 import MLP_2_2_1
from .cnn_lab5 import FashionCNN, DeepCNN, train_model, load_fashion_mnist
from .perceptron_lab2 import plot_decision_boundary
from .filters_lab6 import apply_filters, plot_filter_results, load_and_preprocess_image
from .torch_basics_lab1 import create_tensors, basic_operations, reshape_tensor, compute_gradients, check_gpu

__all__ = [
    # Modules
    'adaline_lab3', 'mlp_lab4', 'cnn_lab5', 'perceptron_lab2', 'filters_lab6', 'torch_basics_lab1',
    
    # ADALINE Lab 3
    'ADALINE', 'from01', 'to01', 'print_metrics', 'plot_decision_boundary_2d', 'generate_synthetic_data',
    
    # MLP Lab 4
    'MLP_2_2_1',
    
    # CNN Lab 5
    'FashionCNN', 'DeepCNN', 'train_model', 'load_fashion_mnist',
    
    # Perceptron Lab 2
    'plot_decision_boundary',
    
    # Filters Lab 6
    'apply_filters', 'plot_filter_results', 'load_and_preprocess_image',
    
    # Torch Basics Lab 1
    'create_tensors', 'basic_operations', 'reshape_tensor', 'compute_gradients', 'check_gpu'
]