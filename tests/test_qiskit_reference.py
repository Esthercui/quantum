"""Independent gate-level check against the original pairwise-ZZ construction.

Qiskit is optional for package users, and required in the verification CI job.
The circuit below follows entangler() in quantum_pd_k2k3.ipynb and
quantum_pd_k4.ipynb, without their reversed payoff indexing or Aer dependency.
"""

from itertools import combinations

import numpy as np
import pytest
from numpy.testing import assert_allclose

from quantum_pd.game import expected_payoff, probabilities, statevector

qiskit = pytest.importorskip("qiskit")
from qiskit.quantum_info import Statevector  # noqa: E402


@pytest.mark.parametrize("players", [2, 3, 4])
@pytest.mark.parametrize("gamma", [0, 0.31, np.pi / 2])
def test_actual_gate_sequence(players, gamma):
    rng = np.random.default_rng(410 + players)
    for _ in range(8):
        angles = rng.random((players, 2)) * [np.pi, np.pi / 2]
        circuit = qiskit.QuantumCircuit(players)
        for i, j in combinations(range(players), 2):
            circuit.cx(i, j)
            circuit.rz(2 * gamma, j)
            circuit.cx(i, j)
        for player, (theta, phi) in enumerate(angles):
            circuit.ry(theta, player)
            circuit.rz(phi, player)
        for i, j in combinations(range(players), 2):
            circuit.cx(i, j)
            circuit.rz(-2 * gamma, j)
            circuit.cx(i, j)
        actual = Statevector.from_instruction(circuit)
        assert_allclose(actual.data, statevector(angles, gamma), atol=1e-12)
        assert_allclose(actual.probabilities(), probabilities(angles, gamma), atol=1e-12)
        # Independent payoff decoding: reverse the displayed Qiskit bitstring.
        payoff = np.zeros(players)
        for index, probability in enumerate(actual.probabilities()):
            bits = [int(b) for b in format(index, f"0{players}b")[::-1]]
            if all(b == 0 for b in bits):
                pay = [3] * players
            elif all(b == 1 for b in bits):
                pay = [1] * players
            else:
                pay = [5 if bit else 0 for bit in bits]
            payoff += probability * np.array(pay)
        assert_allclose(payoff, expected_payoff(angles, gamma=gamma), atol=1e-12)
