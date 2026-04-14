"""
Local E2E / regression helpers.

- Default `pytest` run: one fast test that Django's live_server starts (no Playwright).
- Playwright stubs: remove @pytest.mark.skip on individual tests after `playwright install`
  and implement steps; or set RUN_E2E=1 only when browsers are installed.

Install (from repo root, using backend venv recommended):
  pip install -r e2e/requirements.txt
  playwright install
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Resolve Django project (backend/) on sys.path
_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

pytest_plugins = ["pytest_django"]


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: browser tests (Playwright), often skipped stubs")


@pytest.fixture
def run_e2e() -> bool:
    return os.environ.get("RUN_E2E", "").lower() in ("1", "true", "yes")
