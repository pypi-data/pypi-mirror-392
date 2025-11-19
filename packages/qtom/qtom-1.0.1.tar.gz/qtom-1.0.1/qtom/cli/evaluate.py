import os
import numpy as np
import keras
from ..evaluation.metrics import evaluate_model

def main():
    """Run evaluation using existing trained models."""
    dimensions = [2, 5, 7]
    os.makedirs('results', exist_ok=True)
    
    print("MODEL EVALUATION (Using Existing Trained Models)")
    
    all_results = {}
    
    for d in dimensions:
        print(f"Evaluating model for dimension {d}")
        
        model_path = f'models/best_model_d{d}.h5'
        
        if not os.path.exists(model_path):
            print(f"ERROR: Model {model_path} not found! Skipping...")
            continue
        
        print(f"Loading model from {model_path}...")
        model = keras.models.load_model(model_path, compile=False)
        
        print("Running evaluation...")
        results = evaluate_model(model, d, test_size=10000)
        all_results[d] = results
        
        print(f"Summary for d={d}:")
        for trials in [10, 100, 1000, 10000, 100000]:
            if trials in results:
                hs = results[trials]['mean_hs_distance']
                pos = results[trials]['percent_positive']
                print(f"  {trials:6d} trials: HS={hs:.4f}, Positive={pos:.1f}%")
    
    results_file = 'results/evaluation_results.txt'
    print(f"Saving results to {results_file}...")
    
    with open(results_file, 'w') as f:
        for d in dimensions:
            if d not in all_results:
                continue
                
            f.write(f"Results for dimension {d}\n")
            for trials, metrics in all_results[d].items():
                f.write(f"\nTrials: {trials}\n")
                f.write(f"  Mean HS distance: {metrics['mean_hs_distance']:.6f}\n")
                f.write(f"  Std HS distance: {metrics['std_hs_distance']:.6f}\n")
                f.write(f"  Positive states: {metrics['percent_positive']:.1f}%\n")
    
    print("Evaluation complete!")

if __name__ == "__main__":
    main()
