#!/usr/bin/env python3
"""Run full project health checks (env, data, pipeline, tests)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(label: str, cmd: list[str]) -> bool:
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    result = subprocess.run(cmd, cwd=ROOT)
    ok = result.returncode == 0
    print(f"-> {'PASS' if ok else 'FAIL'} ({label})")
    return ok


def main() -> int:
    checks = [
        ("Environment (.env)", [sys.executable, "scripts/check_env.py"]),
        ("Unit tests", [sys.executable, "-m", "pytest", "-q"]),
        ("Data smoke", [sys.executable, "scripts/smoke_data.py"]),
        ("Mock demos", [sys.executable, "scripts/run_demos.py"]),
    ]

    results: list[bool] = []
    for label, cmd in checks:
        results.append(_run(label, cmd))

    print(f"\n{'=' * 60}\nOptional live checks (require Groq API)\n{'=' * 60}")
    print("Run manually if needed:")
    print("  python -m pytest -m integration -q")
    print("  python scripts/smoke_recommend.py")
    print("  streamlit run src/app/main.py")
    print("  uvicorn src.api.main:app --port 8001")

    passed = sum(results)
    total = len(results)
    print(f"\nSummary: {passed}/{total} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
