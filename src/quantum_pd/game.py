"""The payoff rules and the pairwise-ZZ circuit used in the original notebooks.

Player i owns qubit i. Array index x denotes outcome bit i = (x >> i) & 1.
The circuit is J† (⊗ Rz(phi_i) Ry(theta_i)) J |0...0>, where
J = exp(-i gamma sum_{i<j} Z_i Z_j). See docs/methods.md for its reduction.
"""

from itertools import combinations
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

PayoffModel = Literal["collective", "pairwise"]
# Rows: own action; columns: opponent action. C = 0, D = 1.
PAIR_PAYOFF = np.array([[3.0, 0.0], [5.0, 1.0]])


def validate_players(players: int) -> None:
    """Keep the public API within the researched two- to four-player scope."""
    if isinstance(players, bool) or not isinstance(players, (int, np.integer)):
        raise ValueError("players must be an integer in {2, 3, 4}")
    if players not in (2, 3, 4):
        raise ValueError("players must be 2, 3, or 4")


def validate_model(model: str) -> None:
    if model not in ("collective", "pairwise"):
        raise ValueError("payoff model must be 'collective' or 'pairwise'")


def outcomes(players: int) -> NDArray[np.int64]:
    """Return all outcomes in statevector order, with columns in player order."""
    validate_players(players)
    return (np.arange(2**players)[:, None] >> np.arange(players)) & 1


def classical_payoff(actions: ArrayLike, model: PayoffModel = "collective") -> NDArray:
    """Payoff for one action profile, ordered by player (0 = C, 1 = D).

    Collective: everyone gets 3 at all-C, 1 at all-D; otherwise defectors
    get 5 and cooperators get 0. Pairwise: sum ordinary PD across all pairs.
    These are different games for more than two players.
    """
    bits = np.asarray(actions)
    if bits.ndim != 1:
        raise ValueError("actions must be a one-dimensional profile")
    validate_players(len(bits))
    validate_model(model)
    if not np.isin(bits, [0, 1]).all():
        raise ValueError("each action must be 0 (cooperate) or 1 (defect)")
    bits = bits.astype(int)
    if model == "collective":
        if np.all(bits == 0):
            return np.full(len(bits), 3.0)
        if np.all(bits == 1):
            return np.ones(len(bits))
        return np.where(bits == 1, 5.0, 0.0)
    pay = np.zeros(len(bits))
    for i, j in combinations(range(len(bits)), 2):
        pay[i] += PAIR_PAYOFF[bits[i], bits[j]]
        pay[j] += PAIR_PAYOFF[bits[j], bits[i]]
    return pay


def _angles(strategies: ArrayLike) -> NDArray[np.float64]:
    angles = np.asarray(strategies, dtype=float)
    if angles.ndim != 2 or angles.shape[1] != 2:
        raise ValueError("strategies must have shape (players, 2): (theta, phi)")
    validate_players(len(angles))
    if not np.isfinite(angles).all():
        raise ValueError("strategy angles must be finite")
    if (angles < 0).any() or (angles > [np.pi, np.pi / 2]).any():
        raise ValueError("theta must lie in [0, pi] and phi in [0, pi/2]")
    return angles


def _gamma(gamma: float) -> None:
    if not np.isfinite(gamma) or not 0 <= gamma <= np.pi / 2:
        raise ValueError("gamma must be finite and lie in [0, pi/2]")


def probabilities(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Exact Born probabilities of the historical diagonal circuit.

    For this circuit only, phi and gamma cannot change measurement probabilities.
    Evaluate the proven product formula instead of simulating redundant phases.
    'Exact' means no shot sampling; numerical values use float64 arithmetic.
    """
    angles = _angles(strategies)
    _gamma(gamma)
    defect = np.sin(angles[:, 0] / 2) ** 2
    return np.prod(np.where(outcomes(len(angles)), defect, 1 - defect), axis=1)


def statevector(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Complex amplitudes of the actual pairwise-ZZ circuit, including its phases.

    This reference retains the diagonal gates even though probabilities() can
    remove them. Qiskit gate-level tests check both amplitudes and probabilities.
    """
    angles = _angles(strategies)
    _gamma(gamma)
    state = np.array([1.0 + 0j])
    for theta, phi in reversed(angles):
        local = np.array(
            [np.exp(-0.5j * phi) * np.cos(theta / 2), np.exp(0.5j * phi) * np.sin(theta / 2)]
        )
        state = np.kron(state, local)
    z = 1 - 2 * outcomes(len(angles))
    pair_sum = sum(z[:, i] * z[:, j] for i, j in combinations(range(len(angles)), 2))
    initial_pair_sum = len(angles) * (len(angles) - 1) // 2
    return state * np.exp(1j * gamma * (pair_sum - initial_pair_sum))


def expected_payoff(
    strategies: ArrayLike, model: PayoffModel = "collective", gamma: float = np.pi / 2
) -> NDArray:
    """Return each player's expected payoff under the selected payoff rule."""
    probs = probabilities(strategies, gamma)
    table = np.array([classical_payoff(bits, model) for bits in outcomes(len(strategies))])
    return probs @ table
