from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repo root is importable in environments where pytest import-mode
# does not automatically add it.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

