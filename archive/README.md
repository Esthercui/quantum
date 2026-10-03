# Original exploration

This folder preserves the original public repository at
[`1c84b80`](https://github.com/Esthercui/quantum/tree/1c84b800e14efee63b8e8d9decc3aa0fc2d62d45).
The notebook bytes and saved outputs are unchanged; only their paths changed.
The [manifest](manifest.json) records source paths, destination paths, and SHA-256
hashes. Git history retains the original root-level layout.

For executable current results, begin with the
[maintained walkthrough](../notebooks/01_prisoners_dilemma.ipynb).
The [reconstruction notes](../docs/research-notes.md) explain corrections to the
original circuit interpretation and Nash search.

| Notebook | Original purpose | Reproduction status |
|---|---|---|
| [classical_pd.py.ipynb](notebooks/classical_pd.py.ipynb) | Classical PD enumeration for k = 2–4 | Payoff rules reconstructed and tested in the package |
| [quantum_pd.py-Copy1.ipynb](notebooks/quantum_pd.py-Copy1.ipynb) | QAOA, sampled and coarse-grid circuit experiments | Historical exploration; not executed in this refactor |
| [quantum_pd_k2k3.ipynb](notebooks/quantum_pd_k2k3.ipynb) | Higher-resolution k = 2,3 circuit search | Same grids recomputed with corrected player mapping and all ties |
| [quantum_pd_k4.ipynb](notebooks/quantum_pd_k4.ipynb) | Parallel k = 4 payoff sweep | Same grid covered through the exact phase reduction |
| [NasheEuilibria_K4.ipynb](notebooks/NasheEuilibria_K4.ipynb) | Analyze an external k = 4 pickle | Original pickle absent; saved output remains unverified |
| [all_schelling.py.ipynb](notebooks/all_schelling.py.ipynb) | Classical and quantum coordination experiments | Separate topic; historical only |

The original [READ_ME.txt](READ_ME.txt) is retained as an artifact. Historical
comments and results can conflict with the corrected methods. These notebooks
are excluded from CI execution: some start large jobs at the top level or depend
on missing files. Preservation does not imply that they are ready to rerun.
