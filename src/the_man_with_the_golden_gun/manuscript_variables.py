"""Manuscript variable hydration for the SOLEX film package.

Every ``{{TOKEN}}`` in ``manuscript/[0-9]*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` and the
deterministic domain models. Metrics are never hand-authored in prose — they
flow through this module so the manuscript cannot drift from the code.

Consumed by ``scripts/z_generate_manuscript_variables.py`` (thin wrapper); the
live cross-reference gate lives in ``tests/test_manuscript_variables.py``.
"""

from __future__ import annotations

import platform
import re
from pathlib import Path
from typing import Any

import yaml

from .duel_scheduler import CANONICAL_DUELS, find_conflicts, max_bounty_schedule
from .lair_topology import (
    CANONICAL_ENTRY,
    CANONICAL_EXIT,
    articulation_points,
    canonical_lair,
    escape_distance,
    find_escape_path,
    mirror_gated_bottlenecks,
)
from .solar_concentration import (
    SOLEX_DNI,
    SOLEX_FIELD,
    SOLEX_RECEIVER_AREA_M2,
    concentration_ratio,
    field_optical_power,
    solex_heat_output_kw,
)

__all__ = ["DEFAULT_TIMESTAMP", "generate_variables", "load_manuscript_config"]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

#: Fixed build timestamp for byte-deterministic outputs (no wall-clock).
DEFAULT_TIMESTAMP = "2026-08-04T00:00:00Z"

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def load_manuscript_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate ``manuscript/config.yaml`` (or an explicit path)."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manuscript config must be a top-level mapping, got {type(data).__name__}")
    return data


def generate_variables(
    *,
    config_path: str | Path | None = None,
    now: str = DEFAULT_TIMESTAMP,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` → value mapping for the SOLEX manuscript.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        now: Fixed timestamp injected into the token map (defaults to the
            deterministic :data:`DEFAULT_TIMESTAMP` so outputs are byte-stable).
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        paper = {}

    graph = canonical_lair()[0]
    path = find_escape_path(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    distance = escape_distance(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    bottlenecks = mirror_gated_bottlenecks(graph, CANONICAL_ENTRY, CANONICAL_EXIT)
    arts = articulation_points(graph)
    bounty, selected = max_bounty_schedule(CANONICAL_DUELS)
    conflicts = find_conflicts(CANONICAL_DUELS)

    optical_kw = field_optical_power(SOLEX_FIELD, SOLEX_DNI) / 1000.0

    return {
        "BOND_TITLE": str(paper.get("title", "The Man with the Golden Gun: SOLEX")),
        "BOND_CODENAME": "SOLEX",
        "SOLEX_FIELD_AREA": f"{sum(m.area_m2 for m in SOLEX_FIELD):.1f}",
        "SOLEX_DNI": f"{SOLEX_DNI:.0f}",
        "SOLEX_OPTICAL_POWER_KW": f"{optical_kw:.1f}",
        "SOLEX_HEAT_KW": f"{solex_heat_output_kw():.4f}",
        "SOLEX_CONCENTRATION": f"{concentration_ratio(SOLEX_FIELD, SOLEX_RECEIVER_AREA_M2):.2f}",
        "SOLEX_RECEIVER_AREA_M2": f"{SOLEX_RECEIVER_AREA_M2:.1f}",
        "LAIR_NUM_ROOMS": str(len(graph)),
        "LAIR_ESCAPE_DISTANCE": str(distance) if distance is not None else "INF",
        "LAIR_ESCAPE_PATH": " -> ".join(path) if path else "NONE",
        "LAIR_NUM_BOTTLENECKS": str(len(bottlenecks)),
        "LAIR_BOTTLENECKS": ", ".join(bottlenecks) if bottlenecks else "NONE",
        "LAIR_NUM_ARTICULATION": str(len(arts)),
        "DUEL_NUM_DUELS": str(len(CANONICAL_DUELS)),
        "DUEL_TOTAL_BOUNTY": f"{bounty:.1f}",
        "DUEL_SELECTED": ", ".join(selected) if selected else "NONE",
        "DUEL_NUM_CONFLICTS": str(len(conflicts)),
        "PYTHON_VERSION": platform.python_version(),
        "GENERATION_TIMESTAMP": now,
    }


def unresolved_tokens(text: str) -> list[str]:
    """Return any ``{{TOKEN}}`` placeholders still present in ``text``."""
    return _TOKEN_RE.findall(text)


def resolve_text(text: str, variables: dict[str, str]) -> str:
    """Substitute every ``{{TOKEN}}`` in ``text`` using ``variables``."""

    def _sub(match: re.Match[str]) -> str:
        return variables.get(match.group(0)[2:-2], match.group(0))

    return _TOKEN_RE.sub(_sub, text)


def write_resolved_tree(
    variables: dict[str, str],
    source_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
) -> list[Path]:
    """Substitute tokens across the numbered manuscript sections.

    Copies each ``manuscript/[0-9]*.md`` into ``out_dir`` (default
    ``output/manuscript/``) with every ``{{TOKEN}}`` replaced, and returns the
    written paths. Unresolved tokens are left verbatim so the live
    cross-reference test can detect drift.
    """
    src = Path(source_dir) if source_dir is not None else PACKAGE_ROOT / "manuscript"
    out = Path(out_dir) if out_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for section in sorted(src.glob("[0-9]*.md")):
        target = out / section.name
        target.write_text(resolve_text(section.read_text(encoding="utf-8"), variables), encoding="utf-8")
        written.append(target)
    return written
