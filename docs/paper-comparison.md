# Paper and code

This page connects Esther Cui's final manuscript, **Simulating Game Theory and
Strategic Interactions Using Quantum Computing**, to its original source and the
maintained implementation. Page numbers refer to the supplied 13-page PDF.
The PDF's SHA-256 identifier is recorded in
[`paper-reported.json`](../results/paper-reported.json); the manuscript itself
has not been changed or republished here.

**The paper and the verified code do not fully agree.** Some reported numbers
can be traced to saved notebook outputs, but the cooperative Nash interpretation
fails a corrected unilateral-deviation check. This page states which results
match, which are historical observations, and which need correction.

## Read and reproduce

- [Original research archive](../archive/README.md): exact notebooks, including
  their saved results, from the manuscript's repository.
- [Paper companion notebook](../notebooks/02_paper_companion.ipynb): small,
  executable checks for the PD, QAOA, and Schelling sections.
- [Reported values](../results/paper-reported.json): manuscript transcription
  alongside historical outputs, explicitly labeled as reported evidence.
- [Computed checks](../results/paper-checks.json): current exact statevector
  evaluations and deviation witnesses, not historical shot-count reruns.

```bash
python -m pip install -e '.[notebook,verify]'
python scripts/check_paper.py --check
python -m jupyter nbconvert --execute --to notebook --inplace \
  notebooks/02_paper_companion.ipynb
```

## Prisoner's Dilemma: methods and results

| Paper location | Paper reports | Original code and saved output | Resolution |
|---|---|---|---|
| §3.1.1, p. 3 | k = 2,3: 15 × 8; k = 4: 11 × 6 | These grids are in the later circuit notebooks | Matches; full profile counts are 14,400, 1,728,000, and 18,974,736 |
| §3.1.1, p. 3 | Maximally entangling pair gates; U = Ry Rz | Gates execute Ry then Rz, so the matrix product is Rz Ry; CX–RZ–CX is a diagonal ZZ gate | [Methods](methods.md) describe the actual sequence. Its measured probabilities are independent of phase and gamma |
| §3.1.1, p. 3 | Nash threshold below 10⁻³ | Original search selects a single strict argmax; no grid-regret tolerance is applied | The maintained search keeps all ties. Both 10⁻³ and 10⁻¹⁰ return all-D on the stated grids |
| §3.1.3 and Table 2, pp. 4,6 | 4,096 shots for quantum values | High-resolution PD sweeps use saved statevectors with exact probabilities; the early sampled two-player sweep uses 4,096 shots | Statevector expectations and sampled estimates must be labeled separately |
| Table 2, p. 6 | Classical all-D payoff is 1 for every k | Classical k = 3,4 code sums pairwise payoffs: all-D pays 2 and 3 per player | Use 1,2,3 for pairwise comparisons, or rerun all methods under the collective rule |
| Table 2 and §4.1.2, p. 6 | Cooperative equilibria at k = 2,4, payoff 3 | Saved notebooks print cooperative profiles; player-payoff indexing is reversed | These are historical outputs, not valid equilibrium certificates; see the deviation witnesses below |
| §4.1.2, p. 6 | (C,D,C) at k = 3; a parity mechanism | Saved output shows (0,5,0), but a cooperator can gain by defecting | The implemented circuit does not establish this equilibrium or the parity explanation |
| §4.1.2, p. 6 | k = 4 defection pays 2.4 rather than 3 | Correctly assigned collective payoff to the deviator is 5 | The computed incentive is +2, not −0.6 |
| Table 2 / text, p. 6 | Two k = 3 equilibria in the table; one in the prose | Coarse notebook prints two profiles; the 15 × 8 notebook prints six | Counts from different runs were combined; neither is a corrected count of Nash profiles |

### Direct deviation witnesses

These calculations retain the original circuit and collective payoff rule,
while assigning each payoff to the player who controls that qubit.

| Reported profile | Current payoff to player 0 | Player 0 switches to D | Payoff gain |
|---|---:|---:|---:|
| k = 2: (C,C) | 3 | 5 | +2 |
| k = 3: (C,D,C) | 0 | 5 | +5 |
| k = 4: (C,C,C,C) | 3 | 5 | +2 |

