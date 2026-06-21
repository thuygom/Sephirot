"""Neo4j/Cypher export for Sephirot dual graphs."""

from __future__ import annotations

import json
import re
from typing import Any


def _cypher_string(value: Any) -> str:
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def _cypher_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_cypher_string(item) for item in value) + "]"
    if value is None:
        return "null"
    return _cypher_string(value)


def _prop_map(properties: dict[str, Any]) -> str:
    parts = []
    for key, value in properties.items():
        if value is None:
            continue
        safe_key = re.sub(r"[^A-Za-z0-9_]", "_", key)
        parts.append(f"{safe_key}: {_cypher_value(value)}")
    return "{ " + ", ".join(parts) + " }"


def _set_props(alias: str, properties: dict[str, Any]) -> str:
    assignments = []
    for key, value in properties.items():
        safe_key = re.sub(r"[^A-Za-z0-9_]", "_", key)
        assignments.append(f"{alias}.{safe_key} = {_cypher_value(value)}")
    return "SET " + ", ".join(assignments)


def graph_to_cypher(graph: dict[str, Any]) -> str:
    """Return Cypher statements compatible with Neo4j."""

    lines = [
        "// Sephirot dual knowledge graph export",
        "CREATE CONSTRAINT sephira_id IF NOT EXISTS FOR (n:Sephira) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT qliphoth_id IF NOT EXISTS FOR (n:Qliphoth) REQUIRE n.id IS UNIQUE;",
        "CREATE CONSTRAINT journey_id IF NOT EXISTS FOR (n:Journey) REQUIRE n.id IS UNIQUE;",
        "",
    ]

    journey = graph.get("journey", {})
    journey_props = {
        "id": "malkuth-to-kether",
        "from": journey.get("from", "Malkuth"),
        "to": journey.get("to", "Kether"),
        "human_state": journey.get("human_state", ""),
        "current_state": journey.get("current_state", ""),
        "target_state": journey.get("target_state", ""),
        "success_condition": journey.get("success_condition", ""),
        "ambiguity": graph.get("ambiguity"),
    }
    lines.append(f"MERGE (j:Journey {{ id: {_cypher_string(journey_props['id'])} }})")
    lines.append(_set_props("j", journey_props) + ";")
    lines.append("")

    for node in graph.get("sephirot_tree", {}).get("nodes", []):
        props = dict(node)
        node_id = props.pop("id")
        lines.append(f"MERGE (n:Sephira {{ id: {_cypher_string(node_id)} }})")
        lines.append(_set_props("n", {"id": node_id, **props}) + ";")

    for node in graph.get("qliphoth_tree", {}).get("nodes", []):
        props = dict(node)
        node_id = props.pop("id")
        mirror_of = props.get("mirror_of")
        lines.append(f"MERGE (q:Qliphoth {{ id: {_cypher_string(node_id)} }})")
        lines.append(_set_props("q", {"id": node_id, **props}) + ";")
        if mirror_of:
            lines.append(
                f"MATCH (q:Qliphoth {{ id: {_cypher_string(node_id)} }}), "
                f"(s:Sephira {{ id: {_cypher_string(mirror_of)} }}) "
                "MERGE (q)-[:MIRRORS]->(s);"
            )

    lines.append("")
    lines.append(
        "MATCH (j:Journey { id: \"malkuth-to-kether\" }), (m:Sephira { id: \"Malkuth\" }) "
        "MERGE (j)-[:STARTS_AT]->(m);"
    )
    lines.append(
        "MATCH (j:Journey { id: \"malkuth-to-kether\" }), (k:Sephira { id: \"Kether\" }) "
        "MERGE (j)-[:TARGETS]->(k);"
    )

    for edge in graph.get("sephirot_tree", {}).get("edges", []):
        props = dict(edge)
        rel_id = props.pop("id")
        source = props.pop("from")
        target = props.pop("to")
        props["correspondence_layer"] = props.get("symbolic_profile", {}).get("correspondence_layer", [])
        props.pop("symbolic_profile", None)
        lines.append(
            f"MATCH (a:Sephira {{ id: {_cypher_string(source)} }}), "
            f"(b:Sephira {{ id: {_cypher_string(target)} }}) "
            f"MERGE (a)-[r:SEPHIROT_PATH {{ id: {_cypher_string(rel_id)} }}]->(b) "
            f"{_set_props('r', {'id': rel_id, **props})};"
        )

    for edge in graph.get("qliphoth_tree", {}).get("edges", []):
        props = dict(edge)
        rel_id = props.pop("id")
        source = props.pop("from")
        target = props.pop("to")
        props["correspondence_layer"] = props.get("symbolic_profile", {}).get("correspondence_layer", [])
        props.pop("symbolic_profile", None)
        lines.append(
            f"MATCH (a:Qliphoth {{ id: {_cypher_string(source)} }}), "
            f"(b:Qliphoth {{ id: {_cypher_string(target)} }}) "
            f"MERGE (a)-[r:QLIPHOTH_PATH {{ id: {_cypher_string(rel_id)} }}]->(b) "
            f"{_set_props('r', {'id': rel_id, **props})};"
        )

    return "\n".join(lines) + "\n"
