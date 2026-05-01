"""Shared pytest fixtures for ml-automation-snowflake."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def plugin_root():
    """Return the root directory of the plugin."""
    return Path(__file__).parent.parent


@pytest.fixture
def manifest(plugin_root):
    """Load and return the plugin manifest from .cortex-plugin/plugin.json."""
    manifest_path = plugin_root / ".cortex-plugin" / "plugin.json"
    with open(manifest_path) as f:
        return json.load(f)


@pytest.fixture
def agents_md(plugin_root):
    """Load and return the contents of AGENTS.md."""
    agents_path = plugin_root / "AGENTS.md"
    with open(agents_path) as f:
        return f.read()
