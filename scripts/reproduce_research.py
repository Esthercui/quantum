"""Run the manuscript's full EWL grids and save continuous-deviation certificates."""

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np

from quantum_pd import __version__, classical_nash, pure_nash_mask
from quantum_pd.ewl import C, D, Q, expected_payoff
from quantum_pd.ewl_search import best_response, equilibrium_records, grid_payoffs

ROOT = Path(__file__).resolve().parents[1]


def scientific_sources():
    paths = [
        ROOT / "src/quantum_pd" / (name + ".py") for name in ("ewl", "ewl_search", "game", "search")
    ]
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
    }


def run(players):
    theta, phi = (11, 6) if players == 4 else (15, 8)
    started = time.perf_counter()
    last = [-1]

    def progress(done, total):
        percent = int(done * 10 / total)
        if percent > last[0]:
            print(f"k={players}: {done:,}/{total:,} profiles ({done / total:.0%})", flush=True)
            last[0] = percent

    grid, table = grid_payoffs(players, theta_points=theta, phi_points=phi, progress=progress)
    grid_seconds = time.perf_counter() - started
    print(f"k={players}: grid evaluated in {grid_seconds:.3f}s; certifying candidates", flush=True)
    records = equilibrium_records(grid, table, atol=1e-3)
    strict_count = int(pure_nash_mask(table, 1e-10).sum())
    # Save the tensor locally for investigations without recomputing the full grid.
    np.save(ROOT / "output/revision" / f"ewl_k{players}_payoffs.npy", table)
    accepted = [r for r in records if r["continuous_nash_within_tolerance"]]
    continuous_strict = [r for r in records if max(r["continuous_regrets"]) <= 1e-10]
    probe = []
    named = [
        ("all_C", [C] * players),
        ("all_D", [D] * players),
        ("all_Q", [Q] * players),
        ("D_against_Q", [D] + [Q] * (players - 1)),
    ]
    if players == 3:
        named.append(("off_grid_equal_phase_pi_over_4", [(0.0, float(np.pi / 4))] * 3))
    for label, profile in named:
        pay = expected_payoff(profile)
        responses = [best_response(profile, p) for p in range(players)]
        probe.append(
            {
                "profile": label,
                "angles": [list(a) for a in profile],
                "payoffs": pay.tolist(),
                "best_responses": responses,
                "continuous_regrets": [
                    max(0.0, r["payoff"] - pay[p]) for p, r in enumerate(responses)
                ],
            }
        )
    payload = {
        "schema_version": 1,
        "circuit": "all_pairs_ewl",
        "players": players,
        "payoff_model": "collective",
        "gamma": float(np.pi / 2),
        "theta_points": theta,
        "phi_points": phi,
        "strategy_grid": grid.tolist(),
        "full_angle_profiles": len(grid) ** players,
        "absolute_tolerance": 1e-3,
        "strict_diagnostic_tolerance": 1e-10,
        "grid_equilibrium_count": len(records),
        "strict_grid_equilibrium_count": strict_count,
        "continuous_certified_count": len(accepted),
        "continuous_strict_count": len(continuous_strict),
        "certified_payoff_patterns": sorted({tuple(np.round(r["payoffs"], 9)) for r in accepted}),
        "classical_equilibria": classical_nash(players),
        "named_profiles": probe,
        "grid_equilibria": records,
        "source_sha256": scientific_sources(),
        "execution": {
            "package_version": __version__,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "processor": platform.machine(),
            "grid_seconds": grid_seconds,
            "total_seconds": time.perf_counter() - started,
            "shots": 0,
            "timing_scope": "One local run, excluding file publication; no speedup comparison.",
        },
    }
    path = ROOT / "results" / f"ewl-k{players}.json"
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                key: payload[key]
                for key in [
                    "players",
                    "grid_equilibrium_count",
                    "strict_grid_equilibrium_count",
                    "continuous_certified_count",
                    "continuous_strict_count",
                    "certified_payoff_patterns",
                ]
            }
        ),
        flush=True,
    )
    print(f"Saved {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--players", nargs="+", type=int, choices=[2, 3, 4], default=[2, 3, 4])
    args = parser.parse_args()
    (ROOT / "output/revision").mkdir(parents=True, exist_ok=True)
    for players in args.players:
        run(players)


if __name__ == "__main__":
    main()
