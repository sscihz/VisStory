"""Matplotlib theme helpers for the textbook figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt

BACKGROUND = "#f7f4ef"
INK = "#202124"
MUTED = "#6b7280"
GRID = "#ded8cf"
ACCENT = "#e95f2b"
BLUE = "#2563eb"
GREEN = "#16a34a"
PURPLE = "#7c3aed"
RED = "#dc2626"
YELLOW = "#f59e0b"

POSITION_COLORS = {
    "Guard": BLUE,
    "Forward": ACCENT,
    "Center": GREEN,
}


def _register_cjk_font_files() -> None:
    """Register common Linux CJK font files before selecting font families."""
    for font_path in [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    ]:
        if font_path.exists():
            font_manager.fontManager.addfont(str(font_path))


def configure_matplotlib() -> None:
    """Apply a clean theme and use a Chinese-capable font when available."""
    _register_cjk_font_files()
    available = {font.name for font in font_manager.fontManager.ttflist}
    preferred_fonts = [
        "Noto Sans CJK SC",
        "Noto Sans CJK JP",
        "Source Han Sans SC",
        "WenQuanYi Zen Hei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    font_family = next((font for font in preferred_fonts if font in available), "DejaVu Sans")
    plt.rcParams.update(
        {
            "font.family": font_family,
            "font.sans-serif": preferred_fonts,
            "axes.facecolor": BACKGROUND,
            "figure.facecolor": BACKGROUND,
            "axes.edgecolor": GRID,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "axes.grid": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.facecolor": BACKGROUND,
            "savefig.edgecolor": BACKGROUND,
            "figure.dpi": 140,
        }
    )


def save_figure(fig: plt.Figure, path: Path, *, close: bool = True) -> Path:
    """Save a figure, ensuring the parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    if path.suffix.lower() == ".png":
        fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    if close:
        plt.close(fig)
    return path


def add_source_note(fig: plt.Figure, note: str) -> None:
    """Add a small source note at the bottom-left of a figure."""
    fig.text(0.01, 0.01, note, color=MUTED, fontsize=8, ha="left", va="bottom")
