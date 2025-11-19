"""
Command-line interface for generating quantum tomography data.
"""

import os
import numpy as np
from math import floor
from ..core.povm import generate_fixed_povm, save_povm
from ..core.data_generation import generate_dataset
from ..core.state_representation import density_to_cholesky
from ..utils.io import ensure_directory, save_training_data

def generate_povms(dimensions, num_states = 100000, data_dir='data'):
    """Generate and save fixed POVMs for specified dimensions."""
    print("Generating fixed POVMs...")
    ensure_directory(data_dir)

    train_num_states = floor(num_states*.75)
    val_num_states = floor(num_states*.25)
    
    for d in dimensions:
        povm_file = f'{data_dir}/SRMpom{d}.npz'
        if not os.path.exists(povm_file):
            print(f"Generating POVM for dimension {d}...")
            povm = generate_fixed_povm(d)
            save_povm(povm, d, data_dir)
        else:
            print(f"POVM for d={d} already exists, skipping...")

def generate_training_data(dimensions, num_states = 100000, data_dir='data'):
    """Generate training data for specified dimensions."""
    print("Generating training data...")

    train_num_states = floor(num_states*.75)
    val_num_states = floor(num_states*.25)
    
    for d in dimensions:
        print(f"Generating data for dimension {d}...")
        
        # Generate training and validation datasets
        train_probs, train_rho = generate_dataset(
            d, num_states=train_num_states, sampled_fraction=0.25, use_fixed_povm=True
        )
        val_probs, val_rho = generate_dataset(
            d, num_states=val_num_states, sampled_fraction=0.25, use_fixed_povm=True
        )

        # Convert to Cholesky representation
        train_cholesky = density_to_cholesky(train_rho)
        val_cholesky = density_to_cholesky(val_rho)

        # Combine and shuffle datasets
        combined_probs = np.concatenate([train_probs, val_probs])
        combined_cholesky = np.concatenate([train_cholesky, val_cholesky])

        indices = np.random.permutation(len(combined_probs))
        combined_probs = combined_probs[indices]
        combined_cholesky = combined_cholesky[indices]

        # Split 80/20 for train/validation
        split_idx = int(0.8 * len(combined_probs))

        # Prepare data dictionary
        data_dict = {
            'train_input': combined_probs[:split_idx],
            'train_output': combined_cholesky[:split_idx],
            'val_input': combined_probs[split_idx:],
            'val_output': combined_cholesky[split_idx:],
        }

        # Save data
        filename = f'{data_dir}/quantum_training_data_d{d}.npz'
        save_training_data(data_dict, filename)

def main():
    """Main function for data generation CLI."""
    dimensions = [2, 5, 7]
    
    print("=" * 60)
    print("QUANTUM TOMOGRAPHY DATA GENERATION")
    print("=" * 60)
    
    # Generate POVMs
    generate_povms(dimensions)
    
    # Generate training data
    generate_training_data(dimensions)
    
    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
