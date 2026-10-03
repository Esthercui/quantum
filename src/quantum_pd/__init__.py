"""Classical payoffs and the diagonal-ZZ compatibility API.

Use quantum_pd.ewl for the manuscript's EWL circuit and quantum_pd.ewl_search
for full-grid enumeration and continuous response certificates.
"""

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
