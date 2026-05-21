#!/usr/bin/env python3
"""
scripts/gen_pad_mockup.py
Sprint 4 — Variation 2: Custom script to generate a static PNG mockup of Pad Alpha.

Usage:
    pip install matplotlib numpy
    python scripts/gen_pad_mockup.py [--output OUTPUT]

Generates:
    gke/fault-trigger-ui/static/pad_alpha_mockup.png  (default)

Design: 2D schematic / technical drawing style, dark background, distinct
cyan accent for GDC Edge AI, matching the V2 API endpoint visual language.
Non-AI-generated, hand-authored positioning using matplotlib patches.

Elements:
  - Pad boundary
  - 6 ESP wells in a line (A-1 through A-6) with wellbore stubs
  - Production header / manifold
  - SCADA RTU (top-right, gray)
  - GDC Edge AI device (top-center, distinctive blue/cyan)
  - Power Generator (top-left, green-gray)
  - Starlink dish (far right)
  - Data & power connecting lines
  - Engineering title block (bottom-right)
  - Legend
"""

import argparse
import sys
from pathlib import Path

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")   # headless backend — no display required
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyArrowPatch
    import numpy as np
except ImportError:
    print("ERROR: matplotlib and numpy are required. Install with:")
    print("  pip install matplotlib numpy")
    sys.exit(1)

# ── Layout constants (inches @ 150 dpi → 1200 × 390 pixels) ──────────────────
FIG_W, FIG_H = 8.0, 2.6          # figure size in inches
DPI          = 150                # render resolution
BG_COLOR     = "#04080e"          # near-black navy
BORDER_COLOR = "#0d1e30"
GDC_BLUE     = "#006888"          # distinct GDC Edge AI colour
GDC_GLOW     = "#00a8c0"          # text / accent
GEN_COLOR    = "#0d1e14"          # generator box fill
SCADA_COLOR  = "#0d1e14"          # SCADA RTU box fill
WELL_STROKE  = "#00c8a0"          # healthy well colour
MANIFOLD_COL = "#0a2040"          # production header
DATA_LINE    = (0.0, 0.62, 0.75, 0.30)   # RGBA: cyan, semi-transparent
POWER_LINE   = (0.30, 0.24, 0.06, 0.45)  # RGBA: gold, semi-transparent

# Well x-positions (0→1 scale, clipped to pad interior)
WELL_XS     = [0.100, 0.225, 0.350, 0.475, 0.600, 0.720]
WELL_NAMES  = ["A-1", "A-2", "A-3", "A-4", "A-5", "A-6"]
WELL_DEPTHS = ["8,240 ft", "8,310 ft", "8,190 ft", "8,450 ft", "8,275 ft", "8,360 ft"]
WELL_Y      = 0.38     # well circle centre y (normalised)
WELL_R      = 0.048    # well circle radius (normalised)
MANIFOLD_Y  = 0.60     # production header y (normalised)


def _normalise(x, y, xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0):
    """Convert 0-1 normalised coords to data coords in the Axes."""
    return xmin + x * (xmax - xmin), ymin + y * (ymax - ymin)


def draw_rounded_box(ax, xc, yc, w, h, radius=0.012, fill=BG_COLOR,
                     edgecolor=BORDER_COLOR, lw=1.0, zorder=2):
    """Draw a rounded rectangle centred at (xc, yc)."""
    box = mpatches.FancyBboxPatch(
        (xc - w / 2, yc - h / 2), w, h,
        boxstyle=f"round,pad={radius}",
        facecolor=fill, edgecolor=edgecolor, linewidth=lw, zorder=zorder,
    )
    ax.add_patch(box)


def draw_equipment_box(ax, xc, yc, w, h, fill, edge, title, subtitle=None, zorder=3):
    """Draw a labelled equipment box."""
    draw_rounded_box(ax, xc, yc, w, h, fill=fill, edgecolor=edge, lw=1.2, zorder=zorder)
    ty = yc + 0.022 if subtitle else yc + 0.004
    ax.text(xc, ty, title, ha="center", va="center", fontsize=4.5,
            color=edge, fontweight="bold", fontfamily="monospace", zorder=zorder + 1)
    if subtitle:
        ax.text(xc, yc - 0.024, subtitle, ha="center", va="center", fontsize=3.8,
                color=BORDER_COLOR, fontfamily="monospace", zorder=zorder + 1)