Phase values do not affect these witnesses. Each gain exceeds either tolerance,
so none of these profiles is a Nash equilibrium of the implemented game.
The full corrected grid searches return all-D, with 64, 512, and 1,296 equivalent
phase assignments for k = 2,3,4. The [analytical dominance argument](methods.md#search-and-equilibrium-certificate)
explains why this behavior also holds across the continuous angle domain.

## QAOA: optimization results and limits

The paper correctly distinguishes payoff optimization from Nash search in
§3.1 (p. 3). The original code maximizes the sum of pairwise player payoffs with
a depth-one uniform ZZ/RX circuit. Its ZZ phase layer alone is not a complete
encoding of the stated aggregate PD payoff: one pair's total payoff is
`4.5 + Z_i + Z_j - 0.5 Z_i Z_j`. The original phase layer omits the linear terms.
The maintained replay retains that ansatz and labels it explicitly.

| k | Paper payoff/player, Table 2 | Saved notebook payoff vector | Traceability |
|---:|---:|---|---|
| 2 | 2.50 | (2.48, 2.50) | Matches one rounded player estimate; the saved mean is 2.49 |
| 3 | 4.68 | (4.56, 4.58, 4.72) | Exact reported value is not in this saved vector; its mean is 4.62 |
| 4 | 6.73 | (6.73, 7.02, 6.85, 7.02) | Matches one player estimate; the saved mean is 6.905 |

These historical optimizations are unseeded; their raw measurement counts and
final k = 3,4 parameters were not saved as reusable data. A fresh simulation
cannot be described as an exact reproduction of those rounded estimates.
The original code uses 1,024 shots at k = 2 and 2,048 at k = 3,4, rather than
4,096 throughout. A statevector backend may still sample shots when measured.

The exact replay checks the original 7 × 7 heatmap domain. For k = 3 it finds
an average payoff of 4.59375 at a best grid point, consistent in scale with the
paper's sampled heatmap near 4.6. This is a grid maximum, not the old optimizer's
result or a proof of a global optimum. Additional k = 2,4 7 × 7 scans in the
companion are labeled as new diagnostic checks, not experiments reported in
the manuscript.

The uniform circuit is invariant under flipping all bits, so expected
cooperation, defined as the fraction of players choosing C, is 50% for every
parameter choice. The paper's 67% and 75% entries do not match that metric.
Its QAOA “equilibrium frequency” entries also have no unilateral-deviation
check. They should be described only as outcome frequencies when the underlying
counts and event definitions are available.

Using the paper's reported QAOA values with the actual pairwise Nash baseline
would give differences 1.50, 2.68, and 3.73, not 1.50, 3.68, and 5.73. This is
an arithmetic correction to reported values, not validation of those values.
There is no matched optimizer/runtime benchmark establishing speedup.

## Schelling coordination

Most of Table 3 (p. 7) is traceable to the saved notebook and agrees with the
ideal circuit up to sampling noise.

| Case | Paper classical | Paper quantum, without inverse | Exact classical expectation | Exact quantum expectation |
|---|---:|---:|---:|---:|
| Two spots, unbiased | 0.503 | 1.000 | 0.500 | 1.000 |
| Shared classical p = 0.7; equal quantum rotations | 0.578 | 1.000 | 0.580 | 1.000 |
| Shared classical p = 0.9; equal quantum rotations | 0.821 | 1.000 | 0.820 | 1.000 |
| Individual classical p = (0.8,0.2); quantum angles (π/6,0) | 0.321 | 0.936 | 0.320 | 0.9330127 |
| Quantum angles (π/2,0) | — | 0.487 | Unspecified in Table 3 | 0.500 |
| Four spots, unbiased | 0.252 | 1.000 | 0.250 | 1.000 |

The classical probabilities and quantum rotation angles are different
parameterizations; rows do not establish that the marginals are matched.
The saved π/6 quantum output is **0.934**, rather than the paper's 0.936.
Both are plausible sampled observations around 0.9330127; no raw counts or seed
establish that 0.936 came from the archived run. Table 3 gives no classical
baseline for π/2, while §4.2.3 supplies 0.250 without matching parameters.

For a Bell pair with real Ry rotations, the no-inverse match probability is
`cos²((theta_A - theta_B)/2)`. With the inverse circuit used here, measurement
has support only on 00 and 11, giving match probability 1 for all these rotations.
That inverse includes a joint two-qubit gate; it is a different coordination
protocol from separated local measurements. Shared classical randomness can
also achieve perfect matching, so comparison with independent random choices
alone does not establish a uniquely quantum coordination benefit.

Further method details needing alignment:

- Classical examples use 10,000 samples, but the quantum examples shown in the
  notebook use 1,000 shots, not the paper's stated 10,000.
- The bias curve maps `|pA-pB| / 0.8` to an angle in [0,π/2]. At its endpoint
  pA = 1, pB = 0.2, the plotted expectations are classical 0.2 and quantum 0.5;
  the curves do not reach parity as stated on p. 8. This continuous mapping
  also differs from the table's example pairing (0.8,0.2) with (π/6,0).
- `count_ops()` in the notebook counts measurements. The four-spot no-inverse
  circuit contains two H gates, two CX gates, and four measurements: eight
  operations total, not eight single-qubit gates plus two CX gates. Counts for
  inverse variants are larger. No noise model or hardware run validates the
  manuscript's >96% device-success estimate.
- The unfinished `statsmodels` cell uses assumed integer counts reconstructed
  from rounded rates. The maintained companion uses exact circuit probabilities
  and makes no statistical-significance claim from those assumed counts.

## Runtime, environment, and missing evidence

The original k = 4 sweep prints **3,036.22 seconds** (about 50.6 minutes) for
18,974,736 profiles, supporting the paper's “under an hour” statement for the
saved run. It does not independently verify the CPU type or worker deployment.
The paper also describes five hours on an M1 and, elsewhere, five hours on a
30-core cloud machine. No retained benchmark establishes both timings on the
same grid and implementation. The k = 4 analysis prints 30 historical profiles,
but the source pickle is absent, so that output cannot be rerun from the original
inputs.

The 15 × 8 notebook prints about **11.79 s** for k = 2 and **1,836.17 s** for
k = 3. The paper's 13.8 s k = 3 entry belongs to the earlier 7 × 4 experiment.
Its runtime figure is assembled from manually entered values (453.09, 13.78,
18,000 s), so it is not a controlled scaling comparison across the final grids.
The finer k = 4 grid mentioned on p. 9 contains `(31 × 16)^4 = 60,523,872,256`
profiles, roughly 60.5 billion; “over 450 million” substantially understates its size.

The paper lists Python 3.11.4, Qiskit 0.46.1, and Aer 0.13.3. The notebooks do
not record a complete environment lock. The maintained environment is pinned
separately in `uv.lock`; modern statevector checks are not evidence of execution
under the reported historical versions. Likewise, quoted CX counts need an
identified circuit, transpilation configuration, and measurement convention.

## Alignment needed in the manuscript

Repository cleanup can make the evidence traceable, but cannot make contradictory
results identical. To align the manuscript with the code, its methods and tables
need the corrections above. In particular, the PD result can be stated as:

> The implemented diagonal-ZZ circuit produced phase-independent outcome
> probabilities. After correcting player-payoff indexing and retaining all tied
> best responses, exhaustive searches on the stated grids found all-defection
> as the equilibrium behavior for two, three, and four players. The previously
> reported cooperative and single-defector profiles fail a unilateral-deviation
> test. The QAOA track optimized sampled aggregate payoff and did not certify
> Nash equilibria.

The Schelling result can retain its ideal-circuit match-rate finding while
specifying the sampling budget, bias mapping, comparison with independent
classical choices, and joint operations in the inverse variant. Application
claims on pp. 9–10, “largest to date,” and hardware/economic gains have not been
validated by these code checks. This review covers the computational methods
and traceable results; it does not fact-check the manuscript's external examples.
