"""Verify EWL matrices against an independently assembled RYY/RZ/RY circuit."""

from math import pi

import numpy as np
import pytest
from numpy.testing import assert_allclose

from quantum_pd.ewl import statevector

qiskit = pytest.importorskip("qiskit")
from qiskit.quantum_info import Statevector  # noqa: E402


@pytest.mark.parametrize("gamma", [0, 0.57, pi / 2])
def test_ewl_matches_gate_sequence(gamma):
    rng = np.random.default_rng(491)
    for _ in range(8):
        angles = rng.random((2, 2)) * [pi, pi / 2]
        circuit = qiskit.QuantumCircuit(2)
        circuit.ryy(-gamma, 0, 1)
        for player, (theta, phi) in enumerate(angles):
            circuit.rz(-phi, player)
            circuit.ry(-theta, player)
            circuit.rz(-phi, player)
        circuit.ryy(gamma, 0, 1)
        assert_allclose(
            statevector(angles, gamma), Statevector.from_instruction(circuit).data, atol=1e-12
        )
