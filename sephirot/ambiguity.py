"""Ambiguity scoring for specification-first Sephirot seeds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canon import ASCENT_SEPHIROT, PATHS


MIN_STRONG_CHARS = 24


@dataclass(frozen=True)
class AmbiguityItem:
    key: str
    question: str
    weight: float
    missing: float


def _string_missing(value: Any) -> float:
    text = str(value or "").strip()
    if not text:
        return 1.0
    if len(text) < MIN_STRONG_CHARS:
        return 0.5
    return 0.0


def _list_missing(value: Any) -> float:
    if not value:
        return 1.0
    if isinstance(value, list):
        return 0.0 if any(str(item).strip() for item in value) else 1.0
    return _string_missing(value)


def _field(spec: dict[str, Any], *path: str) -> Any:
    current: Any = spec
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def ambiguity_items(spec: dict[str, Any]) -> list[AmbiguityItem]:
    items: list[AmbiguityItem] = [
        AmbiguityItem(
            "malkuth.human_state",
            "Who or what is the Malkuth subject, the embodied human/current actor?",
            2.0,
            _string_missing(_field(spec, "malkuth", "human_state")),
        ),
        AmbiguityItem(
            "malkuth.current_state",
            "What is concretely true in Malkuth right now?",
            3.0,
            _string_missing(_field(spec, "malkuth", "current_state")),
        ),
        AmbiguityItem(
            "kether.target_state",
            "What Kether target state should this Malkuth become?",
            3.0,
            _string_missing(_field(spec, "kether", "target_state")),
        ),
        AmbiguityItem(
            "kether.success_condition",
            "How will we know Kether has been reached?",
            3.0,
            _string_missing(_field(spec, "kether", "success_condition")),
        ),
    ]

    for profile in ASCENT_SEPHIROT:
        base = ("sephira", profile.name)
        items.extend(
            [
                AmbiguityItem(
                    f"sephira.{profile.name}.domain_instantiation",
                    f"How does {profile.name} manifest in this domain as {profile.focus_value}?",
                    1.0,
                    _string_missing(_field(spec, *base, "domain_instantiation")),
                ),
                AmbiguityItem(
                    f"sephira.{profile.name}.desired_state",
                    f"What should be true at {profile.name} for the ascent to continue?",
                    1.0,
                    _string_missing(_field(spec, *base, "desired_state")),
                ),
                AmbiguityItem(
                    f"sephira.{profile.name}.evidence",
                    f"What evidence proves {profile.name} is not just a label?",
                    0.5,
                    _list_missing(_field(spec, *base, "evidence")),
                ),
                AmbiguityItem(
                    f"sephira.{profile.name}.qliphoth_risk",
                    f"What Qliphoth distortion can corrupt {profile.name}?",
                    0.5,
                    _string_missing(_field(spec, *base, "qliphoth_risk")),
                ),
            ]
        )

    for profile in PATHS:
        base = ("paths", str(profile.number))
        items.extend(
            [
                AmbiguityItem(
                    f"paths.{profile.number}.answer",
                    f"Path {profile.number} ({profile.source}->{profile.target}): {profile.cq}",
                    1.0,
                    _string_missing(_field(spec, *base, "answer")),
                ),
                AmbiguityItem(
                    f"paths.{profile.number}.evidence",
                    f"What evidence answers path {profile.number}?",
                    0.5,
                    _list_missing(_field(spec, *base, "evidence")),
                ),
                AmbiguityItem(
                    f"paths.{profile.number}.qliphoth_check",
                    f"What negative mirror check guards path {profile.number}?",
                    0.5,
                    _string_missing(_field(spec, *base, "qliphoth_check")),
                ),
            ]
        )
    return items


def score_spec(spec: dict[str, Any]) -> float:
    items = ambiguity_items(spec)
    total_weight = sum(item.weight for item in items)
    missing_weight = sum(item.weight * item.missing for item in items)
    if not total_weight:
        return 1.0
    return round(missing_weight / total_weight, 3)


def next_questions(spec: dict[str, Any], limit: int = 8) -> list[AmbiguityItem]:
    items = [item for item in ambiguity_items(spec) if item.missing > 0]
    items.sort(key=lambda item: (item.weight * item.missing, item.weight), reverse=True)
    return items[:limit]
