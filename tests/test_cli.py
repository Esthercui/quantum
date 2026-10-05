"""Installed command behavior and portable result serialization."""

import json
import subprocess
import sys


def test_module_cli_writes_json(tmp_path):
    destination = tmp_path / "nested" / "result.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "quantum_pd",
            "--circuit",
            "zz",
            "--players",
            "4",
            "--output",
            str(destination),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert json.loads(destination.read_text()) == result
    assert result["full_angle_profiles"] == 18_974_736
    assert result["evaluated_representatives"] == 14_641
    assert result["equilibrium_angle_profiles"] == 1296


def test_default_cli_uses_ewl():
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "quantum_pd",
            "--players",
            "2",
            "--theta-points",
            "3",
            "--phi-points",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["circuit"] == "all_pairs_ewl"
    assert result["grid_equilibrium_count"] == 1
    assert result["continuous_certified_count"] == 1


def test_cli_rejects_invalid_search():
    completed = subprocess.run(
        [sys.executable, "-m", "quantum_pd", "--theta-points", "0"],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert "theta_points" in completed.stderr
    assert "Traceback" not in completed.stderr
