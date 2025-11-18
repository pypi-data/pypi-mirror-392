# Qsimkit - Quantum Simulation Toolkit

[![License](https://img.shields.io/github/license/Jue-Xu/Qsimkit.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)
[![Release](https://img.shields.io/github/v/release/jue-xu/Qsimkit?include_prereleases)](https://github.com/Jue-Xu/Qsimkit/releases)

A Python package for quantum simulation with error bounds and Trotterization tools. Built on [Qiskit](https://www.ibm.com/quantum/qiskit) and [OpenFermion](https://github.com/quantumlib/OpenFermion).

## Features

- **Hamiltonians**: Spin lattice models (nearest-neighbor, power-law, IQP) and fermionic systems
- **Trotter Formulas**: First, second, and high-order product formulas with JAX acceleration
- **Error Bounds**: Analytical and numerical bounds for Trotter error analysis
- **States**: Entangled states (GHZ, W) and random states
- **Channels**: Quantum noise channels and transformations
- **Utilities**: Binary search for optimal Trotter steps, plotting tools

##  Installation

### From PyPI (coming soon)
```bash
pip install qsimkit
```

### From source
```bash
git clone https://github.com/Jue-Xu/Qsimkit.git
cd Qsimkit
pip install -e .
```

### Requirements
- Python >= 3.10
- Core: numpy, scipy, qiskit, matplotlib
- Optional: jax/jaxlib (GPU acceleration), openfermion (fermionic systems)

## Quick Start

```python
import qsimkit
from qsimkit.spin import Nearest_Neighbour_1d
from qsimkit.trotter import pf
from qsimkit.bounds import tight_bound

# Create a spin Hamiltonian
H = Nearest_Neighbour_1d(n=4, Jx=1.0, Jy=1.0, Jz=1.0, hx=0.5)
h_list = H.ham  # Get Hamiltonian terms

# Compute Trotter approximation
t = 1.0  # Evolution time
r = 100  # Number of Trotter steps
U_approx = pf(h_list, t, r, order=2)

# Estimate error bound
error = tight_bound(h_list, order=2, t=t, r=r, type='spectral')
print(f"Error bound: {error}")
```

## Usage Examples

### 1. Hamiltonian Models

```python
from qsimkit import spin, fermion

# Nearest-neighbor 1D spin chain
nn_chain = spin.Nearest_Neighbour_1d(
    n=10,           # 10 qubits
    Jx=1.0,         # X coupling
    Jy=1.0,         # Y coupling
    Jz=1.0,         # Z coupling
    hx=0.5,         # X field
    pbc=False       # Open boundary
)

# Get Hamiltonian in different groupings
h_parity = nn_chain.ham_par  # Parity grouping
h_xyz = nn_chain.ham_xyz      # XYZ grouping

# 2D lattice
lattice_2d = spin.Nearest_Neighbour_2d(nx=4, ny=4, Jx=1.0, Jy=1.0, Jz=1.0)

# Cluster Ising model
cluster = spin.Cluster_Ising(n=8, J=1.0, g=0.5)
```

### 2. Trotter Methods

```python
from qsimkit.trotter import pf, pf_high

# First-order Trotter
U1 = pf(h_list, t=1.0, r=50, order=1)

# Second-order Trotter (symmetric)
U2 = pf(h_list, t=1.0, r=50, order=2)

# High-order Trotter (4th, 6th, 8th order)
U4 = pf_high(h_list, t=1.0, r=50, order=4)
U6 = pf_high(h_list, t=1.0, r=50, order=6)

# With JAX acceleration (if available)
U2_jax = pf(h_list, t=1.0, r=50, order=2, use_jax=True)
```

### 3. Error Bounds

```python
from qsimkit.bounds import (
    tight_bound,
    analytic_bound,
    interference_bound,
    lc_tail_bound
)

# Tight commutator-based bound
error = tight_bound(h_list, order=2, t=1.0, r=100, type='spectral')

# Analytical bound
error_analytic = analytic_bound(H=h_list, k=1, t=1.0, r=100)

# Two-term interference bound (Layden 2022)
if len(h_list) == 2:
    bound, e1, e2, e3 = interference_bound(h_list, t=1.0, r=100)

# Light-cone tail bound (for nearest-neighbor Hamiltonians)
error_lc = lc_tail_bound(r=100, n=10, h=nn_chain, t=1.0, ob_type='singl')
```

### 4. Finding Optimal Trotter Steps

```python
from qsimkit.utils import binary_search_r

# Find minimum r to achieve target error
target_error = 1e-3
r_optimal = binary_search_r(
    h_list=h_list,
    order=2,
    t=1.0,
    target_error=target_error,
    norm_type='spectral'
)
print(f"Need r={r_optimal} steps for error < {target_error}")
```

## Package Structure

```
qsimkit/
├── spin.py           # Spin Hamiltonian models
├── fermion.py        # Fermionic Hamiltonians
├── states.py         # Quantum states (GHZ, W, random)
├── trotter.py        # Trotter-Suzuki product formulas
├── bounds.py         # Error bound calculations
├── measure.py        # Operators (commutator, norm, etc.)
├── channel.py        # Quantum channels
├── utils.py          # Utility functions
└── plot_config.py    # Plotting configuration
```

## Documentation

More examples and tutorials: [https://jue-xu.github.io/cookbook-quantum-simulation](https://jue-xu.github.io/cookbook-quantum-simulation)

## Citation

If you use Qsimkit in your research, please cite:

```bibtex
@software{qsimkit,
  author = {Xu, Jue},
  title = {Qsimkit: Quantum Simulation Toolkit},
  url = {https://github.com/Jue-Xu/Qsimkit},
  year = {2024}
}
```

## Migration from quantum-simulation-recipe

If you're upgrading from the old `quantum-simulation-recipe` package:

```python
# Old imports
from quantum_simulation_recipe.spin import Nearest_Neighbour_1d
from quantum_simulation_recipe.trotter import pf
from quantum_simulation_recipe.bounds import tight_bound

# New imports (just change package name)
from qsimkit.spin import Nearest_Neighbour_1d
from qsimkit.trotter import pf
from qsimkit.bounds import tight_bound
```

All functionality remains the same, just the package name has changed.

## Development

### Running Tests
```bash
pytest tests/
```

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contact

- Author: Jue Xu
- Email: xujue@connect.hku.hk
- GitHub: [@Jue-Xu](https://github.com/Jue-Xu)
