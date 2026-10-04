"""Build manuscript text and tables from saved results; optionally render its PDF.

--check needs the core environment. --pdf additionally needs ReportLab and
Matplotlib; on the author's Mac these run through the separate studio-python.
"""

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def academic_fonts():
    """Use installed Times New Roman, with Matplotlib's STIX as a portable fallback."""
    import matplotlib.font_manager as fm

    mac_fonts = Path("/System/Library/Fonts/Supplemental")
    names = ["", " Bold", " Italic", " Bold Italic"]
    paths = [mac_fonts / f"Times New Roman{suffix}.ttf" for suffix in names]
    if all(path.is_file() for path in paths):
        return "Times New Roman", paths
    try:
        paths = [
            Path(
                fm.findfont(
                    fm.FontProperties(family="Times New Roman", weight=w, style=s),
                    fallback_to_default=False,
                )
            )
            for w, s in [
                ("normal", "normal"),
                ("bold", "normal"),
                ("normal", "italic"),
                ("bold", "italic"),
            ]
        ]
        return "Times New Roman", paths
    except ValueError:
        root = Path(fm.findfont("STIXGeneral")).parent
        return "STIXGeneral", [
            root / f"STIXGeneral{suffix}.ttf" for suffix in ["", "Bol", "Italic", "BolIta"]
        ]


def table(headers, rows):
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
            *["| " + " | ".join(str(v) for v in row) + " |" for row in rows],
        ]
    )


def material():
    ewl = [json.loads((ROOT / f"results/ewl-k{k}.json").read_text()) for k in [2, 3, 4]]
    optimizer = json.loads((ROOT / "results/optimization.json").read_text())
    experiments = json.loads((ROOT / "results/experiments.json").read_text())
    opt = optimizer["results"]
    rows = ewl[-1]["grid_equilibria"]
    distinct = {
        tuple(
            (ewl[2]["theta_points"] - 1) * ewl[2]["phi_points"]
            if i >= (ewl[2]["theta_points"] - 1) * ewl[2]["phi_points"]
            else i
            for i in row["strategy_indices"]
        )
        for row in rows
    }
    cooperative = sum(all(abs(p - 3) < 1e-10 for p in row["payoffs"]) for row in rows)
    probes = [
        next(p for p in run["named_profiles"] if p["profile"] == "D_against_Q") for run in ewl
    ]
    offgrid = next(
        p for p in ewl[1]["named_profiles"] if p["profile"] == "off_grid_equal_phase_pi_over_4"
    )
    heatmap = experiments["qaoa_7x7_checks"][1]["best_grid_point"]["mean_payoff"]
    settings = [
        ["Two, unbiased", "0.5, 0.5", "0, 0"],
        ["Two, shared rotation A", "0.7, 0.7", "pi/6, pi/6"],
        ["Two, shared rotation B", "0.9, 0.9", "pi/6, pi/6"],
        ["Two, unequal rotations", "0.8, 0.2", "pi/6, 0"],
        ["Two, pi/2 difference", "Not paired", "pi/2, 0"],
        ["Four, unbiased", "Uniform independent", "Two Bell pairs"],
    ]
    classical = [x["exact_match"] for x in experiments["classical_match_checks"][:4]]
    binary = experiments["schelling_binary_checks"]
    rates = [
        binary[0]["without_inverse"],
        binary[1]["without_inverse"],
        binary[1]["without_inverse"],
        binary[2]["without_inverse"],
        binary[3]["without_inverse"],
        experiments["schelling_four_spots"]["without_inverse"]["match_rate"],
    ]
    base = classical + [None, 0.25]
    values = {
        "nash_counts": ", ".join(str(r["grid_equilibrium_count"]) for r in ewl),
        "k4_distinct": str(len(distinct)),
        "k4_allq_count": str(cooperative),
        "k4_asymmetric_count": str(len(rows) - cooperative),
        "opt_means": ", ".join(f"{r['mean_payoff']:.4f}" for r in opt),
        "opt_gains": ", ".join(f"{r['mean_payoff'] - (r['players'] - 1):.4f}" for r in opt),
        "python_version": "Python " + ewl[0]["execution"]["python"],
        "numpy_version": optimizer["numpy"],
        "qiskit_version": optimizer["qiskit"],
        "scipy_version": optimizer["scipy"],
        "d_against_q": ", ".join(f"{p['payoffs'][0]:.0f}" for p in probes),
        "offgrid_payoff": f"{offgrid['payoffs'][0]:.2f}",
        "grid_times": ", ".join(f"{r['execution']['grid_seconds']:.4f}" for r in ewl),
        "k4_profiles": f"{ewl[2]['full_angle_profiles']:,}",
        "fine_grid_profiles": f"{(31 * 16) ** 4:,}",
        "heatmap_max": f"{heatmap:.5f}",
        "heatmap_gain": f"{heatmap - 2:.5f}",
        "schelling_pi6": f"{binary[2]['without_inverse']:.7f}",
        "table_ewl": table(
            [
                "k",
                "Grid / player",
                "Joint profiles",
                "Grid NE",
                "Continuous certified",
                "All-Q payoff",
            ],
            [
                [
                    r["players"],
                    f"{r['theta_points']} x {r['phi_points']}",
                    f"{r['full_angle_profiles']:,}",
                    r["grid_equilibrium_count"],
                    r["continuous_certified_count"],
                    "3 each",
                ]
                for r in ewl
            ],
        ),
        "table_optimization": table(
            ["k", "Mean payoff", "Matched baseline", "Gain", "C fraction", "CX gates"],
            [
                [
                    r["players"],
                    f"{r['mean_payoff']:.4f}",
                    r["players"] - 1,
                    f"{r['mean_payoff'] - (r['players'] - 1):.4f}",
                    f"{r['cooperation_rate']:.0%}",
                    r["cx_count_before_transpilation"],
                ]
                for r in opt
            ],
        ),
        "table_schelling_settings": table(
            ["Configuration", "Classical pA, pB", "Quantum angles / state"], settings
        ),
        "table_schelling_results": table(
            ["Configuration", "Classical", "Direct quantum", "With inverse", "Delta"],
            [
                [
                    settings[i][0],
                    "-" if b is None else f"{b:.6f}",
                    f"{rates[i]:.6f}",
                    "1.000000",
                    "-" if b is None else f"{rates[i] - b:+.6f}",
                ]
                for i, b in enumerate(base)
            ],
        ),
    }
    template = (PAPER / "manuscript.template.md").read_text()
    used = set(re.findall(r"\{\{(\w+)\}\}", template))
    assert used == set(values), (used - set(values), set(values) - used)
    text = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)
    return text, values, ewl, optimizer, experiments