def generate_mockup(output_path: Path) -> None:
    """Generate and save the Pad Alpha 2D mockup PNG."""
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.axis("off")

    # ── Pad bounding box ─────────────────────────────────────────────────────
    pad_rect = mpatches.FancyBboxPatch(
        (0.010, 0.035), 0.980, 0.940,
        boxstyle="round,pad=0.008",
        facecolor="none", edgecolor=BORDER_COLOR, linewidth=1.2, zorder=1,
    )
    ax.add_patch(pad_rect)
    ax.text(0.50, 0.98, "PAD ALPHA — ESP PRODUCTION",
            ha="center", va="top", fontsize=5.5,
            color="#0a3050", fontfamily="monospace", fontweight="bold", zorder=2)

    # ── Infrastructure equipment row ─────────────────────────────────────────

    # Generator (top-left)
    gen_x = 0.065
    draw_equipment_box(ax, gen_x, 0.83, 0.095, 0.10, GEN_COLOR, "#2a5040",
                       "GENERATOR", "500 kVA")

    # GDC Edge AI (top-center, distinct blue) — wider box with glowing accent
    gdc_x = 0.50
    draw_rounded_box(ax, gdc_x, 0.83, 0.19, 0.10, fill="#020e26",
                     edgecolor=GDC_BLUE, lw=1.8, zorder=3)
    # Top accent bar
    accent = mpatches.Rectangle((gdc_x - 0.095, 0.87), 0.190, 0.014,
                                  facecolor=GDC_BLUE, zorder=4)
    ax.add_patch(accent)
    # LED indicator dots
    ax.plot(gdc_x - 0.080, 0.877, "o", color="#00e676", ms=2.8, zorder=5)
    ax.plot(gdc_x - 0.060, 0.877, "o", color="#1e90ff", ms=2.8, zorder=5)
    ax.text(gdc_x, 0.848, "GDC EDGE AI", ha="center", va="center", fontsize=6,
            color=GDC_GLOW, fontweight="bold", fontfamily="monospace", zorder=5)
    ax.text(gdc_x, 0.823, "XGBoost · Gemma4 · RAG",
            ha="center", va="center", fontsize=3.8,
            color=GDC_BLUE, fontfamily="monospace", zorder=5)
    ax.text(gdc_x, 0.803, "Inference: 48 ms · Edge",
            ha="center", va="center", fontsize=3.5,
            color="#065060", fontfamily="monospace", zorder=5)

    # SCADA RTU (top-right)
    scada_x = 0.810
    draw_equipment_box(ax, scada_x, 0.83, 0.100, 0.10, SCADA_COLOR, "#2a4028",
                       "SCADA RTU", "Threshold Only")

    # Starlink dish (far right)
    sl_x, sl_y = 0.945, 0.84
    # Dish ellipse (tilted)
    dish = mpatches.Ellipse((sl_x, sl_y + 0.015), width=0.050, height=0.022,
                             angle=-20, facecolor="none",
                             edgecolor="#0a3848", linewidth=1.2, zorder=3)
    ax.add_patch(dish)
    ax.plot([sl_x, sl_x], [sl_y, sl_y - 0.025], color="#0a2838", lw=1.2, zorder=3)
    ax.plot([sl_x - 0.016, sl_x + 0.016], [sl_y - 0.025, sl_y - 0.025],
            color="#0a2838", lw=1.5, zorder=3)
    ax.text(sl_x, sl_y - 0.055, "STARLINK", ha="center", va="center", fontsize=3.5,
            color="#0a3850", fontfamily="monospace", zorder=3)

    # ── Connecting lines ─────────────────────────────────────────────────────

    # Data line: GDC → SCADA (cyan dashed)
    ax.annotate("", xy=(scada_x - 0.052, 0.83), xytext=(gdc_x + 0.098, 0.83),
                arrowprops=dict(arrowstyle="->", color=DATA_LINE, lw=0.9,
                                linestyle="dashed", connectionstyle="arc3,rad=0"))

    # Data line: SCADA → Starlink
    ax.plot([scada_x + 0.052, sl_x - 0.026], [0.83, 0.855],
            color=DATA_LINE, lw=0.7, linestyle=(0, (2, 5)), zorder=2)

    # Power line: GEN → manifold level (vertical dashed gold)
    ax.plot([gen_x, gen_x], [0.78, MANIFOLD_Y + 0.015],
            color=POWER_LINE, lw=1.0, linestyle=(0, (3, 4)), zorder=2)

    # Data line: GDC → manifold (vertical cyan dotted)
    ax.plot([gdc_x, gdc_x], [0.78, MANIFOLD_Y + 0.015],
            color=DATA_LINE, lw=0.8, linestyle=(0, (2, 5)), zorder=2)

    # ── Production manifold ───────────────────────────────────────────────────
    # Main horizontal line
    ax.plot([0.040, 0.840], [MANIFOLD_Y, MANIFOLD_Y],
            color=MANIFOLD_COL, lw=4.0, solid_capstyle="round", zorder=3)
    # Flow arrow
    ax.annotate("", xy=(0.860, MANIFOLD_Y), xytext=(0.840, MANIFOLD_Y),
                arrowprops=dict(arrowstyle="->", color=MANIFOLD_COL, lw=2.0))

    # Separator box
    draw_rounded_box(ax, 0.900, MANIFOLD_Y, 0.072, 0.055,
                     fill="#030a10", edgecolor=BORDER_COLOR, lw=0.9, zorder=3)
    ax.text(0.900, MANIFOLD_Y, "SEPARATOR", ha="center", va="center", fontsize=3.5,
            color="#1a3040", fontfamily="monospace", zorder=4)

    ax.text(0.78, MANIFOLD_Y + 0.030, "PROD. HEADER",
            ha="center", va="center", fontsize=3.8,
            color="#1a3040", fontfamily="monospace", zorder=4)

    # ── Vertical connections: manifold → wells ────────────────────────────────
    for wx in WELL_XS:
        ax.plot([wx, wx], [MANIFOLD_Y - 0.005, WELL_Y + WELL_R + 0.005],
                color="#0e2236", lw=1.5, zorder=3)

    # ── ESP Well circles ─────────────────────────────────────────────────────
    for wx, wname, wdepth in zip(WELL_XS, WELL_NAMES, WELL_DEPTHS):
        # Glow fill (subtle circle)
        glow_circle = plt.Circle((wx, WELL_Y), WELL_R * 1.15,
                                  facecolor=(0.0, 0.78, 0.63, 0.12),
                                  edgecolor="none", zorder=3)
        ax.add_patch(glow_circle)
        # Well circle
        well_circle = plt.Circle((wx, WELL_Y), WELL_R,
                                  facecolor=(0.0, 0.78, 0.63, 0.14),
                                  edgecolor=WELL_STROKE, linewidth=1.5, zorder=4)
        ax.add_patch(well_circle)
        # Labels
        ax.text(wx, WELL_Y + 0.008, "ESP", ha="center", va="center", fontsize=4.5,
                color=WELL_STROKE, fontweight="bold", fontfamily="monospace", zorder=5)
        ax.text(wx, WELL_Y - 0.016, wname, ha="center", va="center", fontsize=4.0,
                color="#4a7a8a", fontfamily="monospace", zorder=5)
        ax.text(wx, WELL_Y - 0.038, wdepth, ha="center", va="center", fontsize=3.2,
                color="#2a4a5a", fontfamily="monospace", zorder=5)
        # Wellbore stub (dashed line below circle)
        ax.plot([wx, wx], [WELL_Y - WELL_R - 0.002, WELL_Y - WELL_R - 0.025],
                color="#0a1828", lw=0.9, linestyle=(0, (2, 2)), zorder=3)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_y = 0.060
    lx = 0.015
    # Healthy well
    ax.plot(lx, legend_y, "o", color=WELL_STROKE, ms=4.5, zorder=5,
            markerfacecolor=(0, 0.78, 0.63, 0.18))
    ax.text(lx + 0.016, legend_y, "Healthy", va="center", fontsize=3.5,
            color="#1a4a5a", fontfamily="monospace")
    # Warning well
    ax.plot(lx + 0.090, legend_y, "o", color="#f59e0b", ms=4.5, zorder=5,
            markerfacecolor=(0.96, 0.62, 0.04, 0.18))
    ax.text(lx + 0.090 + 0.016, legend_y, "Warning", va="center", fontsize=3.5,
            color="#1a4a5a", fontfamily="monospace")
    # Critical well
    ax.plot(lx + 0.200, legend_y, "o", color="#ef4444", ms=4.5, zorder=5,
            markerfacecolor=(0.94, 0.27, 0.27, 0.18))
    ax.text(lx + 0.200 + 0.016, legend_y, "Critical", va="center", fontsize=3.5,
            color="#1a4a5a", fontfamily="monospace")
    # Data line
    ax.plot([lx + 0.300, lx + 0.350], [legend_y, legend_y],
            color=DATA_LINE, lw=1.2, linestyle=(0, (3, 3)))
    ax.text(lx + 0.350 + 0.008, legend_y, "Data", va="center", fontsize=3.5,
            color="#1a4a5a", fontfamily="monospace")
    # Power line
    ax.plot([lx + 0.400, lx + 0.450], [legend_y, legend_y],
            color=POWER_LINE, lw=1.2, linestyle=(0, (3, 3)))
    ax.text(lx + 0.450 + 0.008, legend_y, "Power", va="center", fontsize=3.5,
            color="#1a4a5a", fontfamily="monospace")

    # ── Title block (bottom-right, standard engineering drawing format) ───────
    tb_x, tb_y = 0.640, 0.055
    draw_rounded_box(ax, tb_x + 0.175, tb_y, 0.350, 0.080,
                     fill="#020810", edgecolor=BORDER_COLOR, lw=0.7, zorder=2)
    # Dividers
    ax.plot([tb_x + 0.175, tb_x + 0.175],
            [tb_y - 0.040, tb_y + 0.040], color=BORDER_COLOR, lw=0.5, zorder=3)
    ax.plot([tb_x, tb_x + 0.350],
            [tb_y + 0.008, tb_y + 0.008], color=BORDER_COLOR, lw=0.5, zorder=3)
    ax.text(tb_x + 0.060, tb_y + 0.022, "PAD ALPHA — ESP PRODUCTION",
            ha="center", va="center", fontsize=3.5, color="#0a4060",
            fontfamily="monospace", zorder=4)
    ax.text(tb_x + 0.060, tb_y - 0.012, "GDC-PM · Sprint 4 · V2 · PNG",
            ha="center", va="center", fontsize=3.0, color="#082838",
            fontfamily="monospace", zorder=4)
    ax.text(tb_x + 0.270, tb_y + 0.022, "DWG: PA-2D-001",
            ha="center", va="center", fontsize=3.5, color="#0a4060",
            fontfamily="monospace", zorder=4)
    ax.text(tb_x + 0.270, tb_y - 0.012, "REV: Sprint 4",
            ha="center", va="center", fontsize=3.0, color="#082838",
            fontfamily="monospace", zorder=4)

    # ── Save ─────────────────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=DPI, bbox_inches="tight",
                facecolor=BG_COLOR, edgecolor="none")
    plt.close(fig)
    print(f"✅ Pad Alpha mockup PNG saved → {output_path}")
    print(f"   Size: {output_path.stat().st_size // 1024} KB")
    print(f"   Resolution: {int(FIG_W * DPI)} × {int(FIG_H * DPI)} px @ {DPI} dpi")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Pad Alpha 2D schematic PNG (Sprint 4, Mockup V2)"
    )
    default_out = Path(__file__).parent.parent / "gke" / "fault-trigger-ui" / "static" / "pad_alpha_mockup.png"
    parser.add_argument(
        "--output", "-o",
        type=Path, default=default_out,
        help=f"Output PNG path (default: {default_out})"
    )
    args = parser.parse_args()
    generate_mockup(args.output)


if __name__ == "__main__":
    main()
