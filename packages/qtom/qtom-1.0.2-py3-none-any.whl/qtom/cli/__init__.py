"""
Command-line interface for quantum tomography neural network.
"""

from .train import main as train_main
from .evaluate import main as evaluate_main
from .generate_data import main as generate_data_main

__all__ = [
    'train_main',
    'evaluate_main',
    'generate_data_main'
]
