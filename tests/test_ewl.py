"""Classical embedding, quantum responses, and the continuous EWL Nash bound."""

from itertools import product
from math import pi

import numpy as np
import pytest
from numpy.testing import assert_allclose

from quantum_pd import classical_payoff, pure_nash_mask
from quantum_pd.ewl import C, D, Q, expected_payoff, probabilities, statevector, strategy


@pytest.mark.parametrize("gamma", [0, 0.43, pi / 2])
def test_classical_embedding(gamma):
    for actions in product(range(2), repeat=2):
        angles = [(pi * action, 0) for action in actions]
        assert_allclose(expected_payoff(angles, gamma), classical_payoff(actions), atol=1e-12)


@pytest.mark.parametrize(
    "profile,payoffs", [([C, D], [0, 5]), ([Q, D], [5, 0]), ([D, Q], [0, 5]), ([Q, Q], [3, 3])]
)
def test_named_strategies(profile, payoffs):
    assert_allclose(expected_payoff(profile), payoffs, atol=1e-12)


def test_continuous_best_response_formula_against_q():
    # Equation (8) and the following Nash argument in Eisert et al.
    for theta, phi in product(np.linspace(0, pi, 15), np.linspace(0, pi / 2, 8)):
        expected = np.cos(theta / 2) ** 2 * (3 * np.sin(phi) ** 2 + np.cos(phi) ** 2)
        assert_allclose(expected_payoff([(theta, phi), Q])[0], expected, atol=1e-12)
        assert_allclose(expected_payoff([Q, (theta, phi)])[1], expected, atol=1e-12)
        assert expected <= 3 + 1e-12


def test_complete_two_player_grid():
    grid = list(product(np.linspace(0, pi, 15), np.linspace(0, pi / 2, 8)))
    payoffs = np.array([[expected_payoff([a, b]) for b in grid] for a in grid])
    # Q has index 7: theta=0 and phi=pi/2. Phases are fully enumerated.
    assert np.argwhere(pure_nash_mask(payoffs)).tolist() == [[7, 7]]


def test_unitarity_and_normalization():
    for theta, phi in [(0.1, 0.2), (1.7, 1.1), Q, D]:
        unitary = strategy(theta, phi)
        assert_allclose(unitary.conj().T @ unitary, np.eye(2), atol=1e-12)
        assert_allclose(probabilities([(theta, phi), (0.7, 1.2)]).sum(), 1, atol=1e-12)


@pytest.mark.parametrize(
    "angles,gamma",
    [([C, D, Q, C, D], pi / 2), ([(0, -0.1), C], 0), ([C, Q], np.nan), ([C, Q], -1)],
)
def test_invalid_inputs(angles, gamma):
    with pytest.raises(ValueError):
        statevector(angles, gamma)
