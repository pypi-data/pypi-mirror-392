"""
I/O utilities for quantum tomography neural network.
"""

import os
import numpy as np

def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)
    return directory

def save_training_data(data_dict, filename):
    """Save training data to NPZ file."""
    np.savez_compressed(filename, **data_dict)
    print(f"Saved training data to {filename}")

def load_training_data(filename):
    """Load training data from NPZ file."""
    data = np.load(filename)
    return data

def save_results(results, filename, dimensions=None):
    """Save evaluation results to text file."""
    with open(filename, 'w') as f:
        if dimensions:
            for d in dimensions:
                if d in results:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"Results for dimension {d}\n")
                    f.write('='*60 + '\n')
                    for trials, metrics in results[d].items():
                        f.write(f"\nTrials: {trials}\n")
                        f.write(f"  Mean HS distance: {metrics['mean_hs_distance']:.6f}\n")
                        f.write(f"  Std HS distance: {metrics['std_hs_distance']:.6f}\n")
                        f.write(f"  Positive states: {metrics['percent_positive']:.1f}%\n")
        else:
            # Generic results saving
            import json
            # Convert numpy types to Python types for JSON serialization
            json_results = {}
            for key, value in results.items():
                if hasattr(value, 'item'):  # Convert numpy types
                    json_results[key] = value.item()
                else:
                    json_results[key] = value
            json.dump(json_results, f, indent=2)
    
    print(f"Results saved to {filename}")
