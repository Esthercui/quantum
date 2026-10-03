# Research reconstruction notes

The project began as exploratory notebooks covering classical Prisoner's
Dilemma, angle-based quantum circuits, QAOA-style payoff optimization, and
Schelling coordination. The maintained package focuses on pure Nash equilibria
through four players and gives each numerical claim an executable check.

## Corrections that affect interpretation

| Original behavior | Maintained behavior | Why it matters |
|---|---|---|
| Read displayed Qiskit bits from left to right as player order | Decode player i from bit i | Asymmetric outcomes pay the correct player |
| Keep one best-response strategy per opponent profile | Compare payoff with the best-response value | Every tied equilibrium is retained |
| Describe CX–RZ–CX gates as an XX entangler | Document and check the actual ZZ circuit | The observed probabilities have a classical product form |
| Compare pairwise classical payoffs with collective circuit payoffs | Expose both rules and use matched baselines | k > 2 comparisons refer to the same game |
| Allocate all k = 4 tuples and one future per profile | Reduce equivalent phases and accumulate a small tensor | Reproducing the original domain no longer requires millions of tasks |
| Load a result pickle from an absolute external path | Generate portable JSON from source | A new reader can reproduce the maintained results |

The old coarse-grid notebook also uses a chain of CNOTs around one RZ, a
multi-body diagonal Z interaction rather than the pairwise interaction. Its
initial state and final basis measurement give the same probability-invariance
argument, but the maintained complex statevector specifically models the
pairwise circuit in the later k = 2,3 and k = 4 notebooks.

The archived QAOA experiments optimize aggregate payoff. Their parameter
optimum or payoff landscape is not a unilateral-deviation test and does not
establish a Nash equilibrium. The Schelling experiments answer a separate
coordination question. Neither is part of the current package's result table.

## What is preserved and what is new

All six source notebooks and the original index are preserved byte for byte
from commit `1c84b800e14efee63b8e8d9decc3aa0fc2d62d45`, with a hash manifest in
[`archive/manifest.json`](../archive/manifest.json). Their saved outputs have
not been rewritten to agree with the corrected implementation.

The maintained modules, tests, walkthrough, methods, and reference JSON were
created during an AI-assisted refactor. They reconstruct the original game
rules and gate sequence, fix the player mapping and equilibrium test, and add
an analytical phase reduction. They are not evidence that the historical
notebooks originally ran with these corrections or this environment.

The full original k = 4 pickle is absent from the source snapshot. Its saved
analysis output is therefore not independently reproduced. The new result file
is a fresh calculation on the documented grids, not a recovered historical run.
The original package versions, worker timing, and machine configuration cannot
be recovered from the notebooks alone. The current `uv.lock` pins the maintained
environment; it does not reconstruct the old one.

## Extending the study

A different entangler, initial state, strategy family, or measurement basis may
invalidate the phase reduction. Add an independent circuit check and a matching
classical baseline before reusing the solver for another model. Any new EWL
implementation should have an explicit model name and separate result artifacts.

The repository makes no claim of journal acceptance, quantum hardware advantage,
or evolutionary stability. Publication-specific claims should be checked
against the submitted manuscript and its exact computational model.
