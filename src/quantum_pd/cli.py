"""Small command-line entry point; emits portable, deterministic JSON."""

import argparse
import json
from pathlib import Path

from . import __version__
from .ewl_search import equilibrium_records, grid_payoffs
from .search import search_grid


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pure Nash equilibria of the all-pairs EWL PD game (k = 2–4)."
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--players", type=int, choices=(2, 3, 4), default=4)
    parser.add_argument("--circuit", choices=("ewl", "zz"), default="ewl")
    parser.add_argument("--theta-points", type=int, default=11)
    parser.add_argument("--phi-points", type=int, default=6)
    parser.add_argument("--payoff-model", choices=("collective", "pairwise"), default="collective")
    parser.add_argument("--atol", type=float, default=1e-10)
    parser.add_argument("--max-profiles", type=int, default=25_000_000)
    parser.add_argument("--output", type=Path, help="Also save JSON to this path.")
    args = parser.parse_args(argv)
    try:
        if args.circuit == "zz":
            result = search_grid(
                args.players,
                theta_points=args.theta_points,
                phi_points=args.phi_points,
                model=args.payoff_model,
                atol=args.atol,
                max_profiles=args.max_profiles,
            )
        else:
            grid, table = grid_payoffs(
                args.players,
                theta_points=args.theta_points,
                phi_points=args.phi_points,
                model=args.payoff_model,
                max_profiles=args.max_profiles,
            )
            records = equilibrium_records(grid, table, model=args.payoff_model, atol=args.atol)
            result = {
                "circuit": "all_pairs_ewl",
                "players": args.players,
                "payoff_model": args.payoff_model,
                "absolute_tolerance": args.atol,
                "theta_points": args.theta_points,
                "phi_points": args.phi_points,
                "full_angle_profiles": len(grid) ** args.players,
                "grid_equilibrium_count": len(records),
                "continuous_certified_count": sum(
                    r["continuous_nash_within_tolerance"] for r in records
                ),
                "grid_equilibria": records,
            }
    except ValueError as exc:
        parser.error(str(exc))
    result["package_version"] = __version__
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0
