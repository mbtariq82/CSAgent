#!/usr/bin/env python3
"""Run the project-owned CyberGym baseline checks.

Examples are documented in ``security_agent/benchmarks/cybergym/README.md``. The module is
deliberately dependency-light so it can be used before the benchmark venv is
installed.
"""

import sys
from pathlib import Path

# Running a script sets sys.path[0] to ``scripts/``. Add the repository root so
# the wrapper works exactly as documented from any current directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from security_agent.benchmarks.cybergym.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
