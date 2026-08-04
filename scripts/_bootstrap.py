"""Shared sys.path bootstrap for SOLEX CLI scripts.

Scripts are thin argv-forwarding wrappers; each inserts ``src/`` onto
``sys.path`` (via this helper) so a bare ``python scripts/<name>.py`` call
imports the package without a package installation. Guardrail note: this
module lives under a 4-level-deep path where the root per-file-ignore E402
pattern does not apply, so the import lines below carry explicit ``noqa``.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