def figures(ewl, experiments):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt
    import numpy as np

    family, paths = academic_fonts()
    for path in paths:
        fm.fontManager.addfont(path)
    plt.rcParams.update(
        {
            "font.family": family,
            "mathtext.fontset": "stix",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.dpi": 220,
        }
    )
    folder = PAPER / "figures"
    folder.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.4, 1.05))
    ax.set_axis_off()
    ax.text(0.02, 0.5, r"$U(\theta,\phi)=$", fontsize=15, va="center")
    ax.text(0.49, 0.72, r"$e^{i\phi}\cos(\theta/2)$", fontsize=15, ha="center")
    ax.text(0.78, 0.72, r"$\sin(\theta/2)$", fontsize=15, ha="center")
    ax.text(0.49, 0.19, r"$-\sin(\theta/2)$", fontsize=15, ha="center")
    ax.text(0.78, 0.19, r"$e^{-i\phi}\cos(\theta/2)$", fontsize=15, ha="center")
    for x, direction in [(0.32, 1), (0.96, -1)]:
        ax.plot(
            [x + 0.02 * direction, x, x, x + 0.02 * direction],
            [0.94, 0.94, 0.08, 0.08],
            color="black",
            lw=1,
        )
    ax.set(xlim=(0, 1), ylim=(0, 1))
    fig.savefig(folder / "strategy-matrix.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.3, 2.8), layout="constrained")
    times = [r["execution"]["grid_seconds"] for r in ewl]
    ax.plot([2, 3, 4], times, "o-", color="black", lw=1.2)
    ax.set(
        yscale="log",
        xticks=[2, 3, 4],
        xlabel="Players (k)",
        ylabel="Grid evaluation time (seconds)",
    )
    ax.grid(axis="y", alpha=0.2)
    for k, t in zip([2, 3, 4], times, strict=True):
        ax.annotate(
            f"{t:.4f} s", (k, t), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=9
        )
    ax.margins(y=0.3)
    fig.savefig(folder / "ewl-runtime.png")
    plt.close(fig)
    data = experiments["qaoa_7x7_checks"][1]
    fig, ax = plt.subplots(figsize=(6.3, 3.35), layout="constrained")
    mesh = ax.pcolormesh(
        data["gamma_values"],
        data["beta_values"],
        np.asarray(data["mean_payoff_grid_gamma_then_beta"]).T,
        shading="nearest",
        cmap="viridis",
    )
    fig.colorbar(mesh, ax=ax, label="Mean summed-pairwise payoff")
    ax.set(
        xlabel=r"$\gamma$ (radians)",
        ylabel=r"$\beta$ (radians)",
        title="Three-player ZZ/RX payoff landscape",
    )
    fig.savefig(folder / "qaoa-landscape.png")
    plt.close(fig)
    curve = experiments["coordination_curve"]
    fig, ax = plt.subplots(figsize=(6.3, 2.9), layout="constrained")
    ax.plot(
        [r["p_a"] for r in curve],
        [r["quantum_match"] for r in curve],
        color="black",
        label="Bell pair, direct measurement",
        lw=1.4,
    )
    ax.plot(
        [r["p_a"] for r in curve],
        [r["classical_match"] for r in curve],
        color="0.4",
        linestyle="--",
        label="Independent classical choices",
        lw=1.4,
    )
    ax.set(
        xlabel=r"Classical comparison parameter $p_A$ ($p_B = 0.2$)",
        ylabel="Match probability",
        ylim=(0, 1.06),
    )
    ax.grid(alpha=0.15)
    ax.legend(frameon=False, loc="lower left", fontsize=9)
    fig.savefig(folder / "coordination-curve.png")
    plt.close(fig)


def render_pdf(text):
    from functools import partial
    from io import BytesIO

    import matplotlib.font_manager as fm
    from matplotlib.mathtext import math_to_image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import (
        Image,
        KeepTogether,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    _, fontpaths = academic_fonts()
    for name, path in zip(
        ["Body", "BodyBold", "BodyItalic", "BodyBoldItalic"], fontpaths, strict=True
    ):
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "Body", normal="Body", bold="BodyBold", italic="BodyItalic", boldItalic="BodyBoldItalic"
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="PaperBody",
            fontName="Body",
            fontSize=12,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            splitLongWords=False,
            allowWidows=False,
            allowOrphans=False,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PaperTitle",
            fontName="BodyBold",
            fontSize=16,
            leading=19,
            alignment=TA_CENTER,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PaperH1",
            fontName="BodyBold",
            fontSize=13,
            leading=17,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PaperH2",
            fontName="BodyBold",
            fontSize=12,
            leading=15,
            spaceBefore=9,
            spaceAfter=5,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(name="CaptionText", fontName="Body", fontSize=10, leading=12, spaceAfter=8)
    )
    styles.add(ParagraphStyle(name="TableText", fontName="Body", fontSize=9.5, leading=11.5))
    styles.add(ParagraphStyle(name="TableHead", fontName="BodyBold", fontSize=9.5, leading=11.5))
    styles.add(
        ParagraphStyle(
            name="Author",
            fontName="Body",
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Reference",
            parent=styles["PaperBody"],
            fontSize=10.5,
            leading=13,
            alignment=TA_LEFT,
        )
    )
    styles.add(ParagraphStyle(name="CodeProse", parent=styles["PaperBody"], alignment=TA_LEFT))
    doc = SimpleDocTemplate(
        str(PAPER / "research-paper.pdf"),
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72,
        title="Simulating Game Theory and Strategic Interactions Using Quantum Computing",
        author="Esther Cui",
        pageCompression=1,
    )
    width = doc.width
    story = []
    lines = text.splitlines()
    i = 0

    def para(s, style="PaperBody"):
        s = s.replace("theta_A", "θ_A").replace("theta_B", "θ_B")
        escaped = html.escape(s)
        escaped = re.sub(r"([A-Za-z0-9]+)\^(-?[0-9]+|T)", r"\1<super>\2</super>", escaped)
        escaped = re.sub(r"([A-Za-zθ]+)_([AB])\b", r"\1<sub>\2</sub>", escaped)
        escaped = re.sub(r"^(Table \d+[a-z]?\.|Figure \d+\.)", r"<b>\1</b>", escaped)
        return Paragraph(escaped, styles[style])

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("# "):
            story.append(para(line[2:], "PaperTitle"))
            i += 1
        elif line.startswith("## "):
            story.append(para(line[3:], "PaperH1"))
            i += 1
        elif line.startswith("### "):
            story.append(para(line[4:], "PaperH2"))
            i += 1
        elif line.startswith("```math"):
            i += 1
            formula = []
            while lines[i].strip() != "```":
                formula.append(lines[i].strip())
                i += 1
            buffer = BytesIO()
            math_to_image(
                "$" + " ".join(formula) + "$",
                buffer,
                dpi=260,
                format="png",
                prop=fm.FontProperties(size=12),
            )
            buffer.seek(0)
            im = Image(buffer)
            ratio = min(width / im.imageWidth, 72 / 260)
            im.drawWidth = im.imageWidth * ratio
            im.drawHeight = im.imageHeight * ratio
            story.extend([Spacer(1, 5), im, Spacer(1, 10)])
            i += 1
        elif line.startswith("!["):
            target = re.search(r"\]\(([^)]+)\)", line).group(1)
            im = Image(str(PAPER / target))
            scale = min((400 if "strategy-matrix" in target else width) / im.imageWidth, 1)
            im.drawWidth = im.imageWidth * scale
            im.drawHeight = im.imageHeight * scale
            block = [Spacer(1, 5), im, Spacer(1, 6)]
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].startswith("Figure "):
                block.append(para(lines[j], "CaptionText"))
                i = j + 1
            else:
                i += 1
            story.append(KeepTogether(block))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            count = len(rows[0])
            if rows[0][0] == "Configuration":
                weights = [1.8] + [1] * (count - 1)
            else:
                weights = [0.55] + [1] * (count - 1)
            widths = [width * v / sum(weights) for v in weights]
            data = [
                [para(v, "TableHead" if n == 0 else "TableText") for v in row]
                for n, row in enumerate(rows)
            ]
            t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
            t.setStyle(
                TableStyle(
                    [
                        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                        ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
                    ]
                )
            )
            block = [Spacer(1, 4), t, Spacer(1, 8)]
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].startswith("Table "):
                block.insert(0, para(lines[j], "CaptionText"))
                i = j + 1
            story.append(KeepTogether(block))
        else:
            parts = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not lines[i].startswith(("#", "|", "![", "```"))
            ):
                parts.append(lines[i].strip())
                i += 1
            value = " ".join(parts)
            if value == "Esther Cui":
                story.append(para(value, "Author"))
            elif value == "Revised computational manuscript | 3 October 2026":
                story.append(para("3 October 2026", "Author"))
            else:
                story.append(
                    para(
                        value,
                        "Reference"
                        if re.match(r"\[\d+\]", value)
                        else "CodeProse"
                        if any(token in value for token in ("scripts/", "src/", "results/"))
                        else "PaperBody",
                    )
                )

    # Keep section headings with the next actual content block (including tables/figures).
    packed = []
    cursor = 0
    while cursor < len(story):
        item = story[cursor]
        if isinstance(item, Paragraph) and item.style.name in ("PaperH1", "PaperH2"):
            group = [item]
            cursor += 1
            while cursor < len(story):
                following = story[cursor]
                if isinstance(following, PageBreak):
                    break
                if isinstance(following, KeepTogether):
                    group.extend(following._content)
                else:
                    group.append(following)
                cursor += 1
                if isinstance(following, Spacer):
                    continue
                if isinstance(following, Paragraph) and following.style.name in (
                    "PaperH1",
                    "PaperH2",
                ):
                    continue
                break
            packed.append(KeepTogether(group))
        else:
            packed.append(item)
            cursor += 1
    story = packed

    def page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Body", 10)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(letter[0] / 2, 36, str(doc.page))
        canvas.restoreState()

    doc.build(story, onFirstPage=page, onLaterPages=page, canvasmaker=partial(Canvas, invariant=1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()
    text, values, ewl, optimizer, experiments = material()
    output = PAPER / "manuscript.md"
    if args.check:
        assert output.read_text() == text, "Manuscript text/tables are stale."
        manifest = json.loads((PAPER / "build-manifest.json").read_text())
        for name, sha in manifest["sha256"].items():
            assert digest(ROOT / name) == sha, f"Manuscript build input/output changed: {name}"
        print("Manuscript text, tables, figures, PDF, and numerical source hashes agree.")
        return
    output.write_text(text)
    (PAPER / "numerical-values.json").write_text(json.dumps(values, indent=2) + "\n")
    if args.pdf:
        figures(ewl, experiments)
        render_pdf(text)
        paths = [
            PAPER / "manuscript.template.md",
            output,
            PAPER / "research-paper.pdf",
            PAPER / "numerical-values.json",
            ROOT / "scripts/build_manuscript.py",
            *sorted((PAPER / "figures").glob("*.png")),
            *[ROOT / f"results/ewl-k{k}.json" for k in [2, 3, 4]],
            ROOT / "results/optimization.json",
            ROOT / "results/experiments.json",
        ]
        (PAPER / "build-manifest.json").write_text(
            json.dumps(
                {
                    "renderer": {
                        "reportlab": __import__("reportlab").Version,
                        "matplotlib": __import__("matplotlib").__version__,
                        "body_font": academic_fonts()[0],
                        "font_sha256": {p.name: digest(p) for p in academic_fonts()[1]},
                    },
                    "sha256": {str(p.relative_to(ROOT)): digest(p) for p in paths},
                },
                indent=2,
            )
            + "\n"
        )
        print("Built paper/research-paper.pdf and its source-linked manuscript.")


if __name__ == "__main__":
    main()
