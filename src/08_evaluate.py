from __future__ import annotations

from pathlib import Path
import runpy


if __name__ == "__main__":
    script = Path(__file__).resolve().parents[1] / "scripts" / "evaluate.py"
    runpy.run_path(str(script), run_name="__main__")
