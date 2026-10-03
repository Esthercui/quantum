"""EWL game and its explicit all-pairs extension to two through four players.

Conventions follow equations (3), (5), and (7) of quant-ph/9806088v4:
U = [[exp(i phi) cos(theta/2), sin(theta/2)],
     [-sin(theta/2), exp(-i phi) cos(theta/2)]];
J = product_{i<j} exp(-i gamma D_i D_j/2), D = U(pi, 0).
For k=2 this is the standard EWL protocol. For k>2 it specifies the
all-pairs extension used in this study; it is not a unique multiplayer model.
Player i owns qubit i, matching the rest of the package's little-endian arrays.
"""

from functools import lru_cache
from itertools import combinations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .game import PayoffModel, _angles, _gamma, classical_payoff, outcomes, validate_players

C = (0.0, 0.0)
D = (np.pi, 0.0)
Q = (0.0, np.pi / 2)


def strategy(theta: float, phi: float) -> NDArray[np.complex128]:
    """Return U(theta, phi) for theta in [0, pi], phi in [0, pi/2]."""
    _angles([(theta, phi), C])
    cosine, sine = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[np.exp(1j * phi) * cosine, sine], [-sine, np.exp(-1j * phi) * cosine]])


@lru_cache(maxsize=32)
def entangler(players: int, gamma: float = np.pi / 2) -> NDArray:
    """All-pairs J matrix in little-endian basis order; returned array is read-only."""
    validate_players(players)
    _gamma(gamma)
    indices = np.arange(2**players)
    z = 1 - 2 * outcomes(players)
    matrix = np.eye(2**players, dtype=complex)
    for i, j in combinations(range(players), 2):
        flipped = indices ^ (1 << i) ^ (1 << j)
        sign = (z[:, i] * z[:, j])[:, None]
        matrix = np.cos(gamma / 2) * matrix - 1j * np.sin(gamma / 2) * sign * matrix[flipped]
    matrix.flags.writeable = False
    return matrix


def statevector(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Apply J, each player's strategy, then J† to the initial all-zero state."""
    angles = _angles(strategies)
    matrix = entangler(len(angles), gamma)
    local = np.array([[1.0 + 0j]])
    for theta, phi in reversed(angles):
        local = np.kron(local, strategy(theta, phi))
    return matrix.conj().T @ local @ matrix[:, 0]


def probabilities(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Born probabilities in little-endian statevector order."""
    return np.abs(statevector(strategies, gamma)) ** 2


def expected_payoff(
    strategies: ArrayLike, gamma: float = np.pi / 2, *, model: PayoffModel = "collective"
) -> NDArray:
    """Expected payoffs in player order, using one explicit rule for every outcome."""
    probs = probabilities(strategies, gamma)
    table = np.array([classical_payoff(bits, model) for bits in outcomes(len(strategies))])
    return probs @ table


def batch_probabilities(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Evaluate a bounded batch of full angle profiles, without phase reduction.

    Input shape is (profiles, players, 2). Local operations are applied by
    tensor slices, avoiding a separate Kronecker matrix per profile.
    """
    angles = np.asarray(strategies, dtype=float)
    if angles.ndim != 3 or angles.shape[2] != 2 or len(angles) == 0:
        raise ValueError("strategies must have shape (profiles, players, 2), with profiles > 0")
    players = angles.shape[1]
    validate_players(players)
    if not np.isfinite(angles).all() or (angles < 0).any() or (angles > [np.pi, np.pi / 2]).any():
        raise ValueError("finite theta in [0, pi] and phi in [0, pi/2] are required")
    matrix = entangler(players, gamma)
    state = np.broadcast_to(matrix[:, 0], (len(angles), 2**players)).copy()
    for player in range(players):
        theta, phi = angles[:, player].T
        cosine = np.cos(theta / 2)[:, None, None]
        sine = np.sin(theta / 2)[:, None, None]
        phase = np.exp(1j * phi)[:, None, None]
        view = state.reshape(len(angles), -1, 2, 2**player)
        zero, one = view[:, :, 0, :].copy(), view[:, :, 1, :].copy()
        view[:, :, 0, :] = phase * cosine * zero + sine * one
        view[:, :, 1, :] = -sine * zero + phase.conj() * cosine * one
    state = state @ matrix.conj()
    return np.abs(state) ** 2
