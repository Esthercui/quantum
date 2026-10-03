# Quantum Game Simulations

**Prisoner’s Dilemma for two to four players, and Bell-pair coordination.**

Research code accompanying Esther Cui's final manuscript, *Simulating Game
Theory and Strategic Interactions Using Quantum Computing*. The project explores
classical enumeration, QAOA-style payoff optimization, circuit-based pure Nash
searches, and Schelling coordination.

The maintained package turns that exploration into small, tested experiments
with explicit payoff rules, reproducible outputs, and a documented connection
to the original paper.

[Paper and code](docs/paper-comparison.md) ·
[PD walkthrough](notebooks/01_prisoners_dilemma.ipynb) ·
[Paper companion](notebooks/02_paper_companion.ipynb) ·
[Methods](docs/methods.md)

## Relationship to the paper

The original grids and many Schelling results can be traced to the notebooks.
Some numerical summaries and the cooperative Nash interpretation require
correction. The [paper-to-code comparison](docs/paper-comparison.md) identifies
the exact pages, reported values, original outputs, and verified calculations.
Reported manuscript values remain in [a separate source record](results/paper-reported.json).
The [original notebooks](archive/README.md) are preserved unchanged in a verified
ZIP; the two maintained notebooks are executed and contain no saved errors.

## Verified Prisoner’s Dilemma result

The implemented circuit uses diagonal ZZ gates around local `Ry` / `Rz`
strategies. For its initial state and computational-basis measurement, the
outcome probabilities reduce to independent classical randomization:

```math
p_i(D)=\sin^2(\theta_i/2).
```

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
While this update is under review, clone the review branch shown below.

```bash
git clone --branch polish/reproducible-nash https://github.com/Esthercui/quantum.git
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

## Read or run the notebooks

The [walkthrough](notebooks/01_prisoners_dilemma.ipynb) includes saved outputs and
covers the classical game, player ordering, the circuit reduction, and k = 2–4
searches. The [paper companion](notebooks/02_paper_companion.ipynb) adds direct
checks of the manuscript’s PD, QAOA, and Schelling results. To rerun both from
the repository root:

```bash
python -m pip install -e '.[notebook,verify]'
python -m jupyter nbconvert --execute --to notebook --inplace \
  notebooks/01_prisoners_dilemma.ipynb
python -m jupyter nbconvert --execute --to notebook --inplace \
  notebooks/02_paper_companion.ipynb
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
python scripts/check_paper.py --check
```

Tests cover the classical payoff matrix, all classical action profiles through
k = 4, asymmetric player assignments, tied best responses, a game with no pure
equilibrium, absolute tolerances, unreduced versus reduced grid enumeration,
and gate-level agreement with Qiskit. CI runs the core suite on Python 3.11–3.13
and a separate Qiskit/notebook verification job for both walkthroughs. Qiskit tests skip when the
optional verification dependency is absent.

## Repository guide

| Path | Purpose |
|---|---|
| [`src/quantum_pd/`](src/quantum_pd/) | Payoff rules, circuit reference, exhaustive search, CLI |
| [`tests/`](tests/) | Mathematical invariants and independent circuit checks |
| [`notebooks/`](notebooks/) | Executed research walkthrough |
| [`results/reference.json`](results/reference.json) | Reproducible results for both payoff rules |
| [`docs/paper-comparison.md`](docs/paper-comparison.md) | Final manuscript mapped to source, results, and needed corrections |
| [`docs/methods.md`](docs/methods.md) | Equations, assumptions, equilibrium definition, complexity |
| [`docs/research-notes.md`](docs/research-notes.md) | Corrections and scope of the reconstruction |
| [`archive/`](archive/) | Original notebooks and source hashes |

## Scope and provenance

The PD solver studies finite-grid **pure-strategy Nash** equilibria. A fixed angle pair is one
pure strategy in the circuit game, even when measurement is probabilistic.
The search does not solve mixed distributions over angle strategies, population
evolutionary stability, or general quantum games. The analytical dominance
argument for this particular circuit is given separately in the methods.

The original notebooks belong to Esther Cui's research project. The maintained
package, tests, and documentation are an AI-assisted reconstruction of that
work, with corrections recorded explicitly. Original notebook bytes and saved
outputs remain in the archive; they are historical evidence, not newly verified
results. QAOA payoff optimization and Schelling coordination have separate, bounded
circuit replays in the paper companion. These do not certify Nash equilibria
or reproduce missing historical samples.
