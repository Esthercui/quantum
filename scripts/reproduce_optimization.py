"""Run the original COBYLA starts using exact statevector payoff expectations."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from quantum_pd.experiments import optimize_qaoa, qaoa_outcomes

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "results/optimization.json"
    sources = {
        f"src/quantum_pd/{name}.py": hashlib.sha256(
            (ROOT / f"src/quantum_pd/{name}.py").read_bytes()
        ).hexdigest()
        for name in ["experiments", "game"]
    }
    if args.check:
        payload = json.loads(path.read_text())
        assert payload["source_sha256"] == sources, "Optimization source changed; rerun and review."
        for row in payload["results"]:
            observed = qaoa_outcomes(row["players"], row["gamma"], row["beta"])
            assert np.allclose(observed["payoffs"], row["payoffs"], rtol=0, atol=1e-12)
            assert np.isclose(observed["cooperation_rate"], row["cooperation_rate"], atol=1e-12)
            assert row["classical_nash_payoff_per_player"] == row["players"] - 1
            assert row["converged"]
        print("Recorded optimizer parameters reproduce payoffs and matched baselines.")
    else:
        import qiskit
        import scipy

        payload = {
            "evaluation": "Exact statevector expectation; one local optimization per k.",
            "source_sha256": sources,
            "numpy": np.__version__,
            "qiskit": qiskit.__version__,
            "scipy": scipy.__version__,
            "results": [optimize_qaoa(k) for k in [2, 3, 4]],
        }
        path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
        for row in payload["results"]:
            print(
                row["players"],
                row["mean_payoff"],
                "baseline",
                row["classical_nash_payoff_per_player"],
                "converged",
                row["converged"],
            )


if __name__ == "__main__":
    main()
