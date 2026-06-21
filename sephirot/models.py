"""Spec factories and JSON helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canon import ASCENT_SEPHIROT, PATHS


Spec = dict[str, Any]


def blank_spec(context: str = "") -> Spec:
    """Create an empty Malkuth-to-Kether seed spec."""

    return {
        "schema_version": "0.1",
        "context": context,
        "threshold": 0.2,
        "malkuth": {
            "human_state": "",
            "current_state": "",
            "evidence": [],
        },
        "kether": {
            "target_state": "",
            "success_condition": "",
            "evidence": [],
        },
        "sephira": {
            profile.name: {
                "focus_value": profile.focus_value,
                "domain_instantiation": "",
                "desired_state": "",
                "evidence": [],
                "qliphoth_risk": "",
            }
            for profile in ASCENT_SEPHIROT
        },
        "paths": {
            str(profile.number): {
                "from": profile.source,
                "to": profile.target,
                "cq": profile.cq,
                "answer": "",
                "evidence": [],
                "qliphoth_check": "",
            }
            for profile in PATHS
        },
    }


def load_json(path: str | Path) -> Spec:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(data: Any, path: str | Path | None = None) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    return text


def ensure_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.split(";") if part.strip()]
    return [str(value).strip()]
