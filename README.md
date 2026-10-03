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
[Methods](docs/methods.md) · [Original notebooks](archive/README.md)

## Research overview

| Experiment | Question | Implementation |
|---|---|---|
| Classical Prisoner's Dilemma, k = 2–4 | Which action profiles are stable under unilateral deviations? | Exhaustive enumeration with explicit multiplayer payoff rules |
| Two-player EWL game | How does the quantum strategy Q change a player's best response? | Entangle–strategy–disentangle circuit and a complete 15 × 8 strategy grid |
| Multiplayer circuit exploration, k = 2–4 | How do circuit choices and strategy grids affect payoffs and search cost? | Documented ZZ circuit benchmark and the original research archive |
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

The separate [ZZ circuit benchmark](docs/zz-reference.md) has a command-line
interface. Its JSON output includes the grid, payoff rule, equilibrium angles,
and each player's maximum gain from a unilateral deviation:

```bash
quantum-pd --players 4 --theta-points 11 --phi-points 6 --output output/zz-k4.json
```

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
```

For the pinned environment, use `uv sync --frozen --all-extras` and prefix
commands with `uv run`. CI checks Python 3.11–3.13, independent Qiskit gate
implementations, result regeneration, and both notebooks.

## Repository guide

| Path | Contents |
|---|---|
| [`src/quantum_pd/ewl.py`](src/quantum_pd/ewl.py) | Standard two-player EWL reference |
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
reference is for two players; the multiplayer benchmark and archive are described
separately. Current examples use exact statevector probabilities and do not
require quantum hardware or a cloud account.

The original work is preserved in the archive. The maintained package,
walkthroughs, and tests were developed through an AI-assisted refactor.
