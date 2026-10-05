"""Regenerate the small reference artifact, or verify it without changing files."""

import argparse
import hashlib
import json
from pathlib import Path

from quantum_pd import __version__, search_grid

ROOT = Path(__file__).resolve().parents[1]


def source_digest() -> str:
    """Bind results to maintained scientific source, independent of checkout path."""
    digest = hashlib.sha256()
    for source in sorted((ROOT / "src/quantum_pd").glob("*.py")):
        digest.update(source.name.encode() + b"\0" + source.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if reference.json is stale.")
    args = parser.parse_args()
    results = []
    for model in ("collective", "pairwise"):
        for players in (2, 3, 4):
            theta, phi = (11, 6) if players == 4 else (15, 8)
            results.append(search_grid(players, theta_points=theta, phi_points=phi, model=model))
    payload = {
        "package_version": __version__,
        "circuit_model": "pairwise_zz_ry_rz",
        "source_sha256": source_digest(),
        "method": "Exhaustive theta grid with exact phase-equivalence reduction; float64.",
        "results": results,
    }
    destination = ROOT / "results/reference.json"
    serialized = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    if args.check:
        if not destination.exists() or json.loads(destination.read_text()) != payload:
            raise SystemExit(
                "Reference results differ. Run python scripts/reproduce.py and review."
            )
        print("Reference results match all six searches and the maintained source hash.")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(serialized, encoding="utf-8")
        print("Wrote results/reference.json (six searches).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
