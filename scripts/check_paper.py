"""Recompute bounded manuscript checks; never relabel them as historical runs."""

import argparse
import json
from math import pi
from pathlib import Path

import numpy as np

from quantum_pd import expected_payoff, search_grid
from quantum_pd.experiments import (
    classical_match,
    qaoa_outcomes,
    schelling_four_spots,
    schelling_probabilities,
)

ROOT = Path(__file__).resolve().parents[1]


def compute_checks() -> dict:
    """Use the original grids and gate sequences with explicit modern evaluation."""
    nash = []
    for players, actions in [(2, [0, 0]), (3, [0, 1, 0]), (4, [0, 0, 0, 0])]:
        angles = [(pi * action, 0) for action in actions]
        current = expected_payoff(angles)
        deviation = angles.copy()
        deviation[0] = (pi, 0)
        changed = expected_payoff(deviation)
        nash.append(
            {
                "players": players,
                "paper_reported_actions": actions,
                "current_payoffs": current.tolist(),
                "deviating_player": 0,
                "deviation_payoffs": changed.tolist(),
                "deviator_gain": float(changed[0] - current[0]),
            }
        )

    tolerances = []
    for players in (2, 3, 4):
        theta, phi = (11, 6) if players == 4 else (15, 8)
        for atol in (1e-3, 1e-10):
            result = search_grid(players, theta_points=theta, phi_points=phi, atol=atol)
            tolerances.append(
                {
                    "players": players,
                    "absolute_tolerance": atol,
                    "equilibrium_classes": len(result["equilibrium_classes"]),
                    "representative_angles": result["equilibrium_classes"][0][
                        "representative_angles"
                    ],
                    "equivalent_angle_profiles": result["equilibrium_angle_profiles"],
                }
            )

    qaoa = []
    for players in (2, 3, 4):
        candidates = []
        for gamma in np.linspace(0, pi / 2, 7):
            for beta in np.linspace(0, pi, 7):
                candidate = qaoa_outcomes(players, gamma, beta)
                candidates.append({"gamma": float(gamma), "beta": float(beta), **candidate})
        best_value = max(result["mean_payoff"] for result in candidates)
        # Select the first tied grid point so machine rounding cannot change its identity.
        best = next(c for c in candidates if best_value - c["mean_payoff"] <= 1e-12)
        qaoa.append(
            {
                "players": players,
                "theta_grid": "not applicable",
                "gamma_points": 7,
                "beta_points": 7,
                "classical_pairwise_nash_payoff": players - 1,
                "largest_cooperation_error_from_half": float(
                    max(abs(c["cooperation_rate"] - 0.5) for c in candidates)
                ),
                "best_grid_point": best,
            }
        )

    schelling = []
    for label, theta_a, theta_b in [
        ("unbiased", 0, 0),
        ("shared pi/6", pi / 6, pi / 6),
        ("mismatch pi/6", pi / 6, 0),
        ("mismatch pi/2", pi / 2, 0),
    ]:
        row = {"case": label, "theta_a": theta_a, "theta_b": theta_b}
        for undo in (False, True):
            probs = schelling_probabilities(theta_a, theta_b, undo=undo)
            row["with_inverse" if undo else "without_inverse"] = float(probs[0] + probs[3])
        schelling.append(row)
    return {
        "evaluation": (
            "Current Qiskit exact statevectors; no shots, optimizer fit, "
            "or historical timing replay."
        ),
        "nash_claim_checks": nash,
        "tolerance_checks": tolerances,
        "qaoa_7x7_checks": qaoa,
        "schelling_binary_checks": schelling,
        "schelling_four_spots": {
            "without_inverse": schelling_four_spots(),
            "with_inverse": schelling_four_spots(undo=True),
        },
        "classical_match_checks": [
            {"p_a": a, "p_b": b, "exact_match": classical_match(a, b)}
            for a, b in [(0.5, 0.5), (0.7, 0.7), (0.9, 0.9), (0.8, 0.2), (1, 0.2)]
        ],
        "four_player_31_by_16_profiles": (31 * 16) ** 4,
    }


def compare(actual, expected) -> None:
    """Allow only small floating-point differences across CPU and Qiskit versions."""
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            compare(actual[key], expected[key])
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for left, right in zip(actual, expected, strict=True):
            compare(left, right)
    elif isinstance(expected, float):
        assert np.isclose(actual, expected, rtol=0, atol=1e-12), (actual, expected)
    else:
        assert actual == expected, (actual, expected)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        payload = compute_checks()
    except ImportError as exc:
        parser.error(str(exc))
    path = ROOT / "results/paper-checks.json"
    if args.check:
        compare(payload, json.loads(path.read_text()))
        print("Manuscript checks reproduce within 1e-12 numerical tolerance.")
    else:
        path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
        print("Wrote results/paper-checks.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
