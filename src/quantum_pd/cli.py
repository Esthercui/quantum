"""Small command-line entry point; emits portable, deterministic JSON."""

import argparse
import json
from pathlib import Path

from . import __version__
from .search import search_grid


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pure Nash equilibria of the pairwise-ZZ PD circuit (k = 2–4)."
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--players", type=int, choices=(2, 3, 4), default=4)
    parser.add_argument("--theta-points", type=int, default=11)
    parser.add_argument("--phi-points", type=int, default=6)
    parser.add_argument("--payoff-model", choices=("collective", "pairwise"), default="collective")
    parser.add_argument("--atol", type=float, default=1e-10)
    parser.add_argument("--max-profiles", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, help="Also save JSON to this path.")
    args = parser.parse_args(argv)
    try:
        result = search_grid(
            args.players,
            theta_points=args.theta_points,
            phi_points=args.phi_points,
            model=args.payoff_model,
            atol=args.atol,
            max_profiles=args.max_profiles,
        )
    except ValueError as exc:
        parser.error(str(exc))
    result["package_version"] = __version__
    result["circuit_model"] = "pairwise_zz_ry_rz"
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0
