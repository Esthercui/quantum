# Original research archive

[Download the original notebooks](original-notebooks.zip) ·
[Read the paper-to-code comparison](../docs/paper-comparison.md) ·
[Run the maintained paper companion](../notebooks/02_paper_companion.ipynb)

The ZIP preserves all six notebooks and the original index byte for byte from
[`1c84b80`](https://github.com/Esthercui/quantum/tree/1c84b800e14efee63b8e8d9decc3aa0fc2d62d45).
The [manifest](manifest.json) records each member's SHA-256. Tests verify the
archive contents. The source is also retained in Git history.

The original exploration includes repeated definitions, large top-level jobs,
a missing external pickle, and an unfinished statistical cell with a saved
`statsmodels` import error. These historical files are packaged for provenance;
the maintained notebooks provide the clean, executed reading experience.
No original results or tracebacks were rewritten to appear newly validated.

| ZIP member under `notebooks/` | Paper connection |
|---|---|
| `classical_pd.py.ipynb` | Classical PD baseline, k = 2–4 |
| `quantum_pd.py-Copy1.ipynb` | QAOA, sampled PD, coarse grids, runtime plot, heatmap |
| `quantum_pd_k2k3.ipynb` | Higher-resolution 15 × 8 PD grids |
| `quantum_pd_k4.ipynb` | 11 × 6 four-player payoff sweep |
| `NasheEuilibria_K4.ipynb` | Analysis of the unavailable k = 4 pickle |
| `all_schelling.py.ipynb` | Coordination experiments and bias curves |

The original `READ_ME.txt` is at the ZIP root. Historical notebook output is
reported evidence; the [comparison](../docs/paper-comparison.md) distinguishes
it from verified results and explains corrections that affect interpretation.
