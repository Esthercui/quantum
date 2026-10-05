"""Exhaustive pure Nash search with all tied best responses retained."""

from itertools import product

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .game import PayoffModel, classical_payoff, outcomes, validate_model, validate_players


def pure_nash_mask(payoffs: ArrayLike, atol: float = 1e-10) -> NDArray[np.bool_]:
    """Find profiles with no unilateral improvement greater than absolute atol.

    Input shape is (strategies_player_0, ..., strategies_player_k_minus_1, k).
    Return a boolean array with one entry per profile. All tied best responses
    qualify; selecting just one argmax can incorrectly discard equilibria.
    """
    table = np.asarray(payoffs, dtype=float)
    if table.ndim < 3 or table.shape[-1] != table.ndim - 1 or 0 in table.shape:
        raise ValueError("payoffs must have one strategy axis per player and a final player axis")
    if not np.isfinite(table).all():
        raise ValueError("payoffs must be finite")
    if not np.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    mask = np.ones(table.shape[:-1], dtype=bool)
    for player in range(table.shape[-1]):
        values = table[..., player]
        best = values.max(axis=player, keepdims=True)
        mask &= best - values <= atol
    return mask


def classical_nash(players: int, model: PayoffModel = "collective") -> list[dict]:
    """Enumerate classical pure equilibria for the same payoff model as the circuit."""
    validate_players(players)
    validate_model(model)
    table = np.empty((2,) * players + (players,))
    for profile in product(range(2), repeat=players):
        table[profile] = classical_payoff(profile, model)
    pure_mask = pure_nash_mask(table)
    return [
        {"actions": list(profile), "payoffs": table[profile].tolist()}
        for profile in product(range(2), repeat=players)
        if pure_mask[profile]
    ]


def _positive_int(value: int, name: str, minimum: int = 1) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def search_grid(
    players: int,
    *,
    theta_points: int = 11,
    phi_points: int = 6,
    model: PayoffModel = "collective",
    atol: float = 1e-10,
    max_profiles: int = 1_000_000,
) -> dict:
    """Search the entire angle grid after an exact phase-equivalence reduction.

    theta spans [0, pi]; phi spans [0, pi/2] (or {0} when phi_points = 1).
    All phi values have identical payoffs at fixed theta for this circuit.
    Evaluate theta_points**players representatives and count every represented
    angle profile. This reduction is specific to the historical diagonal circuit.

    The resource bound applies before any grid or payoff tensor is allocated.
    Returned regrets certify only the specified finite grid and tolerance.
    """
    validate_players(players)
    validate_model(model)
    _positive_int(theta_points, "theta_points", 2)
    _positive_int(phi_points, "phi_points")
    _positive_int(max_profiles, "max_profiles")
    if not np.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and nonnegative")
    profiles = theta_points**players
    if profiles > max_profiles:
        raise ValueError(
            f"search requires {profiles:,} reduced profiles; limit is {max_profiles:,}. "
            "Use fewer theta points or explicitly increase max_profiles."
        )

    theta = np.linspace(0, np.pi, theta_points)
    defect = np.sin(theta / 2) ** 2
    payoff_table = np.array([classical_payoff(bits, model) for bits in outcomes(players)])
    table = np.zeros((theta_points,) * players + (players,))
    # Accumulate one basis outcome at a time; no list of profile tuples or futures.
    for bits, payoff in zip(outcomes(players), payoff_table, strict=True):
        probability = np.ones((theta_points,) * players)
        for player, bit in enumerate(bits):
            axis_shape = [1] * players
            axis_shape[player] = theta_points
            marginal = defect if bit else 1 - defect
            probability *= marginal.reshape(axis_shape)
        table += probability[..., None] * payoff

    mask = pure_nash_mask(table, atol)
    best = [table[..., p].max(axis=p, keepdims=True) for p in range(players)]
    equilibria = []
    for indices in np.argwhere(mask):
        profile = tuple(indices)
        regrets = []
        for p in range(players):
            opponents = list(profile)
            opponents[p] = 0
            regrets.append(float(max(0, best[p][tuple(opponents)] - table[profile][p])))
        equilibria.append(
            {
                "theta_indices": indices.tolist(),
                "representative_angles": [[float(theta[i]), 0.0] for i in profile],
                "payoffs": table[profile].tolist(),
                "unilateral_regrets": regrets,
                "represented_angle_profiles": phi_points**players,
            }
        )
    return {
        "schema_version": 1,
        "circuit": "pairwise-zz-ry-rz",
        "players": players,
        "payoff_model": model,
        "theta_points": theta_points,
        "phi_points": phi_points,
        "theta_range_radians": [0.0, float(np.pi)],
        "phi_range_radians": [0.0, float(np.pi / 2) if phi_points > 1 else 0.0],
        "gamma_range_radians": [0.0, float(np.pi / 2)],
        "absolute_tolerance": atol,
        "full_angle_profiles": (theta_points * phi_points) ** players,
        "evaluated_representatives": profiles,
        "phase_multiplicity_per_representative": phi_points**players,
        "equilibrium_classes": equilibria,
        "equilibrium_angle_profiles": len(equilibria) * phi_points**players,
        "classical_equilibria": classical_nash(players, model),
    }
