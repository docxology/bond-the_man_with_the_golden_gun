#!/usr/bin/env python
"""SOLEX manuscript variable hydration.

Writes ``output/data/manuscript_variables.json`` (the ``{{TOKEN}}`` map) and
the resolved manuscript tree under ``output/manuscript/`` from
``manuscript/[0-9]*.md``. Strict by default: an unresolved workspace raises.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import _bootstrap  # noqa: E402,F401

from the_man_with_the_golden_gun.manuscript_variables import (  # noqa: E402
    generate_variables,
    unresolved_tokens,
    write_resolved_tree,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    variables = generate_variables()
    data_dir = PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    variables_path = data_dir / "manuscript_variables.json"
    variables_path.write_text(json.dumps(variables, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    written = write_resolved_tree(variables)

    # Strict gate: no unresolved tokens may remain in any resolved section.
    broken = [p for p in written if unresolved_tokens(p.read_text(encoding="utf-8"))]
    result = "\n".join(f"unresolved token in {path}" for path in broken)
    print(f"wrote {variables_path}")
    print(f"resolved {len(written)} sections")

    if broken:
        print(result, file=sys.stderr)
        return 1
    print("all manuscript tokens resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())  # noqa: B904
