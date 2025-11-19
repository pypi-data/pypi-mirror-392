import numpy as np
from ..core.data_generation import get_probabilities, sample_measurements
from ..core.povm import load_fixed_povm
from ..core.random_states import random_HS_state  # Changed import
from ..core.state_representation import cholesky_to_density

def hilbert_schmidt_distance(rho_true, rho_pred):
    """Calculate Hilbert-Schmidt distance between two density matrices."""
    diff = rho_true - rho_pred
    return np.sqrt(np.real(np.trace(diff @ diff.conj().T)))

def generate_test_data(dim, num_states, trials):
    """Generate test data with fixed number of trials using fixed POVM."""
    povm = load_fixed_povm(dim)
    test_probs = []
    test_rho = []

    print(f"  Generating {num_states} test states with {trials} trials...")
    for _ in range(num_states):
        rho = random_HS_state(dim)
        probs = get_probabilities(rho, povm)
        counts = sample_measurements(probs, trials)
        sampled_probs = counts / trials

        test_probs.append(sampled_probs)
        test_rho.append(rho)

    return np.array(test_probs), np.array(test_rho)

def evaluate_model(model, dim, test_size=10000, trial_range=[10, 100, 1000, 10000, 100000]):
    """Evaluate model following the paper's methodology."""
    results = {}

    for trials in trial_range:
        print(f"\nEvaluating with {trials} trials...")

        test_probs, test_rho = generate_test_data(dim, test_size, trials)
        pred_cholesky = model.predict(test_probs, batch_size=100, verbose=0)

        hs_distances = []
        num_positive = 0
        min_eigenvalues = []

        for i in range(test_size):
            rho_pred = cholesky_to_density(pred_cholesky[i], dim)

            hs_dist = hilbert_schmidt_distance(test_rho[i], rho_pred)
            hs_distances.append(hs_dist)

            eigenvalues = np.linalg.eigvalsh(rho_pred)
            min_eig = np.min(eigenvalues)
            min_eigenvalues.append(min_eig)

            if min_eig >= -1e-10:
                num_positive += 1

        results[trials] = {
            'mean_hs_distance': np.mean(hs_distances),
            'std_hs_distance': np.std(hs_distances),
            'percent_positive': 100 * num_positive / test_size,
            'min_eigenvalue': np.mean(min_eigenvalues)
        }

        print(f"  Mean HS distance: {results[trials]['mean_hs_distance']:.6f}")
        print(f"  Positive states: {results[trials]['percent_positive']:.1f}%")

    return results
