"""Smoke tests for ml-automation-snowflake — validate plugin layout invariants."""

import json
import re
from pathlib import Path


def test_manifest_validity(manifest):
    """Verify that the plugin manifest is valid JSON and has required fields."""
    assert manifest is not None, "Manifest should be loadable"
    assert isinstance(manifest, dict), "Manifest should be a dict"
    assert manifest.get("name") == "spark-snowflake", "Manifest name should be 'spark-snowflake'"
    assert "version" in manifest, "Manifest should have a version field"
    assert "description" in manifest, "Manifest should have a description field"
    assert "cortex" in manifest, "Manifest should have a cortex configuration"
    cortex_config = manifest["cortex"]
    assert cortex_config.get("agents_dir") == "agents", "agents_dir should be 'agents'"
    assert cortex_config.get("skills_dir") == "skills", "skills_dir should be 'skills'"


def test_agents_md_referential_integrity(plugin_root, agents_md):
    """
    Verify that every agents/*.md file and skills/*/ directory is referenced in AGENTS.md.

    This test checks the file→AGENTS.md direction (orphans), not AGENTS.md→file
    (dangling refs). Known dangling refs like PM3-77's /connections are excluded.
    """
    # Collect existing agent files (stems without .md extension)
    agents_dir = plugin_root / "agents"
    agent_files = {f.stem for f in agents_dir.glob("*.md")}

    # Collect existing skill directories
    skills_dir = plugin_root / "skills"
    skill_dirs = {d.name for d in skills_dir.iterdir() if d.is_dir()}

    # Extract all agent references from AGENTS.md (markdown bold headers in tables, e.g., `| Agent | When to use |`)
    # Find the "Available Agents" section and extract backtick-quoted or plain text agent names
    agent_pattern = r"\|\s*`?([a-z0-9\-]+)`?\s*\|"
    agent_matches = re.findall(agent_pattern, agents_md)

    # Filter to likely agent names (should be lowercase with hyphens, matching our files)
    referenced_agents = {m for m in agent_matches if m in agent_files}

    # Extract all skill references from AGENTS.md (e.g., `/snowflake-sql`)
    skill_pattern = r"`/([a-z0-9\-]+)`"
    referenced_skills = set(re.findall(skill_pattern, agents_md))

    # Check that all agent files are referenced in AGENTS.md
    orphan_agents = agent_files - referenced_agents
    assert not orphan_agents, (
        f"Agent files not referenced in AGENTS.md (orphans): {sorted(orphan_agents)}"
    )

    # Check that all skill directories are referenced in AGENTS.md
    orphan_skills = skill_dirs - referenced_skills
    assert not orphan_skills, (
        f"Skill directories not referenced in AGENTS.md (orphans): {sorted(orphan_skills)}"
    )
