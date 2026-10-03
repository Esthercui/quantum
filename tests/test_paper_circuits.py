"""Independent model identities for the manuscript companion circuits."""

from math import pi

import numpy as np
import pytest
from numpy.testing import assert_allclose

from quantum_pd.experiments import (
    classical_match,
    qaoa_outcomes,
    schelling_four_spots,
    schelling_probabilities,
)

pytest.importorskip("qiskit")


@pytest.mark.parametrize("players", [2, 3, 4])
def test_qaoa_bit_complement_symmetry_implies_half_cooperation(players):
    for gamma, beta in [(0, 0), (0.32, 0.71), (1.17, 2.49)]:
        result = qaoa_outcomes(players, gamma, beta)
        assert_allclose(result["cooperation_rate"], 0.5, atol=1e-12)
        assert_allclose(result["payoffs"], [result["mean_payoff"]] * players, atol=1e-12)
        assert result["cx_count_before_transpilation"] == players * (players - 1)


def test_qaoa_two_player_known_optimum():
    result = qaoa_outcomes(2, pi / 4, 3 * pi / 8)
    assert_allclose(result["payoffs"], [2.5, 2.5], atol=1e-12)


@pytest.mark.parametrize("a,b", [(0, 0), (pi / 6, pi / 6), (pi / 6, 0), (pi / 2, 0), (0.7, 1.2)])
def test_schelling_matches_analytic_rotation_difference(a, b):
    raw = schelling_probabilities(a, b)
    assert_allclose(raw[0] + raw[3], np.cos((a - b) / 2) ** 2, atol=1e-12)
    decoded = schelling_probabilities(a, b, undo=True)
    assert_allclose(decoded[0] + decoded[3], 1, atol=1e-12)


@pytest.mark.parametrize("undo,unitaries,cx", [(False, 4, 2), (True, 8, 4)])
def test_four_spot_register_match_and_operation_counts(undo, unitaries, cx):
    result = schelling_four_spots(undo=undo)
    assert_allclose(result["match_rate"], 1, atol=1e-12)
    assert result["unitary_gates"] == unitaries
    assert result["cx_count"] == cx
    assert result["measurement_operations"] == 4


def test_classical_bias_mapping_values():
    assert_allclose(
        [
            classical_match(0.5, 0.5),
            classical_match(0.7, 0.7),
            classical_match(0.9, 0.9),
            classical_match(0.8, 0.2),
        ],
        [0.5, 0.58, 0.82, 0.32],
    )
    assert_allclose(classical_match(1, 0.2), 0.2)
