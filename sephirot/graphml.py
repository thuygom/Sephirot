"""GraphML exporter for generic graph tooling."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any


GRAPHML_NS = "http://graphml.graphdrawing.org/xmlns"


def _text(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _key(parent: ET.Element, key_id: str, name: str, target: str = "all") -> None:
    ET.SubElement(
        parent,
        "key",
        {
            "id": key_id,
            "for": target,
            "attr.name": name,
            "attr.type": "string",
        },
    )


def _data(parent: ET.Element, key: str, value: Any) -> None:
    element = ET.SubElement(parent, "data", {"key": key})
    element.text = _text(value)


def _node(parent: ET.Element, node_id: str, properties: dict[str, Any]) -> None:
    element = ET.SubElement(parent, "node", {"id": node_id})
    for key, value in properties.items():
        _data(element, key, value)


def _edge(parent: ET.Element, edge_id: str, source: str, target: str, properties: dict[str, Any]) -> None:
    element = ET.SubElement(parent, "edge", {"id": edge_id, "source": source, "target": target, "directed": "true"})
    for key, value in properties.items():
        _data(element, key, value)


def graph_to_graphml(graph: dict[str, Any]) -> str:
    """Return GraphML for Sephirot/Qliphoth graph exchange."""

    ET.register_namespace("", GRAPHML_NS)
    root = ET.Element("graphml", {"xmlns": GRAPHML_NS})
    for key in (
        "label",
        "type",
        "focus_value",
        "kg_role",
        "domain_instantiation",
        "desired_state",
        "evidence",
        "failure_mode",
        "domain_risk",
        "mirror_of",
        "path",
        "cq",
        "answer",
        "risk_check",
        "correspondence_layer",
    ):
        _key(root, key, key)

    graph_el = ET.SubElement(root, "graph", {"id": "sephirot-dual-graph", "edgedefault": "directed"})
    _node(
        graph_el,
        "journey-malkuth-to-kether",
        {
            "label": "Malkuth to Kether Journey",
            "type": "Journey",
            "domain_instantiation": graph.get("journey", {}).get("current_state", ""),
            "desired_state": graph.get("journey", {}).get("target_state", ""),
        },
    )

    sephira_ids = set()
    qliphoth_ids = set()
    for node in graph.get("sephirot_tree", {}).get("nodes", []):
        node_id = str(node["id"])
        sephira_ids.add(node_id)
        _node(
            graph_el,
            node_id,
            {
                "label": node_id,
                "type": "Sephira",
                "focus_value": node.get("focus_value", ""),
                "kg_role": node.get("kg_role", ""),
                "domain_instantiation": node.get("domain_instantiation", ""),
                "desired_state": node.get("desired_state", ""),
                "evidence": node.get("evidence", []),
            },
        )

    for node in graph.get("qliphoth_tree", {}).get("nodes", []):
        node_id = "qliphoth-" + str(node["id"])
        qliphoth_ids.add(node_id)
        _node(
            graph_el,
            node_id,
            {
                "label": node.get("id", ""),
                "type": "Qliphoth",
                "failure_mode": node.get("failure_mode", ""),
                "domain_risk": node.get("domain_risk", ""),
                "mirror_of": node.get("mirror_of", ""),
            },
        )
        mirror = node.get("mirror_of")
        if mirror in sephira_ids:
            _edge(
                graph_el,
                f"mirror-{node_id}",
                node_id,
                str(mirror),
                {"label": "MIRRORS", "type": "MIRRORS"},
            )

    _edge(
        graph_el,
        "journey-starts-at",
        "journey-malkuth-to-kether",
        "Malkuth",
        {"label": "STARTS_AT", "type": "STARTS_AT"},
    )
    _edge(
        graph_el,
        "journey-targets",
        "journey-malkuth-to-kether",
        "Kether",
        {"label": "TARGETS", "type": "TARGETS"},
    )

    for edge in graph.get("sephirot_tree", {}).get("edges", []):
        _edge(
            graph_el,
            str(edge["id"]),
            str(edge["from"]),
            str(edge["to"]),
            {
                "label": "SEPHIROT_PATH",
                "type": "CompetencyQuestionPath",
                "path": edge.get("path", ""),
                "cq": edge.get("cq", ""),
                "answer": edge.get("answer", ""),
                "evidence": edge.get("evidence", []),
                "correspondence_layer": edge.get("symbolic_profile", {}).get("correspondence_layer", []),
            },
        )

    for edge in graph.get("qliphoth_tree", {}).get("edges", []):
        source = "qliphoth-" + str(edge["from"])
        target = "qliphoth-" + str(edge["to"])
        if source not in qliphoth_ids or target not in qliphoth_ids:
            continue
        _edge(
            graph_el,
            str(edge["id"]),
            source,
            target,
            {
                "label": "QLIPHOTH_PATH",
                "type": "QliphothRiskPath",
                "path": edge.get("path", ""),
                "risk_check": edge.get("risk_check", ""),
                "mirror_of": edge.get("mirror_of", ""),
                "correspondence_layer": edge.get("symbolic_profile", {}).get("correspondence_layer", []),
            },
        )

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"
