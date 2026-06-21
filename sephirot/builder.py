"""Build Sephirot and Qliphoth trees from a seed spec."""

from __future__ import annotations

from typing import Any

from .ambiguity import score_spec
from .canon import PATHS, SEPHIROT_BY_NAME, SEPHIROT


def _path_value(spec: dict[str, Any], *path: str, default: Any = "") -> Any:
    current: Any = spec
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def build_dual_tree(
    spec: dict[str, Any],
    *,
    threshold: float = 0.2,
    allow_ambiguous: bool = False,
) -> dict[str, Any]:
    """Build positive and negative KG structures from a seed spec."""

    ambiguity = score_spec(spec)
    if ambiguity > threshold and not allow_ambiguous:
        raise ValueError(
            f"Spec ambiguity {ambiguity} is above threshold {threshold}. "
            "Continue the interview or pass allow_ambiguous=True."
        )

    positive_nodes = []
    negative_nodes = []
    for profile in SEPHIROT:
        data = _path_value(spec, "sephira", profile.name, default={}) or {}
        positive_nodes.append(
            {
                "id": profile.name,
                "number": profile.number,
                "ascent_order": profile.ascent_order,
                "type": "Sephira",
                "focus_value": profile.focus_value,
                "kg_role": profile.kg_role,
                "domain_instantiation": data.get("domain_instantiation", ""),
                "desired_state": data.get("desired_state", ""),
                "evidence": data.get("evidence", []),
            }
        )
        negative_nodes.append(
            {
                "id": profile.qliphoth,
                "mirror_of": profile.name,
                "type": "Qliphoth",
                "failure_mode": profile.failure_mode,
                "domain_risk": data.get("qliphoth_risk", ""),
            }
        )

    positive_edges = []
    negative_edges = []
    for path in PATHS:
        data = _path_value(spec, "paths", str(path.number), default={}) or {}
        source_profile = SEPHIROT_BY_NAME[path.source]
        target_profile = SEPHIROT_BY_NAME[path.target]
        positive_edges.append(
            {
                "id": f"path-{path.number}",
                "path": path.number,
                "from": path.source,
                "to": path.target,
                "type": "CompetencyQuestionPath",
                "cq": path.cq,
                "answer": data.get("answer", ""),
                "evidence": data.get("evidence", []),
                "symbolic_profile": {
                    "tree": "Sephirot",
                    "movement": "ascent",
                    "correspondence_layer": list(path.correspondence_layer),
                },
            }
        )
        negative_edges.append(
            {
                "id": f"qliphoth-path-{path.number}",
                "path": path.number,
                "from": source_profile.qliphoth,
                "to": target_profile.qliphoth,
                "mirror_of": f"path-{path.number}",
                "type": "QliphothRiskPath",
                "risk_check": data.get("qliphoth_check", ""),
                "symbolic_profile": {
                    "tree": "Qliphoth",
                    "movement": "descent_or_corruption",
                    "correspondence_layer": list(path.correspondence_layer),
                },
            }
        )

    return {
        "schema_version": "0.1",
        "source": "sephirot.spec",
        "ambiguity": ambiguity,
        "threshold": threshold,
        "journey": {
            "from": "Malkuth",
            "to": "Kether",
            "human_state": _path_value(spec, "malkuth", "human_state"),
            "current_state": _path_value(spec, "malkuth", "current_state"),
            "target_state": _path_value(spec, "kether", "target_state"),
            "success_condition": _path_value(spec, "kether", "success_condition"),
        },
        "sephirot_tree": {
            "polarity": "positive",
            "nodes": positive_nodes,
            "edges": positive_edges,
        },
        "qliphoth_tree": {
            "polarity": "negative",
            "nodes": negative_nodes,
            "edges": negative_edges,
        },
    }
