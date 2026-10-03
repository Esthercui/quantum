"""Check that the source record and cleaned notebooks preserve evidence honestly."""

import ast
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def saved_output(name, cell):
    with zipfile.ZipFile(ROOT / "archive/original-notebooks.zip") as archive:
        notebook = json.loads(archive.read("notebooks/" + name))
    return "\n".join(
        "".join(output.get("text", output.get("data", {}).get("text/plain", [])))
        for output in notebook["cells"][cell].get("outputs", [])
    )


def test_transcribed_historical_counts_match_archived_outputs():
    source = json.loads((ROOT / "results/paper-reported.json").read_text())["historical_outputs"]
    row = source["high_resolution_grid"]
    text = saved_output(row["notebook"], row["cell"])
    two, three = text.split("===== GRID search  n = 3")
    assert len(re.findall(r" idx ", two)) == row["k2_printed_profiles"]
    assert len(re.findall(r" idx ", three)) == row["k3_printed_profiles"]
    row = source["k4_sweep"]
    assert f"Finished in {row['finished_seconds']:.2f} seconds" in saved_output(
        row["notebook"], row["cell"]
    )
    row = source["k4_analysis"]
    output = ast.literal_eval(saved_output(row["notebook"], row["cell"]))
    assert output[1] == row["saved_profile_count"]
    assert list(output[0][0][1]) == row["shown_payoffs"]


def test_maintained_notebooks_have_executed_cells_and_no_saved_errors():
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text())
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                ast.parse("".join(cell["source"]))
                assert cell["execution_count"] is not None, path.name
                assert all(o["output_type"] != "error" for o in cell.get("outputs", [])), path.name
