# Model and methods

For the final manuscript comparison, including QAOA and Schelling experiments,
see [Paper and code](paper-comparison.md). This page describes the verified
Prisoner's Dilemma implementation.

## Question and scope

For k ∈ {2, 3, 4}, fix each player's strategy and ask whether a unilateral
change increases that player's expected payoff. The numerical search checks
all deviations in a finite angle grid. A profile qualifies when every player's
maximum improvement is at most an absolute tolerance of 1e-10.

A pure strategy is one fixed pair (θ, φ). Probabilistic measurement of that
strategy does not make it a mixed strategy over angle pairs. The package does
not search distributions over strategies or model evolutionary populations.

## Payoffs

Cooperation is 0 and defection is 1. The two-player payoff table is:

| Player 0 / Player 1 | Cooperate | Defect |
|---|---|---|
| Cooperate | (3, 3) | (0, 5) |
| Defect | (5, 0) | (1, 1) |

The archived notebooks use two extensions to more players:

- **Collective**, in the circuit Nash notebooks: every player gets 3 at all-C
  and 1 at all-D. At any other profile, defectors receive 5 and cooperators 0.
- **Pairwise**, in the classical notebooks: each player sums the two-player
  payoff over their k − 1 opponents. There is no averaging or normalization.

For example, `(D, C, C)` pays `(5, 0, 0)` collectively and `(10, 3, 3)` pairwise.
Comparisons must use the same rule. Both have all-D as the unique classical
pure equilibrium, paying 1 or k − 1 per player, respectively.

## Circuit actually implemented

The maintained model follows `quantum_pd_k2k3.ipynb` and `quantum_pd_k4.ipynb`:

```math
|\psi_f\rangle=J^\dagger\left(\bigotimes_i U_i\right)J|0\rangle^{\otimes k},
```

```math
J=\prod_{i\lt j}\exp(-i\gamma Z_iZ_j),\qquad
U_i=R_z(\phi_i)R_y(\theta_i).
```

The allowed ranges are θ ∈ [0, π], φ ∈ [0, π/2], γ ∈ [0, π/2]. The notebook
sequence `cx(i,j); rz(2*gamma,j); cx(i,j)` is a ZZ rotation, as follows from
[IBM's RZZ matrix](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZZGate).
It is not the XX entangler described in some original comments. At the historical
γ = π/2, each pair gate is `-i Z⊗Z`, itself a product of local operators.

This implementation documents the original gate sequence rather than silently
substituting a different quantum game. The foundational EWL paper is
[Eisert, Wilkens, and Lewenstein, *Quantum Games and Quantum Strategies*,
Phys. Rev. Lett. 83, 3077 (1999)](https://arxiv.org/abs/quant-ph/9806088).
Its strategy and entangler conventions must be implemented and validated
separately before transferring its equilibrium claims to a program.

## Exact reduction of the measurement probabilities

`J` is diagonal, so its action on the initial all-zero basis state is only a
global phase. Each local strategy then produces

```math
R_z(\phi_i)R_y(\theta_i)|0\rangle
=e^{-i\phi_i/2}\cos(\theta_i/2)|0\rangle
+e^{i\phi_i/2}\sin(\theta_i/2)|1\rangle.
```

The final `J†` is also diagonal and changes no computational-basis probability.
Consequently, for outcome b in player order,

```math
P(b)=\prod_i\begin{cases}
\cos^2(\theta_i/2),&b_i=0,\\
\sin^2(\theta_i/2),&b_i=1.
\end{cases}
```

This is independent of every φ and γ in the stated domain. It does not assert
that the final state is separable for every γ; diagonal gates can change
entanglement without changing these measurement probabilities.

Expected payoff is `Σ_b P(b) payoff_i(b)`. `game.statevector` retains the complex
phases as a reference; `game.probabilities` uses the product formula. The tests
compare both with an independent Qiskit gate sequence at three γ values and
asymmetric random strategies for all three player counts.

## Player ordering

Player i controls qubit i. At statevector index x, that player's action is
`(x >> i) & 1`. Qiskit displays bitstrings as `q_(k-1)...q_0`, so displayed strings
must be reversed before interpreting them as player-ordered payoff vectors.
See [IBM's bit-ordering guide](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering).

An essential regression case is player 0 defecting while player 1 cooperates:
angles `[(π, 0), (0, 0)]` produce basis index 1 (displayed `01`) and payoff
`(5, 0)`. The old left-to-right string mapping assigned this payoff backwards.

## Search and equilibrium certificate

Let nθ and nφ denote grid sizes, with endpoints included. A single-point φ grid
means φ = 0. For each θ profile, all nφ^k phase profiles have identical payoffs
and identical incentives to deviate. The search therefore enumerates nθ^k
representatives and reports their phase multiplicity explicitly.

The payoff tensor has one strategy axis per player and a final payoff axis.
For player i, reducing their strategy axis by `max` yields their best attainable
payoff with opponents fixed. Regret is that value minus current payoff. A profile
is returned if every regret is ≤ `atol`. No arbitrary `argmax` tie-breaking is used.

Output includes all qualifying equivalence classes, their representative angles
(φ = 0), payoffs, regrets, and the count of represented angle profiles. Under the
default tolerance, the reference searches find one class, θ_i = π for every
player. The respective phase multiplicities are 8² = 64, 8³ = 512, and 6⁴ = 1,296.
These are strategically equivalent parameter choices, not distinct behaviors.

A finite-grid certificate alone does not prove a continuous-space equilibrium.
For this particular model there is also a separate analytical argument:

- In the collective game, choosing D instead of C improves payoff by 2 if all
  opponents cooperate, 1 if all defect, and 5 otherwise. Every difference is
  positive, so the expected difference is positive against any independent
  opponent randomization.
- In the pairwise game, each opponent contributes a strictly positive gain
  (2 against C, 1 against D); summing preserves strict dominance.

Thus payoff strictly increases with one's defection probability. In the stated
θ domain, the optimum is θ = π regardless of opponents. All-D, with arbitrary
phases, is the only exact equilibrium behavior even in the continuous angle
space. Large numerical tolerances may also admit approximate equilibria.

## Cost and numerical limits

The reduction evaluates nθ^k representatives instead of `(nθ nφ)^k` full angle
profiles. The implemented outcome accumulation costs O(k 2^k nθ^k) arithmetic
and uses O(k nθ^k) tensor storage. Search cost still grows exponentially with k;
this package intentionally limits k to 2–4. A default limit of one million
representatives rejects oversized requests before allocation.

The original four-player grid requires 14,641 representatives instead of
18,974,736 angle profiles, a factor of 1,296 in profile count. This is a
model-specific algebraic reduction, not a hardware speedup or a measured runtime
ratio. No historical timing comparison is claimed.

Calculations use deterministic float64 arithmetic without shot sampling. All
angles, payoffs, and tolerances are validated. JSON results are generated from
source and include a source digest; `scripts/reproduce.py --check` verifies the
saved artifact. The original missing pickle is not an input to these new runs.
