"""Shared pytest configuration for the SOLEX film package.

* Forces the matplotlib ``Agg`` backend so figure tests never open a display.
* Adds ``src/`` to ``sys.path`` (belt-and-braces beside the ``pythonpath``
  setting in ``pyproject.toml``) so the package imports in any run mode.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
