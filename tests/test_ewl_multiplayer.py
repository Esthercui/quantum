"""Validate the all-pairs extension and its full-grid/continuous Nash certificates."""

from itertools import product
from math import pi

import numpy as np
import pytest
from numpy.testing import assert_allclose

from quantum_pd import classical_payoff, pure_nash_mask
from quantum_pd.ewl import C, D, Q, batch_probabilities, expected_payoff, probabilities
from quantum_pd.ewl_search import best_response, grid_payoffs


@pytest.mark.parametrize("players", [2, 3, 4])
@pytest.mark.parametrize("gamma", [0, 0.37, pi / 2])
@pytest.mark.parametrize("model", ["collective", "pairwise"])
def test_classical_embedding_and_batched_probabilities(players, gamma, model):
    profiles = np.array(
        [[(pi * a, 0) for a in actions] for actions in product(range(2), repeat=players)]
    )
    batch = batch_probabilities(profiles, gamma)
    for angles, probs in zip(profiles, batch, strict=True):
        assert_allclose(probs, probabilities(angles, gamma), atol=1e-12)
        actions = (angles[:, 0] > 0).astype(int)
        assert_allclose(
            expected_payoff(angles, gamma, model=model),
            classical_payoff(actions, model),
            atol=1e-12,
        )


@pytest.mark.parametrize("players", [2, 3, 4])
def test_all_q_continuous_payoff_formula(players):
    for theta, phi in product(np.linspace(0, pi, 7), np.linspace(0, pi / 2, 6)):
        a = np.cos(theta / 2) * np.cos(phi)
        b = np.sin(theta / 2)
        c = np.cos(theta / 2) * np.sin(phi)
        target = 3 * c * c + (a * a if players % 2 == 0 else b * b)
        assert_allclose(
            expected_payoff([(theta, phi)] + [Q] * (players - 1))[0], target, atol=1e-12
        )
    for player in range(players):
        assert_allclose(best_response([Q] * players, player)["payoff"], 3, atol=1e-12)
    assert_allclose(expected_payoff([D] + [Q] * (players - 1))[0], players % 2, atol=1e-12)


@pytest.mark.parametrize("players", [2, 3, 4])
def test_batched_grid_against_individual_statevectors(players):
    grid, tensor = grid_payoffs(players, theta_points=3, phi_points=3, batch_size=17)
    rng = np.random.default_rng(124)
    for indices in rng.integers(0, len(grid), size=(16, players)):
        assert_allclose(tensor[tuple(indices)], expected_payoff(grid[indices]), atol=1e-12)
    assert pure_nash_mask(tensor)[(2,) * players]


@pytest.mark.parametrize("players", [2, 3, 4])
def test_continuous_response_attains_value_and_dominates_dense_samples(players):
    rng = np.random.default_rng(230)
    deviations = np.array(list(product(np.linspace(0, pi, 41), np.linspace(0, pi / 2, 33))))
    for _ in range(6):
        profile = rng.random((players, 2)) * [pi, pi / 2]
        for player in range(players):
            response = best_response(profile, player)
            trial = profile.copy()
            trial[player] = response["angles"]
            assert_allclose(expected_payoff(trial)[player], response["payoff"], atol=1e-11)
            samples = np.broadcast_to(profile, (len(deviations), players, 2)).copy()
            samples[:, player] = deviations
            from quantum_pd.game import outcomes

            weights = np.array([classical_payoff(b)[player] for b in outcomes(players)])
            sampled = batch_probabilities(samples) @ weights
            assert sampled.max() <= response["payoff"] + 1e-11


def test_response_with_degenerate_payoff_faces():
    # Classical opponent D makes all phases at theta=pi tied.
    response = best_response([C, D], 0, gamma=0)
    assert_allclose(response["payoff"], 1, atol=1e-12)


def test_large_grid_rejected_before_allocation():
    with pytest.raises(ValueError, match="profiles; limit"):
        grid_payoffs(4, theta_points=31, phi_points=16)
