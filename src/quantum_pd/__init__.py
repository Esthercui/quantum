"""Prisoner's Dilemma payoffs and pure Nash searches for k = 2, 3, 4."""

from .game import classical_payoff, expected_payoff, probabilities, statevector
from .search import classical_nash, pure_nash_mask, search_grid

__all__ = [
    "classical_nash",
    "classical_payoff",
    "expected_payoff",
    "probabilities",
    "pure_nash_mask",
    "search_grid",
    "statevector",
]
__version__ = "0.1.0"
