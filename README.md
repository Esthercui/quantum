# Quantum Prisoner's Dilemma

**Pure-strategy Nash equilibrium search for two, three, and four players.**

A computational study of the Prisoner's Dilemma, from exhaustive classical
baselines to the angle-based circuit explored in the original research notebooks.
The focus is a precise question: **can any player improve their expected payoff
by changing only their own strategy?**

This repository makes the model explicit, checks every unilateral deviation on
the chosen grid, and provides a small, reproducible path from circuit to result.

[Run the walkthrough](notebooks/01_prisoners_dilemma.ipynb) ·
[Read the methods](docs/methods.md) ·
[Inspect the original research](archive/README.md)

## What the study establishes

The implemented circuit uses diagonal ZZ gates around local `Ry` / `Rz`
strategies. For its initial state and computational-basis measurement, the
outcome probabilities reduce to independent classical randomization:

$$p_i(D)=\sin^2(\theta_i/2).$$

The phase angles and ZZ strength do not change those probabilities. This gives
both a substantive result and an exact computational reduction: for the original
four-player grid, **18,974,736 angle profiles reduce to 14,641 distinct payoff
profiles**, with every phase choice still accounted for.

With correctly assigned player payoffs, the tested grids have one equilibrium
class: **every player defects**. All phase choices at that profile are tied.
The historical circuit therefore does not demonstrate a quantum equilibrium
advantage. The [methods](docs/methods.md) explain why and distinguish this circuit
from the EWL model that originally motivated the exploration.

| Players | Original angle grid per player | Full angle profiles | Evaluated representatives | Equilibrium payoff per player¹ |
|:--:|:--:|--:|--:|:--:|
| 2 | 15 × 8 | 14,400 | 225 | 1 |
| 3 | 15 × 8 | 1,728,000 | 3,375 | 1 |
| 4 | 11 × 6 | 18,974,736 | 14,641 | 1 |

¹ Collective payoff rule used by the original circuit notebooks. The classical
notebooks instead sum pairwise payoffs for k > 2. Both rules are implemented and
tested separately; under the pairwise rule the all-defect payoff is k − 1.
[Machine-readable results](results/reference.json) use a 1e-10 absolute tolerance.

## Quick start

Requires Python 3.11 or newer. The core package needs only NumPy.

```bash
git clone https://github.com/Esthercui/quantum.git
cd quantum
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .

# Original k = 4 angle grid, with the exact phase reduction.
quantum-pd --players 4 --theta-points 11 --phi-points 6

# Use the same pairwise payoff rule as the classical notebooks.
quantum-pd --players 3 --payoff-model pairwise --output output/k3.json
```

The JSON records the grid, payoff rule, tolerance, number of represented profiles,
equilibrium angles, payoffs, and each player's maximum gain from a unilateral
deviation. The default search is deterministic and does not require a QPU,
cloud account, worker pool, or external dataset.

For the pinned development environment, install [uv](https://docs.astral.sh/uv/)
and run `uv sync --frozen --all-extras`; prefix commands below with `uv run`.

## Read or run the notebook

The [walkthrough](notebooks/01_prisoners_dilemma.ipynb) includes saved outputs and
covers the classical game, player ordering, the circuit reduction, and k = 2–4
searches. To rerun it from the repository root:

```bash
python -m pip install -e '.[notebook]'
python -m jupyter nbconvert --execute --to notebook --inplace \
  notebooks/01_prisoners_dilemma.ipynb
```

## Use the Python API

```python
from math import pi
from quantum_pd import expected_payoff, search_grid

# Player 0 defects; player 1 cooperates.
assert expected_payoff([(pi, 0), (0, 0)]).tolist() == [5.0, 0.0]

result = search_grid(4, theta_points=11, phi_points=6)
assert result["evaluated_representatives"] == 14_641
assert result["equilibrium_angle_profiles"] == 1_296  # 6 tied phases per player
```

## Verification

```bash
python -m pip install -e '.[dev,verify]'
python -m pytest
ruff check .
ruff format --check .
python scripts/reproduce.py --check
```

Tests cover the classical payoff matrix, all classical action profiles through
k = 4, asymmetric player assignments, tied best responses, a game with no pure
equilibrium, absolute tolerances, unreduced versus reduced grid enumeration,
and gate-level agreement with Qiskit. CI runs the core suite on Python 3.11–3.13
and a separate Qiskit/notebook verification job. Qiskit tests skip when the
optional verification dependency is absent.

## Repository guide

| Path | Purpose |
|---|---|
| [`src/quantum_pd/`](src/quantum_pd/) | Payoff rules, circuit reference, exhaustive search, CLI |
| [`tests/`](tests/) | Mathematical invariants and independent circuit checks |
| [`notebooks/`](notebooks/) | Executed research walkthrough |
| [`results/reference.json`](results/reference.json) | Reproducible results for both payoff rules |
| [`docs/methods.md`](docs/methods.md) | Equations, assumptions, equilibrium definition, complexity |
| [`docs/research-notes.md`](docs/research-notes.md) | Corrections and scope of the reconstruction |
| [`archive/`](archive/) | Original notebooks and source hashes |

## Scope and provenance

This is a finite-grid **pure-strategy Nash** study. A fixed angle pair is one
pure strategy in the circuit game, even when measurement is probabilistic.
The search does not solve mixed distributions over angle strategies, population
evolutionary stability, or general quantum games. The analytical dominance
argument for this particular circuit is given separately in the methods.

The original notebooks belong to Esther Cui's research project. The maintained
package, tests, and documentation are an AI-assisted reconstruction of that
work, with corrections recorded explicitly. Original notebook bytes and saved
outputs remain in the archive; they are historical evidence, not newly verified
results. QAOA payoff optimization and Schelling coordination experiments remain
archived as separate explorations.
