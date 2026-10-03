# Models and methods

The study combines Prisoner's Dilemma equilibrium analysis, variational payoff
optimization, and Schelling coordination. This page defines the models and
conventions used by the maintained examples.

## Classical Prisoner's Dilemma

Cooperation is encoded as 0 and defection as 1. Payoffs are ordered by player:

| Player 0 / Player 1 | C | D |
|---|---|---|
| C | (3, 3) | (0, 5) |
| D | (5, 0) | (1, 1) |

For k = 2–4, the package provides two explicit payoff rules:

- **Collective:** all-C pays 3 to everyone; all-D pays 1. In a mixed action
  profile, defectors receive 5 and cooperators receive 0.
- **Pairwise:** each player sums the two-player payoff over their k − 1 opponents.

For example, `(D, C, C)` pays `(5, 0, 0)` collectively and `(10, 3, 3)` pairwise.
Choose the same rule for the baseline and circuit being compared.

## Two-player EWL game

`quantum_pd.ewl` implements the restricted two-angle game of
[Eisert, Wilkens, and Lewenstein, *Quantum Games and Quantum Strategies*](https://arxiv.org/abs/quant-ph/9806088),
using the conventions in equations (3), (5), and (7) of version 4.

```math
U(\theta,\phi)=\begin{pmatrix}
e^{i\phi}\cos(\theta/2)&\sin(\theta/2)\\
-\sin(\theta/2)&e^{-i\phi}\cos(\theta/2)
\end{pmatrix},\qquad
0\leq\theta\leq\pi,\quad 0\leq\phi\leq\pi/2.
```

```math
C=U(0,0)=I,\qquad D=U(\pi,0)=iY,\qquad
Q=U(0,\pi/2)=iZ.
```

The protocol prepares an entangled state, applies each player's strategy, and
then applies the inverse entangler before measurement:

```math
J=\exp\left(-\frac{i\gamma}{2}D\otimes D\right),\qquad
|\psi_f\rangle=J^\dagger(U_0\otimes U_1)J|00\rangle.
```

Here the equation uses player-ordered tensor factors. Arrays in the implementation
use Qiskit's little-endian order, so their tensor product is `U_1 ⊗ U_0`.
Expected payoff is the sum of each outcome's payoff weighted by its Born
probability. The default γ = π/2 gives maximal entanglement.

A gate-level implementation uses `ryy(-gamma)` for J. Each local strategy is
`rz(-phi)`, then `ry(-theta)`, then `rz(-phi)`. The closing gate is `ryy(gamma)`.
Tests compare that Qiskit sequence with the independent NumPy matrices.

At maximal entanglement, `(Q, D)` pays `(5, 0)` and `(Q, Q)` pays `(3, 3)`.
If player 1 holds Q fixed, player 0's expected payoff satisfies:

```math
u_0\bigl(U(\theta,\phi),Q\bigr)
=\cos^2(\theta/2)\bigl(3\sin^2\phi+\cos^2\phi\bigr)\leq 3.
```

By symmetry the same holds for player 1. This establishes `(Q, Q)` as a Nash
equilibrium throughout the stated strategy family. The notebook also enumerates
all 14,400 joint profiles on the 15 × 8 grid. Phase angles are fully enumerated.
The analytical bound concerns this strategy family and this two-player game.

## Nash test and player ordering

A fixed angle pair is one pure strategy, even if measurement is probabilistic.
For player i, hold every other strategy fixed and compute the best attainable
expected payoff over i's allowed strategies. The difference between that payoff
and the current payoff is the player's regret. A profile is an approximate
Nash equilibrium when every regret is at most the absolute tolerance.

`pure_nash_mask` keeps every tied best response and defaults to `atol=1e-10`.
A finite-grid result certifies deviations on that grid. A continuous-space
claim requires a separate argument, such as the EWL bound above.

Player i controls qubit i. At statevector index x, their measured action is
`(x >> i) & 1`. Displayed Qiskit strings run from the highest qubit to qubit 0;
see [IBM's bit-ordering guide](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering).
The payoff vector always runs from player 0 upward.

## Multiplayer circuit benchmark

The `game` module, `search_grid`, and `quantum-pd` CLI evaluate the pairwise ZZ
circuit for k = 2–4. Its gate definition, exact probability reduction, grid
sizes, and computational cost are given in the [ZZ reference](zz-reference.md).
The reduction is specific to that circuit. The EWL example uses its own complete
payoff tensor with the general Nash test.

## Variational payoff optimization

`experiments.qaoa_circuit` prepares each qubit with H, applies a uniform pairwise
ZZ layer, then applies RX mixing. For depth one, each pair uses
`cx(i,j); rz(2*gamma,j); cx(i,j)`, followed by `rx(2*beta)` on each qubit.
The examples evaluate aggregate pairwise payoff over a 7 × 7 parameter grid.
This is a payoff landscape; a parameter optimum is evaluated separately from
individual-player Nash incentives.

## Schelling coordination

The two-spot protocol prepares a Bell pair, applies local RY rotations, and
measures whether both players choose the same spot. With local angles θA and θB:

```math
P(\mathrm{match})=\cos^2\left(\frac{\theta_A-\theta_B}{2}\right).
```

The optional inverse circuit applies CX and H jointly before measurement; that
variant has match probability 1 for these rotations. Four spots use two Bell
pairs and compare the players' two-bit registers. An independent classical
baseline has match probability `pA*pB + (1-pA)*(1-pB)` for two spots, and 1/4
for uniform independent choices among four spots. Shared randomness is a
different classical resource and can also provide perfect coordination.

## Numerical conventions

Maintained examples use float64 statevector calculations without shot sampling.
Inputs and angle domains are validated. `results/experiments.json` records the
EWL, variational, and coordination examples; `results/reference.json` records
the ZZ benchmark with its source digest. The reproduction scripts regenerate
these artifacts and provide `--check` for verification.
