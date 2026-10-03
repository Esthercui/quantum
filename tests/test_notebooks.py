"""The published walkthroughs contain runnable Python and successful outputs."""

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_maintained_notebooks_have_executed_cells_and_no_saved_errors():
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text())
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                ast.parse("".join(cell["source"]))
                assert cell["execution_count"] is not None, path.name
                assert all(o["output_type"] != "error" for o in cell.get("outputs", [])), path.name
