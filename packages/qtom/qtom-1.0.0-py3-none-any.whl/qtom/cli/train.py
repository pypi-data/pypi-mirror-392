import os
import numpy as np
import keras
from ..core.povm import generate_fixed_povm, save_povm
from ..core.data_generation import generate_dataset
from ..core.state_representation import density_to_cholesky
from ..models.training import train_model
from ..evaluation.metrics import evaluate_model

def setup_povms(dimensions, data_dir='data'):
    """Generate and save fixed POVMs for all dimensions."""
    print("Generating fixed POVMs...")
    os.makedirs(data_dir, exist_ok=True)
    
    for d in dimensions:
        povm_file = f'{data_dir}/SRMpom{d}.npz'
        if not os.path.exists(povm_file):
            povm = generate_fixed_povm(d)
            save_povm(povm, d, data_dir)
        else:
            print(f"POVM for d={d} already exists, skipping...")

def prepare_training_data(dimensions, data_dir='data'):
    """Prepare training data for all dimensions."""
    print("Generating training data...")
    
    for d in dimensions:
        print(f"Generating data for dimension {d}...")
        
        train_probs, train_rho = generate_dataset(d, num_states=750000,
                                                 sampled_fraction=0.25,
                                                 use_fixed_povm=True)
        val_probs, val_rho = generate_dataset(d, num_states=250000,
                                             sampled_fraction=0.25,
                                             use_fixed_povm=True)

        train_cholesky = density_to_cholesky(train_rho)
        val_cholesky = density_to_cholesky(val_rho)

        combined_probs = np.concatenate([train_probs, val_probs])
        combined_cholesky = np.concatenate([train_cholesky, val_cholesky])

        indices = np.random.permutation(len(combined_probs))
        combined_probs = combined_probs[indices]
        combined_cholesky = combined_cholesky[indices]

        split_idx = int(0.8 * len(combined_probs))

        filename = f'{data_dir}/quantum_training_data_d{d}.npz'
        np.savez_compressed(
            filename,
            train_input=combined_probs[:split_idx],
            train_output=combined_cholesky[:split_idx],
            val_input=combined_probs[split_idx:],
            val_output=combined_cholesky[split_idx:],
        )
        print(f"Saved to {filename}")

def train_models(dimensions, data_dir='data', model_dir='models'):
    """Train models for all dimensions."""
    print("Training models...")
    os.makedirs(model_dir, exist_ok=True)
    
    for d in dimensions:
        print(f"Training model for dimension {d}")
        data_file = f'{data_dir}/quantum_training_data_d{d}.npz'
        model_path = f'{model_dir}/best_model_d{d}.h5'
        train_model(d, data_file, model_path)

def main():
    """Main training pipeline."""
    dimensions = [2, 5, 7]
    
    setup_povms(dimensions)
    prepare_training_data(dimensions)
    train_models(dimensions)
    
    print("Training pipeline complete!")

if __name__ == "__main__":
    main()
