import numpy as np
from numpy import linalg as la
import os
from .povm import generate_POVM, load_fixed_povm
from .state_representation import density_to_cholesky, cholesky_to_density
from .random_states import random_HS_state, haar_random_state


def get_probabilities(rho, povm_elements):
    """Calculate probabilities Tr(rho * E_i) for all POVM elements."""
    probs = np.array([np.real(np.trace(rho @ E)) for E in povm_elements])
    probs /= np.sum(probs)
    return probs

def sample_measurements(probabilities, trials):
    """Sample measurement outcomes using multinomial distribution."""
    return np.random.multinomial(trials, probabilities)

def generate_sampling_distribution(max_count=100000):
    """Generate cube-root sampling distribution for number of trials."""
    l = np.cbrt(np.arange(1, max_count + 1))
    pl = l / np.sum(l)
    return pl

def sample_num_trials(dim, sampling_dist):
    """Sample number of trials from the cube-root distribution."""
    idx = np.random.choice(len(sampling_dist), p=sampling_dist)
    return dim**2 + idx

def generate_dataset(dim, num_states, sampled_fraction=0.25, use_fixed_povm=True):
    """Generate dataset with FIXED POVM and cube-root sampling distribution."""
    povm = load_fixed_povm(dim) if use_fixed_povm else generate_POVM(dim)
    sampling_dist = generate_sampling_distribution()

    data_probs = []
    labels = []

    for i in range(num_states):
        if i % 10000 == 0:
            print(f"  Generated {i}/{num_states} states...")

        rho = random_HS_state(dim)
        probs = get_probabilities(rho, povm)

        if np.random.rand() < (1 - sampled_fraction):
            data_probs.append(probs)
        else:
            trials = sample_num_trials(dim, sampling_dist)
            counts = sample_measurements(probs, trials)
            data_probs.append(counts / trials)

        labels.append(rho)

    return np.array(data_probs), np.array(labels)
