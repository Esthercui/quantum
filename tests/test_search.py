"""Compare the reduced search with unreduced games and direct deviations."""

from itertools import product

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from quantum_pd.game import expected_payoff
from quantum_pd.search import classical_nash, pure_nash_mask, search_grid


def test_all_tied_best_responses_are_kept():
    assert pure_nash_mask(np.ones((3, 2, 2))).all()


def test_matching_pennies_has_no_pure_equilibrium():
    table = np.array([[[1, -1], [-1, 1]], [[-1, 1], [1, -1]]])
    assert not pure_nash_mask(table).any()


def test_absolute_tolerance_has_no_implicit_relative_component():
    table = np.zeros((2, 2, 2))
    table[..., 0] = 1e6
    table[1, :, 0] += 1e-5
    assert not pure_nash_mask(table, atol=1e-6)[0].any()
    assert pure_nash_mask(table, atol=1e-4).all()


def test_tensor_reduction_matches_independent_deviation_loop():
    rng = np.random.default_rng(27)
    table = rng.integers(0, 5, size=(3, 2, 4, 3))
    expected = np.ones((3, 2, 4), dtype=bool)
    for profile in product(range(3), range(2), range(4)):
        for player, choices in enumerate((3, 2, 4)):
            for alternative in range(choices):
                deviation = list(profile)
                deviation[player] = alternative
                if table[tuple(deviation)][player] > table[profile][player]:
                    expected[profile] = False
    assert_array_equal(pure_nash_mask(table, atol=0), expected)


@pytest.mark.parametrize("players", [2, 3, 4])
@pytest.mark.parametrize("model", ["collective", "pairwise"])
def test_full_phase_grid_matches_reduced_search(players, model):
    grid = list(product(np.linspace(0, np.pi, 3), [0, np.pi / 2]))
    table = np.empty((len(grid),) * players + (players,))
    for profile in product(range(len(grid)), repeat=players):
        table[profile] = expected_payoff([grid[i] for i in profile], model)
    unreduced = {tuple(p) for p in np.argwhere(pure_nash_mask(table))}
    reduced = search_grid(players, theta_points=3, phi_points=2, model=model)
    expanded = set()
    for equilibrium in reduced["equilibrium_classes"]:
        for phases in product(range(2), repeat=players):
            expanded.add(
                tuple(2 * t + p for t, p in zip(equilibrium["theta_indices"], phases, strict=True))
            )
    assert expanded == unreduced
    assert len(unreduced) == reduced["equilibrium_angle_profiles"] == 2**players


@pytest.mark.parametrize("players", [2, 3, 4])
@pytest.mark.parametrize("model", ["collective", "pairwise"])
def test_historical_grid_and_classical_baseline(players, model):
    # Historical high-resolution grids: 15x8 for k=2,3; 11x6 for k=4.
    theta, phi = (11, 6) if players == 4 else (15, 8)
    result = search_grid(players, theta_points=theta, phi_points=phi, model=model)
    assert result["full_angle_profiles"] == (theta * phi) ** players
    assert result["evaluated_representatives"] == theta**players
    assert result["equilibrium_angle_profiles"] == phi**players
    assert len(result["equilibrium_classes"]) == 1
    equilibrium = result["equilibrium_classes"][0]
    assert equilibrium["theta_indices"] == [theta - 1] * players
    payoff = 1 if model == "collective" else players - 1
    assert equilibrium["payoffs"] == [payoff] * players
    assert equilibrium["unilateral_regrets"] == [0] * players
    assert classical_nash(players, model) == [
        {"actions": [1] * players, "payoffs": [payoff] * players}
    ]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"players": 1},
        {"players": True},
        {"players": 2.5},
        {"theta_points": 1},
        {"theta_points": 2.5},
        {"phi_points": 0},
        {"atol": -1},
        {"atol": np.nan},
        {"model": "other"},
        {"max_profiles": 0},
    ],
)
def test_invalid_configuration_is_rejected(kwargs):
    config = {"players": 4, **kwargs}
    with pytest.raises(ValueError):
        search_grid(**config)


def test_large_search_fails_before_allocation():
    with pytest.raises(ValueError, match="limit"):
        search_grid(4, theta_points=100_000)


@pytest.mark.parametrize(
    "table",
    [np.zeros((2, 2)), np.zeros((0, 2, 2)), np.zeros((2, 2, 3)), np.full((2, 2, 2), np.nan)],
)
def test_invalid_payoff_tensor_is_rejected(table):
    with pytest.raises(ValueError):
        pure_nash_mask(table)
