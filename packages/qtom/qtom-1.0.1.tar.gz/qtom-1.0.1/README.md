# Quantum Tomography Neural Network Library

A Python library for neural network-based quantum state tomography, implementing the methods from the paper ["Neural-network quantum state tomography"](https://arxiv.org/abs/2206.06736) by Koutný et al.

## The Problem: Quantum State Tomography

### Mathematical Foundation

In quantum mechanics, a quantum state is described by a **density matrix** $\rho$, which is a positive semidefinite matrix with unit trace ($\text{Tr}(\rho) = 1$). For a d-dimensional quantum system, $\rho$ is a $d \times d$ complex matrix.

The goal of quantum state tomography is to reconstruct this unknown density matrix $\rho$ from experimental measurements. According to Born's rule, the probability of obtaining measurement outcome $i$ is:

$$
p_i = \text{Tr}(\rho \Pi_i)
$$

where $\{\Pi_i\}$ forms a Positive Operator-Valued Measure (POVM) satisfying:
- $\Pi_i \geq 0$ (positive semidefinite)
- $\sum_i \Pi_i = I$ (completeness)

### The Challenge

Traditional tomography methods face several challenges:

1. **Positivity constraint**: Reconstructed states must be physically valid (positive semidefinite)
2. **Noise sensitivity**: Real measurements have finite statistics and noise
3. **Computational cost**: Maximum likelihood estimation can be slow for large systems

## Our Solution: Neural Network Approach

We implement a deep neural network that learns the inverse mapping from measurement probabilities to density matrices:

$$
f: [p_1, p_2, \ldots, p_{d^2}] \rightarrow \rho
$$

### Mathematical Details

#### Cholesky Decomposition
Any density matrix can be written as:

$$
\rho = \frac{LL^\dagger}{\text{Tr}(LL^\dagger)}
$$

where $L$ is lower triangular with:
- Real diagonal elements
- Complex off-diagonal elements

This representation has exactly $d^2$ real parameters and automatically ensures $\rho$ is positive semidefinite.

#### Hilbert-Schmidt Distance
The reconstruction quality is measured by:

$$
D_{HS}(\rho, \sigma) = \sqrt{\text{Tr}((\rho-\sigma)^2)}
$$

which quantifies the distance between true state $\rho$ and reconstructed state $\sigma$.

#### Square-Root Measurements
The POVM elements are constructed as:

$$
\Pi_i = S^{-1/2} |\psi_i\rangle\langle\psi_i| S^{-1/2}
$$

where $S = \sum_i |\psi_i\rangle\langle\psi_i|$ and $\{|\psi_i\rangle\}$ are Haar-random states.

## Installation

```bash
git clone https://github.com/yourusername/quantum-tomography-nn
cd quantum-tomography-nn
pip install -e .
```

### Quick Start

```python

#!/usr/bin/env python3
"""
Proper minimal example using library functions correctly.
"""

import numpy as np
import os
from quantum_tomography_nn.cli.generate_data import generate_povms, generate_training_data
from quantum_tomography_nn.models.training import train_model
from quantum_tomography_nn.core.random_states import random_HS_state
from quantum_tomography_nn.evaluation.metrics import hilbert_schmidt_distance

# Generate POVM and data
generate_povms([2], num_states=1000)
generate_training_data([2], num_states=1000)

# Train the model
model, history = train_model(2, 'data/quantum_training_data_d2.npz', 'models/demo_model.h5')

# Test
from quantum_tomography_nn.core.data_generation import get_probabilities, sample_measurements
from quantum_tomography_nn.core.state_representation import cholesky_to_density
import keras

#model = keras.models.load_model('models/demo_model.h5', compile=False)
povm = np.load('data/SRMpom2.npz')['povm']

test_rho = random_HS_state(2)
probs = sample_measurements(get_probabilities(test_rho, povm), 1000) / 1000
pred = cholesky_to_density(model.predict(probs.reshape(1,-1), verbose=0)[0], 2)

print(f"Reconstruction error: {hilbert_schmidt_distance(test_rho, pred):.4f}")
print("True state:\n", np.round(test_rho, 3))
print("Predicted state:\n", np.round(pred, 3))
```

### Example Explanation

This minimal example demonstrates the complete workflow:

* POVM Generation: Creates a fixed set of measurement operators using generate_povms([2], num_states=1000)

* Generation: Generates random quantum states and their measurement statistics using generate_training_data([2], num_states=1000)

* Network Training: Learns the mapping from probabilities to states using train_model()

* Reconstruction: Uses the trained network to predict unknown states from new measurements

* Evaluation: Compares true vs predicted states using Hilbert-Schmidt distance

The neural network automatically learns to produce physically valid density matrices while being robust to measurement noise and finite statistics.

## Neural Network Architecture

The network follows the architecture from the original paper:

* Input layer: $d^2$ nodes (measurement probabilities)

* Hidden layers: 200 → 180 → 180 → 160 → 160 → 160 → 160 → 100 neurons

* Activation: ReLU for hidden layers, tanh for output layer

* Output layer: $d^2$ nodes (Cholesky decomposition elements)

* Optimizer: Nadam with early stopping

## Citation

If you use this library in your research, please cite the original paper:

```
@article{koutny2022neural,
  title={Neural-network quantum state tomography},
  author={Koutn{\`y}, Dominik and Motka, Libor and Hradil, Zdenek and Reh{\'a}{\v{c}}ek, Jaroslav and S{\'a}nchez-Soto, Luis L},
  journal={Physical Review A},
  volume={106},
  number={1},
  pages={012409},
  year={2022},
  publisher={APS}
}
```

## Authors

This project was created by:

- **Manuel A. Garcia** — main developer  
- **Johan Garzón** — co-developer

## License

This project is licensed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**.  
See the [LICENSE](./LICENSE) file for details.
