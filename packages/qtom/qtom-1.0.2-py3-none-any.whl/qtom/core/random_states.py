"""
Random state generation utilities to break circular imports.
"""

import numpy as np
from numpy import linalg as la

def haar_random_state(dim):
    """Generate a Haar-distributed random pure state vector."""
    vec = np.random.randn(dim) + 1j * np.random.randn(dim)
    vec /= la.norm(vec)
    return vec

def random_HS_state(dim):
    """Generate a random density matrix from the Hilbert-Schmidt ensemble."""
    X = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
    rho = X @ X.conj().T
    rho /= np.trace(rho)
    return rho
