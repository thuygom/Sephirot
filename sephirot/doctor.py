"""Environment checks for agent and graph DB integrations."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def _which(command: str) -> Check:
    path = shutil.which(command)
    return Check(
        name=f"command:{command}",
        ok=path is not None,
        detail=path or "not found",
    )


def _env_any(name: str, alternatives: tuple[str, ...] = ()) -> Check:
    names = (name, *alternatives)
    found = [item for item in names if os.environ.get(item)]
    return Check(
        name="env:" + "|".join(names),
        ok=bool(found),
        detail="set: " + ", ".join(found) if found else "not set",
    )


def collect_checks() -> list[Check]:
    return [
        Check("python", True, f"{sys.version.split()[0]} on {platform.system()}"),
        _which("python3"),
        _which("claude"),
        _which("codex"),
        _which("cypher-shell"),
        _which("code"),
        _env_any("ANTHROPIC_API_KEY", ("ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN")),
        _env_any("OPENAI_API_KEY"),
        _env_any("NEO4J_URI"),
        _env_any("NEO4J_USER"),
        _env_any("NEO4J_PASSWORD"),
    ]


def checks_as_dict() -> list[dict[str, object]]:
    return [
        {"name": check.name, "ok": check.ok, "detail": check.detail}
        for check in collect_checks()
    ]
