"""Runtime readiness checker for Startup Opportunity Aggregator.

This script validates environment dependencies and prints actionable output
without crashing when modules are missing.
"""

from __future__ import annotations

import importlib
import sys
from typing import Iterable

REQUIRED_MODULES: tuple[str, ...] = (
    "flask",
    "flask_sqlalchemy",
    "sqlalchemy",
    "dotenv",
    "requests",
    "bs4",
    "tenacity",
    "marshmallow",
    "rapidfuzz",
    "apscheduler",
    "pandas",
)


def check_modules(modules: Iterable[str]) -> tuple[list[str], list[str]]:
    ok: list[str] = []
    missing: list[str] = []
    for module in modules:
        try:
            importlib.import_module(module)
            ok.append(module)
        except Exception:
            missing.append(module)
    return ok, missing


def main() -> int:
    ok, missing = check_modules(REQUIRED_MODULES)

    print("=== Startup Opportunity Aggregator | Environment Check ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Installed required modules: {len(ok)}/{len(REQUIRED_MODULES)}")

    if ok:
        print("\nOK modules:")
        for item in ok:
            print(f"  - {item}")

    if missing:
        print("\nMissing modules:")
        for item in missing:
            print(f"  - {item}")

        print("\nFix:")
        print("  pip install -r requirements.txt")
        print("  # or use your internal package mirror if public pip is blocked")
        return 1

    print("\nStatus: READY ✅")
    print("You can now run: python run.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
