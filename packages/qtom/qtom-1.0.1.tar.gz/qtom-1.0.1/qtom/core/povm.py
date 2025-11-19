import numpy as np
from numpy import linalg as la
import os
from .random_states import haar_random_state

def generate_POVM(dim):
    """Generate square root POVM elements based on Haar random states."""
    povm_states = [haar_random_state(dim) for _ in range(dim**2)]
    povm_elements = [np.outer(state, state.conj()) for state in povm_states]
    return povm_elements

def generate_fixed_povm(dim):
    """Generate a fixed square root POVM (SRM - Square Root Measurement)."""
    print(f"Generating fixed POVM for dimension {dim}...")
    
    povm_states = []
    for _ in range(dim**2):
        state = haar_random_state(dim)
        povm_states.append(np.outer(state, state.conj()))
    
    povm_states = np.array(povm_states)
    
    # Compute square root POVM: E_i = S^{-1/2} |psi_i><psi_i| S^{-1/2}
    S_op = np.sum(povm_states, axis=0)
    
    eigenvalues, eigenvectors = la.eigh(S_op)
    S_sqrt_inv = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.conj().T
    
    povm = np.array([S_sqrt_inv @ povm_states[i] @ S_sqrt_inv for i in range(dim**2)])
    
    return povm

def save_povm(povm, dim, data_dir='data'):
    """Save POVM to file."""
    os.makedirs(data_dir, exist_ok=True)
    filename = f'{data_dir}/SRMpom{dim}.npz'
    np.savez(filename, povm=povm)
    print(f"Saved POVM to {filename}")

def load_fixed_povm(dim, data_dir='data'):
    """Load the pre-generated fixed POVM."""
    filename = f'{data_dir}/SRMpom{dim}.npz'
    if not os.path.exists(filename):
        raise FileNotFoundError(f"POVM file {filename} not found.")
    data = np.load(filename)
    return data['povm']
