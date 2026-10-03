"""Scientific invariants and regressions for payoff and player conventions."""

from itertools import product

import numpy as np
import pytest
from numpy.testing import assert_allclose

from quantum_pd.game import classical_payoff, expected_payoff, outcomes, probabilities, statevector


@pytest.mark.parametrize(
    ("actions", "payoff"),
    [((0, 0), (3, 3)), ((0, 1), (0, 5)), ((1, 0), (5, 0)), ((1, 1), (1, 1))],
)
@pytest.mark.parametrize("model", ["pairwise", "collective"])
def test_two_player_payoff_matrix(actions, payoff, model):
    assert_allclose(classical_payoff(actions, model), payoff)


def test_multiplayer_games_are_distinct():
    assert_allclose(classical_payoff((1, 0, 0), "collective"), [5, 0, 0])
    assert_allclose(classical_payoff((1, 0, 0), "pairwise"), [10, 3, 3])
    assert_allclose(classical_payoff((1, 1, 1, 1), "pairwise"), [3] * 4)


@pytest.mark.parametrize("players", [2, 3, 4])
@pytest.mark.parametrize("model", ["pairwise", "collective"])
def test_every_classical_profile_embeds_with_correct_player_order(players, model):
    for actions in product([0, 1], repeat=players):
        angles = [(np.pi * bit, 0.37) for bit in actions]
        assert_allclose(
            expected_payoff(angles, model), classical_payoff(actions, model), atol=1e-12
        )


def test_player_zero_is_the_least_significant_bit():
    assert outcomes(4)[1].tolist() == [1, 0, 0, 0]
    assert_allclose(probabilities([(np.pi, 0), (0, 0)]), [0, 1, 0, 0], atol=1e-12)
    assert_allclose(expected_payoff([(np.pi, 0), (0, 0)]), [5, 0], atol=1e-12)


@pytest.mark.parametrize("players", [2, 3, 4])
def test_phases_do_not_change_probabilities(players):
    rng = np.random.default_rng(73 + players)
    for _ in range(10):
        strategies = rng.random((players, 2)) * [np.pi, np.pi / 2]
        reference = probabilities(strategies)
        for gamma in (0, 0.37, np.pi / 2):
            assert_allclose(abs(statevector(strategies, gamma)) ** 2, reference, atol=1e-12)
        assert_allclose(reference.sum(), 1, atol=1e-12)
        strategies[:, 1] = 0
        assert_allclose(probabilities(strategies, 0), reference, atol=1e-12)


@pytest.mark.parametrize("model", ["pairwise", "collective"])
def test_relabeling_players_relabels_payoffs(model):
    angles = np.array([[0.2, 0.1], [1.3, 0.7], [2.1, 1.1], [3.0, 0.4]])
    permutation = [2, 0, 3, 1]
    assert_allclose(
        expected_payoff(angles[permutation], model),
        expected_payoff(angles, model)[permutation],
        atol=1e-12,
    )


@pytest.mark.parametrize("actions", [[0], [0, 2], [0, np.nan], [[0, 1]], [0] * 5])
def test_invalid_actions_are_rejected(actions):
    with pytest.raises(ValueError):
        classical_payoff(actions)


@pytest.mark.parametrize(
    "angles", [[[0, 0]], [[0, 0], [np.nan, 0]], [[0, 0], [4, 0]], [[0, 0], [0, -1]], [0, 1]]
)
def test_invalid_angles_are_rejected(angles):
    with pytest.raises(ValueError):
        probabilities(angles)


@pytest.mark.parametrize("gamma", [-1, 2, np.inf, np.nan])
def test_invalid_gamma_is_rejected(gamma):
    with pytest.raises(ValueError):
        probabilities([[0, 0], [0, 0]], gamma)
