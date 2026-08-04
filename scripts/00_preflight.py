#!/usr/bin/env python
"""SOLEX preflight: verify the package is discoverable and satisfies the protocol.

Loads the provider by slug through ``bond_api.discovery`` (exactly as the
orchestrator does), checks the runtime protocol, and reports package identity.
Exit code 0 iff every check passes.
"""

from __future__ import annotations

import sys

import _bootstrap  # noqa: E402,F401

from bond_api.discovery import load_provider  # noqa: E402
from bond_api.protocol import MissionProvider  # noqa: E402

SLUG = "the_man_with_the_golden_gun"


def main() -> int:
    provider = load_provider(SLUG)
    if not isinstance(provider, MissionProvider):
        print(f"FAIL: {SLUG} does not satisfy the MissionProvider protocol", file=sys.stderr)
        return 1
    print(f"preflight OK: film={provider.film} codename={provider.brief().codename}")
    print(f"objectives={len(provider.brief().objectives)} steps={len(provider.plan(provider.brief()).steps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())  # noqa: B904
