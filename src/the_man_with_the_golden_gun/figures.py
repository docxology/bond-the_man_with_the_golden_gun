"""Deterministic figure generation for the SOLEX film package.

One matplotlib figure per domain concept, all written under ``output/figures/``
and rendered with the ``Agg`` backend so nothing needs a display. Figures are
pure functions of the canonical domain constants — regenerating them produces
byte-identical PNGs (a live determinism proof).

* :func:`plot_solex_yield` — thermal heat output vs. direct normal irradiance;
* :func:`plot_lair_topology` — the funhouse lair graph with the escape route
  and bottleneck rooms highlighted;
* :func:`plot_duel_schedule` — the bounty appointment book as a Gantt chart
  with the weighted-interval-scheduling selection highlighted.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .duel_scheduler import CANONICAL_DUELS, max_bounty_schedule  # noqa: E402
from .lair_topology import canonical_lair, find_escape_path, mirror_gated_bottlenecks  # noqa: E402
from .solar_concentration import (  # noqa: E402
    SOLEX_DNI,
    SOLEX_FIELD,
    SOLEX_RECEIVER_AREA_M2,
    concentration_ratio,
    thermal_output_kw,
)
from .solar_tracking import SOLEX_LATITUDE_DEG, solex_daily_profile  # noqa: E402

__all__ = [
    "generate_all_figures",
    "plot_daily_solar_profile",
    "plot_duel_schedule",
    "plot_lair_topology",
    "plot_solex_yield",
]

DEFAULT_FIGURES_DIR = Path(__file__).resolve().parents[2] / "output" / "figures"


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def plot_solex_yield(path: str | Path | None = None) -> Path:
    """Heat output (kW) vs DNI for the canonical mirror field.

    Also draws the concentration ratio on a secondary axis to show both the
    yield (power) and the focusing (concentration) characterisations.
    """
    out = Path(path) if path is not None else DEFAULT_FIGURES_DIR / "solex_yield.png"
    _ensure_dir(out)
    dni_grid = np.linspace(200.0, 1400.0, 61)
    heat = [thermal_output_kw(SOLEX_FIELD, float(dni)) for dni in dni_grid]
    ratio = concentration_ratio(SOLEX_FIELD, SOLEX_RECEIVER_AREA_M2, dni=float(dni_grid[-1]))

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(dni_grid, heat, color="#1f77b4", label="Thermal output (kW)")
    ax.set_xlabel("Direct normal irradiance (W/m²)")
    ax.set_ylabel("Heat output (kW)")
    ax.axvline(SOLEX_DNI, color="#2ca02c", linestyle="--", alpha=0.7, label="Canonical DNI")
    ax.set_title(f"SOLEX solar concentration yield (C ≈ {ratio:.1f})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def plot_lair_topology(path: str | Path | None = None) -> Path:
    """Draw the funhouse lair graph, escape route, and bottleneck rooms."""
    out = Path(path) if path is not None else DEFAULT_FIGURES_DIR / "lair_topology.png"
    _ensure_dir(out)
    graph, entry, exit_ = canonical_lair()
    route = find_escape_path(graph, entry, exit_)
    path_rooms: list[str] = list(route) if route is not None else []
    bottlenecks = set(mirror_gated_bottlenecks(graph, entry, exit_))

    rooms = list(graph)
    pos = {room: (float(i % 3), float(-(i // 3))) for i, room in enumerate(rooms)}
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for room in rooms:
        for neighbour in graph[room]:
            if room < neighbour:
                ax.plot(
                    [pos[room][0], pos[neighbour][0]],
                    [pos[room][1], pos[neighbour][1]],
                    color="grey",
                    linewidth=1,
                    zorder=1,
                )
    for i, room in enumerate(path_rooms[:-1]):
        nxt = path_rooms[i + 1]
        ax.plot([pos[room][0], pos[nxt][0]], [pos[room][1], pos[nxt][1]], color="#e377c2", linewidth=3, zorder=2)
    for room in rooms:
        color = "#d62728" if room in bottlenecks else "#1f77b4"
        ax.scatter(*pos[room], s=700 if room in (entry, exit_) else 420, color=color, edgecolor="black", zorder=3)
        ax.text(pos[room][0], pos[room][1], room, ha="center", va="center", fontsize=7, color="white", zorder=4)
    ax.set_title("SOLEX funhouse lair — escape topology")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def plot_duel_schedule(path: str | Path | None = None) -> Path:
    """Appointment book as a Gantt chart with the max-bounty selection filled."""
    out = Path(path) if path is not None else DEFAULT_FIGURES_DIR / "duel_schedule.png"
    _ensure_dir(out)
    _, selected = max_bounty_schedule(CANONICAL_DUELS)
    selected_set = set(selected)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ordered = sorted(CANONICAL_DUELS, key=lambda a: (a.start, a.id))
    for i, appt in enumerate(ordered):
        color = "#2ca02c" if appt.id in selected_set else "#ff7f0e"
        ax.barh(i, appt.end - appt.start, left=appt.start, height=0.6, color=color, alpha=0.9)
        ax.text(appt.end + 0.05, i, f"{appt.id}:{appt.bounty:.0f}", va="center", fontsize=8)
    ax.set_yticks(range(len(ordered)))
    ax.set_yticklabels([a.id for a in ordered])
    ax.set_xlabel("Time")
    ax.set_title("SOLEX bounty appointment book — max-bounty selection")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def plot_daily_solar_profile(path: str | Path | None = None) -> Path:
    """Beam flux on the horizontal plane across the canonical SOLEX day.

    Uses :func:`solex_daily_profile` (Spencer declination + Duffie–Beckman
    geometry) to draw the deterministic sunrise-to-sunset flux curve.
    """
    out = Path(path) if path is not None else DEFAULT_FIGURES_DIR / "solex_daily.png"
    _ensure_dir(out)
    profile = solex_daily_profile()

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(profile["solar_time_h"], profile["beam_kw_m2"], color="#1f77b4", linewidth=2)
    ax.fill_between(profile["solar_time_h"], profile["beam_kw_m2"], alpha=0.25, color="#1f77b4")
    ax.set_xlabel("Solar time (hours)")
    ax.set_ylabel("Horizontal beam flux (kW/m²)")
    ax.set_title(f"SOLEX daily solar profile (lat {SOLEX_LATITUDE_DEG:.0f}°N, solstice)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def generate_all_figures(output_dir: str | Path | None = None) -> tuple[Path, Path, Path, Path]:
    """Render all four SOLEX figures into ``output_dir`` (default figures dir)."""
    base = Path(output_dir) if output_dir is not None else DEFAULT_FIGURES_DIR
    return (
        plot_solex_yield(base / "solex_yield.png"),
        plot_daily_solar_profile(base / "solex_daily.png"),
        plot_lair_topology(base / "lair_topology.png"),
        plot_duel_schedule(base / "duel_schedule.png"),
    )
