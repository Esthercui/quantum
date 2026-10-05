# Simulating Game Theory with Quantum Computing

**Prisoner's Dilemma, quantum strategies, and coordination — research by Esther Cui.**

This repository accompanies *Simulating Game Theory and Strategic Interactions
Using Quantum Computing*. The study explores how classical and quantum models
shape strategic behavior: unilateral incentives in the Prisoner's Dilemma,
payoff optimization with parameterized circuits, and coordination using shared
quantum states.

The research spans two to four players. Its equilibrium analysis concerns
**pure-strategy Nash equilibria**: each player selects a fixed strategy, and no
player can improve their expected payoff by changing that strategy alone.

[Prisoner's Dilemma walkthrough](notebooks/01_prisoners_dilemma.ipynb) ·
[Circuit experiments](notebooks/02_circuit_experiments.ipynb) ·
[Methods](docs/methods.md) · [Revised paper](paper/research-paper.pdf) ·
[Original notebooks](archive/README.md)

## Research overview

| Experiment | Question | Implementation |
|---|---|---|
| Classical Prisoner's Dilemma, k = 2–4 | Which action profiles are stable under unilateral deviations? | Exhaustive enumeration with explicit multiplayer payoff rules |
| EWL game and all-pairs extension, k = 2–4 | How does Q change incentives, and which strategy profiles are stable? | Complete original grids and continuous unilateral-deviation certificates |
| Variational payoff optimization | Which circuit parameters increase aggregate payoff? | Depth-one ZZ/RX ansatz and payoff landscapes |
| Schelling coordination | How do shared states and local rotations affect matching? | Two-spot and four-spot Bell-pair experiments |

## The quantum strategy Q

In the maximally entangled **two-player EWL game**, Q changes the response to
classical defection:

| Player 0 | Player 1 | Expected payoffs |
|---|---|---|
| C | D | (0, 5) |
| Q | D | (5, 0) |
| D | Q | (0, 5) |
| Q | Q | (3, 3) |

Within EWL's restricted two-angle strategy family, `(Q, Q)` is a Nash
equilibrium. Both players receive the cooperative reward, and neither gains
by deviating alone. Q is a quantum operation; it is distinct from the classical
strategy C. The [methods](docs/methods.md#two-player-ewl-game) specify the matrices
and the unilateral-deviation bound from
[Eisert, Wilkens, and Lewenstein](https://arxiv.org/abs/quant-ph/9806088).

## Results through four players

The all-pairs EWL model uses the same collective payoff rule as its classical
baseline. Every listed grid equilibrium also passes a continuous best-response
check within the restricted two-angle strategy family.

| Players | Grid per player | Joint angle profiles | Certified grid profiles | All-Q payoff |
|---|---|---:|---:|---|
| 2 | 15 × 8 | 14,400 | 1 | (3, 3) |
| 3 | 15 × 8 | 1,728,000 | 1 | (3, 3, 3) |
| 4 | 11 × 6 | 18,974,736 | 433 | (3, 3, 3, 3) |

At four players, 433 angle profiles represent 13 profiles after identical D
operations are counted once: all-Q and 12 permutations of
`(C, U(π/2, π/2), D, D)`. The latter pay 5 to the `U(π/2, π/2)` player and 2.5
to the others. Grid counts do not exhaust the continuous space: at three players,
all players choosing `U(0, π/4)` form an off-grid equilibrium paying 3.25 each.

[The paper](paper/manuscript.md) and [saved certificates](results/) state the exact
model, strategy domain, tolerance, and payoff convention. The original grids
remain unchanged. All-Q is stable at both even and odd player counts studied.

## Quick start

Requires Python 3.11 or newer. NumPy is the only core dependency.
This update is available on the review branch:

```bash
git clone --branch polish/reproducible-nash https://github.com/Esthercui/quantum.git
cd quantum
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
```

Run the EWL example:

```python
from quantum_pd.ewl import C, D, Q, expected_payoff

for profile in ([C, D], [Q, D], [Q, Q]):
    print(expected_payoff(profile).round(6))
# [0. 5.]
# [5. 0.]
# [3. 3.]
```

Run a classical baseline:

```python
from quantum_pd import classical_nash

print(classical_nash(4, model="collective"))
# [{'actions': [1, 1, 1, 1], 'payoffs': [1.0, 1.0, 1.0, 1.0]}]
```

The command-line interface evaluates the EWL game and certifies each grid
candidate against continuous unilateral deviations:

```bash
quantum-pd --players 4 --theta-points 11 --phi-points 6 --atol 0.001 --output output/ewl-k4.json
```

The separate [ZZ benchmark](docs/zz-reference.md) remains available through
`--circuit zz`. It is not the EWL model used in the manuscript.

## Notebooks and reproducibility

The two maintained notebooks include executed outputs and run from the repository
root. Optional dependencies support Qiskit circuit checks and notebook execution:

```bash
python -m pip install -e '.[dev,verify,notebook]'
python -m jupyter nbconvert --execute --to notebook --inplace \
  notebooks/01_prisoners_dilemma.ipynb
python -m jupyter nbconvert --execute --to notebook --inplace \
  notebooks/02_circuit_experiments.ipynb

python -m pytest
ruff check .
ruff format --check .
python scripts/reproduce.py --check
python scripts/reproduce_experiments.py --check
python scripts/reproduce_optimization.py --check
python scripts/verify_research.py --full
python scripts/build_manuscript.py --check
```

For the pinned environment, use `uv sync --frozen --all-extras` and prefix
commands with `uv run`. Regenerate full EWL records with
`python scripts/reproduce_research.py`; rerun the retained local optimizer with
`python scripts/reproduce_optimization.py`. CI checks Python 3.11–3.13, independent Qiskit gate
implementations, result regeneration, and both notebooks.

## Repository guide

| Path | Contents |
|---|---|
| [`src/quantum_pd/ewl.py`](src/quantum_pd/ewl.py) | EWL reference and explicit all-pairs extension |
| [`src/quantum_pd/ewl_search.py`](src/quantum_pd/ewl_search.py) | Full grids and continuous-response certificates |
| [`paper/`](paper/) | Revised manuscript, PDF, figures, and source-linked tables |
| [`src/quantum_pd/`](src/quantum_pd/) | Payoff rules, Nash tests, ZZ benchmark, and circuit experiments |
| [`notebooks/`](notebooks/) | Executed research walkthroughs |
| [`docs/methods.md`](docs/methods.md) | Models, equations, conventions, and equilibrium definition |
| [`results/experiments.json`](results/experiments.json) | EWL, variational, and coordination examples |
| [`results/reference.json`](results/reference.json) | ZZ benchmark grids under both payoff rules |
| [`tests/`](tests/) | Mathematical identities and circuit regression tests |
| [`archive/`](archive/) | Original research notebooks and checksum manifest |

## Research scope

A fixed quantum strategy can have probabilistic measurement outcomes. The Nash
analysis tests deviations between fixed strategies, without searching mixed
distributions over strategies. Variational payoff optimization and coordination
answer separate questions from the Nash search.

Each implementation has an explicit circuit and payoff convention. The EWL
extension through four players is defined explicitly; other multiplayer models
require their own analysis. Current examples use exact statevector probabilities and do not
require quantum hardware or a cloud account.

The original work is preserved in the archive. The maintained package,
walkthroughs, and tests were developed through an AI-assisted refactor.
