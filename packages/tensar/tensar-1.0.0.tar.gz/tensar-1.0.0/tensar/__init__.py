"""
Tensar - A collection of neural network implementations from ANN & DL lab assignments
"""

__version__ = "1.0.0"
__author__ = "Sameer Rizwan"
__email__ = "xie19113@gmail.com"

# Import all modules to make them accessible as tensar.module_name
from . import adaline
from . import mlp 
from . import cnn
from . import perceptron
from . import filters
from . import torch_basics

# Also import main classes/functions to top level for convenience
from .adaline import ADALINE, from01, to01, print_metrics, plot_decision_boundary_2d, generate_synthetic_data
from .mlp import MLP_2_2_1
from .cnn import FashionCNN, DeepCNN, train_model, load_fashion_mnist
from .perceptron import plot_decision_boundary
from .filters import apply_filters, plot_filter_results, load_and_preprocess_image
from .torch_basics import create_tensors, basic_operations, reshape_tensor, compute_gradients, check_gpu

__all__ = [
    # Modules
    'adaline', 'mlp', 'cnn', 'perceptron', 'filters', 'torch_basics',
    
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