"""Full-grid EWL enumeration and continuous unilateral-response certificates."""

from itertools import combinations, product

import numpy as np

from .ewl import C, D, Q, batch_probabilities, statevector
from .game import _angles, _gamma, classical_payoff, outcomes, validate_model, validate_players
from .search import _positive_int, pure_nash_mask


def grid_payoffs(
    players,
    *,
    theta_points=15,
    phi_points=8,
    gamma=np.pi / 2,
    model="collective",
    batch_size=32768,
    max_profiles=25_000_000,
    progress=None,
):
    """Evaluate every angle profile; return the strategy grid and payoff tensor.

    The k=4 manuscript grid uses about 607 MB for the float64 payoff tensor.
    Batching bounds temporary statevector storage. No phase equivalence is assumed.
    """
    validate_players(players)
    validate_model(model)
    _gamma(gamma)
    _positive_int(theta_points, "theta_points", 2)
    _positive_int(phi_points, "phi_points", 2)
    _positive_int(batch_size, "batch_size")
    _positive_int(max_profiles, "max_profiles")
    count = (theta_points * phi_points) ** players
    if count > max_profiles:
        raise ValueError(f"grid requires {count:,} profiles; limit is {max_profiles:,}")
    grid = np.array(
        list(product(np.linspace(0, np.pi, theta_points), np.linspace(0, np.pi / 2, phi_points)))
    )
    table = np.empty((count, players))
    payoff = np.array([classical_payoff(b, model) for b in outcomes(players)])
    shape = (len(grid),) * players
    for start in range(0, count, batch_size):
        stop = min(start + batch_size, count)
        indices = np.array(np.unravel_index(np.arange(start, stop), shape)).T
        table[start:stop] = batch_probabilities(grid[indices], gamma) @ payoff
        if progress is not None:
            progress(stop, count)
    return grid, table.reshape(shape + (players,))


def best_response(strategies, player, *, gamma=np.pi / 2, model="collective"):
    """Global best response within the continuous restricted EWL strategy family.

    Write U=a I+b D+c Q with a,b,c>=0 and a²+b²+c²=1. Expected payoff
    is a real 3x3 quadratic form. Its maximum on the positive sphere occurs
    at an eigenvector on one of its seven nonempty coordinate faces. Repeated
    eigenvalues also attain the same maximum on a lower-dimensional face.
    """
    angles = _angles(strategies).copy()
    validate_model(model)
    if isinstance(player, bool) or not isinstance(player, (int, np.integer)):
        raise ValueError("player must be an integer index")
    if not 0 <= player < len(angles):
        raise ValueError("player index out of range")
    basis = []
    for move in (C, D, Q):
        angles[player] = move
        basis.append(statevector(angles, gamma))
    basis = np.asarray(basis).T
    weights = np.array([classical_payoff(b, model)[player] for b in outcomes(len(angles))])
    matrix = np.real(basis.conj().T @ (weights[:, None] * basis))
    matrix = (matrix + matrix.T) / 2
    candidates = []
    for size in (1, 2, 3):
        for face in combinations(range(3), size):
            _, vectors = np.linalg.eigh(matrix[np.ix_(face, face)])
            for vector in vectors.T:
                for sign in (1, -1):
                    positive = sign * vector
                    if np.min(positive) >= -1e-12:
                        coefficients = np.zeros(3)
                        coefficients[list(face)] = np.maximum(positive, 0)
                        coefficients /= np.linalg.norm(coefficients)
                        candidates.append(
                            (float(coefficients @ matrix @ coefficients), coefficients)
                        )
    value, coefficients = max(candidates, key=lambda item: item[0])
    a, b, c = coefficients
    theta = 2 * np.arctan2(b, np.hypot(a, c))
    phi = np.arctan2(c, a) if a or c else 0.0
    return {"angles": [float(theta), float(phi)], "payoff": value}


def equilibrium_records(grid, payoffs, *, gamma=np.pi / 2, model="collective", atol=1e-3):
    """Keep all grid equilibria and certify each against continuous deviations."""
    mask = pure_nash_mask(payoffs, atol)
    records = []
    for indices in np.argwhere(mask):
        angles = grid[indices]
        current = payoffs[tuple(indices)]
        responses = [
            best_response(angles, p, gamma=gamma, model=model) for p in range(len(indices))
        ]
        regrets = [
            max(0.0, response["payoff"] - current[p]) for p, response in enumerate(responses)
        ]
        records.append(
            {
                "strategy_indices": indices.tolist(),
                "angles": angles.tolist(),
                "payoffs": current.tolist(),
                "best_responses": responses,
                "continuous_regrets": regrets,
                "continuous_nash_within_tolerance": bool(max(regrets) <= atol),
            }
        )
    return records
