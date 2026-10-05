# Research guide

The project studies strategic incentives and coordination with small quantum
circuits. Begin with the [Prisoner's Dilemma walkthrough](../notebooks/01_prisoners_dilemma.ipynb),
then explore [variational and coordination experiments](../notebooks/02_circuit_experiments.ipynb).

The [methods](methods.md) define the classical payoffs, the EWL model and its explicit all-pairs extension,
and the pure Nash test. The [ZZ circuit reference](zz-reference.md) documents
the separate multiplayer benchmark, including its phase reduction and resource
limits. Explicit model definitions make each experiment independently readable.

The [archive](../archive/README.md) preserves six original notebooks and the
research index from commit `1c84b800e14efee63b8e8d9decc3aa0fc2d62d45`. The maintained
modules provide portable functions, input validation, deterministic examples,
and independent circuit checks. The current `uv.lock` pins their environment.

When extending an experiment, specify its initial state, entangler, local
strategy family, measurement rule, and player payoff mapping. Reuse a reduction
only after checking that those assumptions still hold. Compare results under
one common payoff convention, and save strategy parameters alongside outcomes.

The [revised manuscript](../paper/manuscript.md) is built from the saved research
results. Full angle grids are enumerated without the ZZ phase reduction; each
returned EWL candidate is checked against continuous deviations. The original
PDF is preserved separately by the author.
