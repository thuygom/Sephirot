"""Interactive spec-first interview loop."""

from __future__ import annotations

from typing import Any

from .ambiguity import next_questions, score_spec
from .canon import ASCENT_SEPHIROT, PATHS
from .models import Spec, blank_spec, ensure_list


def _set_path(spec: Spec, dotted_key: str, value: Any) -> None:
    keys = dotted_key.split(".")
    target: dict[str, Any] = spec
    for key in keys[:-1]:
        target = target.setdefault(key, {})
    target[keys[-1]] = value


def _prompt(prompt: str, current: Any = "") -> str:
    suffix = f" [{current}]" if current else ""
    return input(f"{prompt}{suffix}\n> ").strip()


def _prompt_list(prompt: str, current: Any = None) -> list[str]:
    current_text = "; ".join(current or []) if isinstance(current, list) else ""
    value = _prompt(f"{prompt} (semicolon-separated)", current_text)
    return ensure_list(value) if value else ensure_list(current)


def collect_full_sweep(context: str = "") -> Spec:
    """Collect as much Malkuth-to-Kether input as the user can provide."""

    spec = blank_spec(context)
    print("\nSephirot Big Bang: Malkuth -> Kether spec-first interview")
    print("Press Enter to skip anything unknown. Skipped fields keep ambiguity high.\n")

    spec["malkuth"]["human_state"] = _prompt(
        "Malkuth human/current actor: who or what is trying to become Kether?"
    )
    spec["malkuth"]["current_state"] = _prompt(
        "Malkuth current state: what is concretely true right now?"
    )
    spec["malkuth"]["evidence"] = _prompt_list(
        "Malkuth evidence: what proves the current state?"
    )
    spec["kether"]["target_state"] = _prompt(
        "Kether target state: what should Malkuth become?"
    )
    spec["kether"]["success_condition"] = _prompt(
        "Kether success condition: how will we know it has been reached?"
    )
    spec["kether"]["evidence"] = _prompt_list(
        "Kether evidence: what would prove the target state?"
    )

    print("\n10 Sephira sweep, in ascent order from Malkuth to Kether.\n")
    for profile in ASCENT_SEPHIROT:
        node = spec["sephira"][profile.name]
        print(f"[{profile.name}] {profile.focus_value}")
        node["domain_instantiation"] = _prompt(
            f"How does {profile.name} manifest in this domain?"
        )
        node["desired_state"] = _prompt(
            f"What should be true at {profile.name}?"
        )
        node["evidence"] = _prompt_list(
            f"What evidence proves {profile.name} is real?"
        )
        node["qliphoth_risk"] = _prompt(
            f"What Qliphoth distortion can corrupt {profile.name}?"
        )
        print("")

    print("\n22 Path/CQ sweep. Each path must become answerable by the KG.\n")
    for path in PATHS:
        item = spec["paths"][str(path.number)]
        print(f"[Path {path.number}] {path.source} -> {path.target}")
        print(f"CQ: {path.cq}")
        item["answer"] = _prompt("Answer")
        item["evidence"] = _prompt_list("Evidence")
        item["qliphoth_check"] = _prompt("Qliphoth mirror/risk check")
        print("")
    return spec


def refine_until_threshold(
    spec: Spec,
    *,
    threshold: float = 0.2,
    max_rounds: int = 32,
    questions_per_round: int = 4,
) -> Spec:
    """Ask follow-up questions until ambiguity is below the threshold."""

    for round_index in range(1, max_rounds + 1):
        ambiguity = score_spec(spec)
        print(f"Ambiguity: {ambiguity:.3f} (target <= {threshold:.3f})")
        if ambiguity <= threshold:
            print("Spec crystallized. Tree construction is now allowed.")
            return spec

        questions = next_questions(spec, limit=questions_per_round)
        if not questions:
            return spec
        print(f"\nRefinement round {round_index}:")
        for item in questions:
            value = _prompt(item.question)
            if not value:
                continue
            if item.key.endswith(".evidence"):
                _set_path(spec, item.key, ensure_list(value))
            else:
                _set_path(spec, item.key, value)
        print("")
    return spec
