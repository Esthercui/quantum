"""Small, exact replays of the manuscript's QAOA and Schelling gate sequences.

Install the optional verification dependency with pip install -e '.[verify]'.
These calculations use current Qiskit statevectors, not the historical unseeded
Aer shot counts. QAOA here denotes the original ZZ/RX ansatz, not a Nash solver.
"""

from itertools import combinations

import numpy as np
from numpy.typing import NDArray

from .game import classical_payoff, outcomes, validate_players


def _qiskit():
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
    except ImportError as exc:
        raise ImportError(
            "Circuit replays need Qiskit. From the repository root run: "
            "python -m pip install -e '.[verify]'"
        ) from exc
    return QuantumCircuit, Statevector


def qaoa_circuit(players: int, gamma: float, beta: float):
    """Rebuild the depth-one circuit from quantum_pd.py-Copy1.ipynb."""
    validate_players(players)
    if not np.isfinite([gamma, beta]).all():
        raise ValueError("gamma and beta must be finite")
    quantum_circuit, _ = _qiskit()
    circuit = quantum_circuit(players)
    circuit.h(range(players))
    for i, j in combinations(range(players), 2):
        circuit.cx(i, j)
        circuit.rz(2 * gamma, j)
        circuit.cx(i, j)
    circuit.rx(2 * beta, range(players))
    return circuit


def qaoa_outcomes(players: int, gamma: float, beta: float) -> dict:
    """Expected pairwise payoffs and mean fraction of cooperating players."""
    circuit = qaoa_circuit(players, gamma, beta)
    _, statevector = _qiskit()
    probabilities = statevector.from_instruction(circuit).probabilities()
    bits = outcomes(players)
    payoffs = probabilities @ np.array([classical_payoff(b, "pairwise") for b in bits])
    return {
        "payoffs": payoffs.tolist(),
        "mean_payoff": float(payoffs.mean()),
        "cooperation_rate": float(probabilities @ (1 - bits).mean(axis=1)),
        "cx_count_before_transpilation": int(circuit.count_ops().get("cx", 0)),
    }


def optimize_qaoa(players: int) -> dict:
    """Replay the original COBYLA settings with deterministic statevector payoffs.

    Retains the original initial points and maximum of 100 evaluations.
    The returned value is attained by this local run, not a global-optimum claim.
    """
    validate_players(players)
    try:
        from scipy.optimize import minimize
    except ImportError as exc:
        raise ImportError("QAOA optimization needs python -m pip install -e '.[verify]'") from exc
    initial = [0.5, 0.5] if players == 2 else [0.7, 1.0]
    result = minimize(
        lambda angles: -sum(qaoa_outcomes(players, *angles)["payoffs"]),
        initial,
        method="COBYLA",
        options={"maxiter": 100},
    )
    return {
        "players": players,
        "method": "COBYLA",
        "initial_angles": initial,
        "max_evaluations": 100,
        "gamma": float(result.x[0]),
        "beta": float(result.x[1]),
        "converged": bool(result.success),
        "evaluations": int(result.nfev),
        "termination": str(result.message),
        "payoff_model": "pairwise",
        "classical_nash_payoff_per_player": players - 1,
        "shots": 0,
        **qaoa_outcomes(players, *result.x),
    }


def classical_match(probability_a: float, probability_b: float) -> float:
    """Two independent binary choices; inputs are probabilities of spot zero."""
    if not all(np.isfinite(p) and 0 <= p <= 1 for p in (probability_a, probability_b)):
        raise ValueError("choice probabilities must be finite and between 0 and 1")
    return probability_a * probability_b + (1 - probability_a) * (1 - probability_b)


def schelling_circuit(theta_a: float = 0, theta_b: float = 0, *, undo: bool = False):
    """Prepare a Bell pair, rotate each player's qubit, and optionally apply J†."""
    if not np.isfinite([theta_a, theta_b]).all():
        raise ValueError("rotation angles must be finite")
    quantum_circuit, _ = _qiskit()
    circuit = quantum_circuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    for player, theta in enumerate((theta_a, theta_b)):
        if theta != 0:
            circuit.ry(theta, player)
    if undo:
        circuit.cx(0, 1)
        circuit.h(0)
    return circuit


def schelling_probabilities(
    theta_a: float = 0, theta_b: float = 0, *, undo: bool = False
) -> NDArray:
    """Return probabilities in Qiskit basis order: 00, 01, 10, 11."""
    circuit = schelling_circuit(theta_a, theta_b, undo=undo)
    _, statevector = _qiskit()
    return statevector.from_instruction(circuit).probabilities()


def schelling_four_spots(*, undo: bool = False) -> dict:
    """Rebuild the unbiased two-player, four-spot Bell-pair construction."""
    quantum_circuit, statevector = _qiskit()
    circuit = quantum_circuit(4)
    circuit.h(0)
    circuit.h(1)
    circuit.cx(0, 2)
    circuit.cx(1, 3)
    if undo:
        circuit.cx(1, 3)
        circuit.cx(0, 2)
        circuit.h(1)
        circuit.h(0)
    probabilities = statevector.from_instruction(circuit).probabilities()
    match = sum(p for index, p in enumerate(probabilities) if (index & 3) == (index >> 2))
    return {
        "match_rate": float(match),
        "unitary_gates": int(sum(circuit.count_ops().values())),
        "cx_count": int(circuit.count_ops().get("cx", 0)),
        "measurement_operations": 4,
    }
