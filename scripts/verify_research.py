"""Verify saved research records, with optional re-enumeration of every profile."""

import argparse
import json
from pathlib import Path

import numpy as np
from reproduce_research import scientific_sources

from quantum_pd import classical_nash, pure_nash_mask
from quantum_pd.ewl import expected_payoff
from quantum_pd.ewl_search import best_response, grid_payoffs

ROOT = Path(__file__).resolve().parents[1]


def verify(full=False):
    for k in (2, 3, 4):
        result = json.loads((ROOT / f"results/ewl-k{k}.json").read_text())
        assert result["source_sha256"] == scientific_sources(), "Scientific source changed."
        assert result["classical_equilibria"] == classical_nash(k)
        assert result["grid_equilibrium_count"] == len(result["grid_equilibria"])
        expected_indices = []
        for row in result["grid_equilibria"] + result["named_profiles"]:
            pay = expected_payoff(row["angles"])
            assert np.allclose(pay, row["payoffs"], rtol=0, atol=1e-12)
            regret = []
            for player, stored in enumerate(row["best_responses"]):
                response = best_response(row["angles"], player)
                trial = np.array(row["angles"])
                trial[player] = stored["angles"]
                assert np.isclose(
                    expected_payoff(trial)[player], stored["payoff"], atol=1e-11, rtol=0
                )
                assert np.isclose(response["payoff"], stored["payoff"], atol=1e-11, rtol=0)
                regret.append(max(0.0, response["payoff"] - pay[player]))
            assert np.allclose(regret, row["continuous_regrets"], atol=1e-11, rtol=0)
            if "strategy_indices" in row:
                expected_indices.append(row["strategy_indices"])
                assert row["continuous_nash_within_tolerance"] == (
                    max(regret) <= result["absolute_tolerance"]
                )
        if full:
            _, table = grid_payoffs(
                k, theta_points=result["theta_points"], phi_points=result["phi_points"]
            )
            indices = np.argwhere(pure_nash_mask(table, result["absolute_tolerance"])).tolist()
            assert indices == expected_indices
            assert (
                int(pure_nash_mask(table, 1e-10).sum()) == result["strict_grid_equilibrium_count"]
            )
        print(f"k={k}: {len(expected_indices)} certified profiles verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    verify(parser.parse_args().full)
