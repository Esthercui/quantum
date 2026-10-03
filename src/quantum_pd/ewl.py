"""Two-player Eisert–Wilkens–Lewenstein game, restricted two-angle strategies.

Conventions follow equations (3), (5), and (7) of quant-ph/9806088v4:
U = [[exp(i phi) cos(theta/2), sin(theta/2)],
     [-sin(theta/2), exp(-i phi) cos(theta/2)]];
J = exp(-i gamma D⊗D/2), D = U(pi, 0).
Player i owns qubit i, matching the rest of the package's little-endian arrays.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .game import _angles, _gamma, classical_payoff, outcomes

C = (0.0, 0.0)
D = (np.pi, 0.0)
Q = (0.0, np.pi / 2)


def strategy(theta: float, phi: float) -> NDArray[np.complex128]:
    """Return U(theta, phi) for theta in [0, pi], phi in [0, pi/2]."""
    _angles([(theta, phi), C])
    cosine, sine = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[np.exp(1j * phi) * cosine, sine], [-sine, np.exp(-1j * phi) * cosine]])


def statevector(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Apply J, both players' strategies, then J† to the initial state |00>."""
    angles = _angles(strategies)
    if len(angles) != 2:
        raise ValueError("the EWL reference requires exactly two players")
    _gamma(gamma)
    defect = np.array([[0, 1], [-1, 0]], dtype=complex)
    entangler = np.cos(gamma / 2) * np.eye(4) - 1j * np.sin(gamma / 2) * np.kron(defect, defect)
    local = np.kron(strategy(*angles[1]), strategy(*angles[0]))
    return entangler.conj().T @ local @ entangler[:, 0]


def probabilities(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Born probabilities in statevector order (00, 01, 10, 11)."""
    return np.abs(statevector(strategies, gamma)) ** 2


def expected_payoff(strategies: ArrayLike, gamma: float = np.pi / 2) -> NDArray:
    """Two-player expected payoffs, ordered by player, without shot sampling."""
    table = np.array([classical_payoff(bits) for bits in outcomes(2)])
    return probabilities(strategies, gamma) @ table
