"""Ensure historical evidence remains intact and results come from maintained code."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_archived_originals_match_manifest():
    archive = ROOT / "archive"
    manifest = json.loads((archive / "manifest.json").read_text())
    assert manifest["source_commit"] == "1c84b800e14efee63b8e8d9decc3aa0fc2d62d45"
    assert len(manifest["files"]) == 7
    with zipfile.ZipFile(archive / manifest["container"]) as original:
        for record in manifest["files"]:
            content = original.read(record["archive_path"])
            assert hashlib.sha256(content).hexdigest() == record["sha256"]
