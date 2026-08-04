"""Subprocess smoke tests for the SOLEX thin CLI scripts (real executions)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / script), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_preflight_ok() -> None:
    proc = _run("00_preflight.py")
    assert proc.returncode == 0, proc.stderr
    assert "preflight OK" in proc.stdout


def test_brief_cli() -> None:
    proc = _run("brief.py")
    assert proc.returncode == 0, proc.stderr
    assert "MissionBrief" in proc.stdout
    assert "SOLEX" in proc.stdout


def test_run_mission_bad_phase_exit_2() -> None:
    proc = _run("run_mission.py", "not-a-phase")
    assert proc.returncode == 2
    assert "unknown phase" in proc.stderr


def test_generate_artifacts_writes_output() -> None:
    proc = _run("generate_artifacts.py")
    assert proc.returncode == 0, proc.stderr
    assert (PROJECT_ROOT / "output" / "data" / "solex_outcome.json").exists()
    assert (PROJECT_ROOT / "output" / "figures" / "solex_yield.png").exists()


def test_generate_manuscript_variables() -> None:
    proc = _run("z_generate_manuscript_variables.py")
    assert proc.returncode == 0, proc.stderr
    assert "all manuscript tokens resolved" in proc.stdout
    assert (PROJECT_ROOT / "output" / "data" / "manuscript_variables.json").exists()
    assert (PROJECT_ROOT / "output" / "manuscript" / "00_abstract.md").exists()
