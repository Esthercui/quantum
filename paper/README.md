# Research manuscript

[Read the PDF](research-paper.pdf) · [Read the text](manuscript.md)

**Simulating Game Theory and Strategic Interactions Using Quantum Computing**

Esther Cui · Original manuscript: Spring 2025 · Edited and recomputed: Fall 2026

The manuscript reports the explicit all-pairs EWL model through four players,
the original depth-one variational circuit, and the Bell-pair coordination
experiments. Numerical tables and substitutions are generated from the same
JSON records used by the code and notebooks.

| File | Purpose |
|---|---|
| `manuscript.template.md` | Editable prose and numerical placeholders |
| `manuscript.md` | Generated paper text and tables |
| `research-paper.pdf` | Rendered manuscript |
| `numerical-values.json` | Values substituted from computation records |
| `figures/` | Figures drawn from saved data and the defined strategy matrix |
| `build-manifest.json` | SHA-256 checksums of paper inputs and outputs |

From the repository root:

```bash
python scripts/build_manuscript.py --check

# Rebuild the PDF after an intentional text or result update.
python -m pip install -e '.[paper]'
python scripts/build_manuscript.py --pdf
```

For the complete pinned environment, use `uv sync --frozen --all-extras` and
prefix commands with `uv run`. Reproduce numerical records before rebuilding
the paper; see Appendix A and the repository README for the commands.

The grid counts describe sampled angle profiles. Continuous best-response
certificates establish their stability within the specified strategy family;
they do not claim a complete enumeration of continuous equilibria.

## Manuscript formatting

The PDF uses a conventional single-column layout: 12-point Times New Roman body
text, one-inch margins, serif headings, plain ruled tables, and centered page
numbers. Installed Times New Roman font files are used when available; otherwise
the renderer uses the bundled STIX serif family. The build manifest records the
actual font family and file hashes. Font files are not redistributed. Figures
use matching serif labels and STIX mathematical symbols.
