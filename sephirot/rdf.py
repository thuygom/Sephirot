"""RDF/Turtle and JSON-LD exporters for Sephirot graphs."""

from __future__ import annotations

import json
import re
from typing import Any


BASE_IRI = "https://sephirot.dev/ontology#"


def _slug(value: Any) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", str(value or "").strip())
    return text.strip("-") or "resource"


def _iri(value: Any) -> str:
    return "seph:" + _slug(value)


def _literal(value: Any) -> str:
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def _number(value: Any) -> str:
    return str(value) if isinstance(value, int | float) else _literal(value)


def _predicate_values(predicate: str, values: list[Any]) -> list[str]:
    return [f"  {predicate} {_literal(value)}" for value in values if str(value).strip()]


def _resource(subject: str, properties: list[str]) -> str:
    if not properties:
        return subject + " ."
    return subject + "\n" + " ;\n".join(properties) + " ."


def graph_to_turtle(graph: dict[str, Any]) -> str:
    """Return a Turtle representation of a Sephirot dual graph."""

    lines = [
        "@prefix seph: <https://sephirot.dev/ontology#> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
    ]

    journey = graph.get("journey", {})
    lines.append(
        _resource(
            "seph:journey-malkuth-to-kether",
            [
                "  rdf:type seph:Journey",
                "  rdfs:label \"Malkuth to Kether Journey\"",
                "  seph:startsAt seph:Malkuth",
                "  seph:targets seph:Kether",
                f"  seph:humanState {_literal(journey.get('human_state', ''))}",
                f"  seph:currentState {_literal(journey.get('current_state', ''))}",
                f"  seph:targetState {_literal(journey.get('target_state', ''))}",
                f"  seph:successCondition {_literal(journey.get('success_condition', ''))}",
                f"  seph:ambiguity {_number(graph.get('ambiguity', 1.0))}",
            ],
        )
    )
    lines.append("")

    for node in graph.get("sephirot_tree", {}).get("nodes", []):
        subject = _iri(node.get("id"))
        props = [
            "  rdf:type seph:Sephira",
            f"  rdfs:label {_literal(node.get('id', ''))}",
            f"  seph:number {_number(node.get('number'))}",
            f"  seph:ascentOrder {_number(node.get('ascent_order'))}",
            f"  seph:focusValue {_literal(node.get('focus_value', ''))}",
            f"  seph:kgRole {_literal(node.get('kg_role', ''))}",
            f"  seph:domainInstantiation {_literal(node.get('domain_instantiation', ''))}",
            f"  seph:desiredState {_literal(node.get('desired_state', ''))}",
        ]
        props.extend(_predicate_values("seph:evidence", node.get("evidence", [])))
        lines.append(_resource(subject, props))

    lines.append("")
    for node in graph.get("qliphoth_tree", {}).get("nodes", []):
        subject = _iri("qliphoth-" + str(node.get("id", "")))
        mirror = _iri(node.get("mirror_of"))
        lines.append(
            _resource(
                subject,
                [
                    "  rdf:type seph:Qliphoth",
                    f"  rdfs:label {_literal(node.get('id', ''))}",
                    f"  seph:mirrorOf {mirror}",
                    f"  seph:failureMode {_literal(node.get('failure_mode', ''))}",
                    f"  seph:domainRisk {_literal(node.get('domain_risk', ''))}",
                ],
            )
        )

    lines.append("")
    for edge in graph.get("sephirot_tree", {}).get("edges", []):
        subject = _iri(edge.get("id"))
        props = [
            "  rdf:type seph:CompetencyQuestionPath",
            f"  seph:pathNumber {_number(edge.get('path'))}",
            f"  seph:source {_iri(edge.get('from'))}",
            f"  seph:target {_iri(edge.get('to'))}",
            f"  seph:competencyQuestion {_literal(edge.get('cq', ''))}",
            f"  seph:answer {_literal(edge.get('answer', ''))}",
        ]
        props.extend(_predicate_values("seph:evidence", edge.get("evidence", [])))
        props.extend(
            _predicate_values(
                "seph:correspondenceLayer",
                edge.get("symbolic_profile", {}).get("correspondence_layer", []),
            )
        )
        lines.append(_resource(subject, props))

    lines.append("")
    for edge in graph.get("qliphoth_tree", {}).get("edges", []):
        subject = _iri(edge.get("id"))
        props = [
            "  rdf:type seph:QliphothRiskPath",
            f"  seph:pathNumber {_number(edge.get('path'))}",
            f"  seph:source {_iri('qliphoth-' + str(edge.get('from', '')))}",
            f"  seph:target {_iri('qliphoth-' + str(edge.get('to', '')))}",
            f"  seph:mirrorOf {_iri(edge.get('mirror_of'))}",
            f"  seph:riskCheck {_literal(edge.get('risk_check', ''))}",
        ]
        props.extend(
            _predicate_values(
                "seph:correspondenceLayer",
                edge.get("symbolic_profile", {}).get("correspondence_layer", []),
            )
        )
        lines.append(_resource(subject, props))

    return "\n".join(lines) + "\n"


def _jsonld_node(node: dict[str, Any]) -> dict[str, Any]:
    return {
        "@id": _iri(node.get("id")),
        "@type": "Sephira",
        "label": node.get("id", ""),
        "number": node.get("number"),
        "ascentOrder": node.get("ascent_order"),
        "focusValue": node.get("focus_value", ""),
        "kgRole": node.get("kg_role", ""),
        "domainInstantiation": node.get("domain_instantiation", ""),
        "desiredState": node.get("desired_state", ""),
        "evidence": node.get("evidence", []),
    }


def graph_to_jsonld(graph: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-LD representation of a Sephirot dual graph."""

    journey = graph.get("journey", {})
    items: list[dict[str, Any]] = [
        {
            "@id": "seph:journey-malkuth-to-kether",
            "@type": "Journey",
            "label": "Malkuth to Kether Journey",
            "startsAt": {"@id": "seph:Malkuth"},
            "targets": {"@id": "seph:Kether"},
            "humanState": journey.get("human_state", ""),
            "currentState": journey.get("current_state", ""),
            "targetState": journey.get("target_state", ""),
            "successCondition": journey.get("success_condition", ""),
            "ambiguity": graph.get("ambiguity"),
        }
    ]
    items.extend(_jsonld_node(node) for node in graph.get("sephirot_tree", {}).get("nodes", []))
    for node in graph.get("qliphoth_tree", {}).get("nodes", []):
        items.append(
            {
                "@id": _iri("qliphoth-" + str(node.get("id", ""))),
                "@type": "Qliphoth",
                "label": node.get("id", ""),
                "mirrorOf": {"@id": _iri(node.get("mirror_of"))},
                "failureMode": node.get("failure_mode", ""),
                "domainRisk": node.get("domain_risk", ""),
            }
        )
    for edge in graph.get("sephirot_tree", {}).get("edges", []):
        items.append(
            {
                "@id": _iri(edge.get("id")),
                "@type": "CompetencyQuestionPath",
                "pathNumber": edge.get("path"),
                "source": {"@id": _iri(edge.get("from"))},
                "target": {"@id": _iri(edge.get("to"))},
                "competencyQuestion": edge.get("cq", ""),
                "answer": edge.get("answer", ""),
                "evidence": edge.get("evidence", []),
                "correspondenceLayer": edge.get("symbolic_profile", {}).get("correspondence_layer", []),
            }
        )
    for edge in graph.get("qliphoth_tree", {}).get("edges", []):
        items.append(
            {
                "@id": _iri(edge.get("id")),
                "@type": "QliphothRiskPath",
                "pathNumber": edge.get("path"),
                "source": {"@id": _iri("qliphoth-" + str(edge.get("from", "")))},
                "target": {"@id": _iri("qliphoth-" + str(edge.get("to", "")))},
                "mirrorOf": {"@id": _iri(edge.get("mirror_of"))},
                "riskCheck": edge.get("risk_check", ""),
                "correspondenceLayer": edge.get("symbolic_profile", {}).get("correspondence_layer", []),
            }
        )

    return {
        "@context": {
            "seph": BASE_IRI,
            "label": "http://www.w3.org/2000/01/rdf-schema#label",
            "Journey": "seph:Journey",
            "Sephira": "seph:Sephira",
            "Qliphoth": "seph:Qliphoth",
            "CompetencyQuestionPath": "seph:CompetencyQuestionPath",
            "QliphothRiskPath": "seph:QliphothRiskPath",
            "startsAt": {"@id": "seph:startsAt", "@type": "@id"},
            "targets": {"@id": "seph:targets", "@type": "@id"},
            "source": {"@id": "seph:source", "@type": "@id"},
            "target": {"@id": "seph:target", "@type": "@id"},
            "mirrorOf": {"@id": "seph:mirrorOf", "@type": "@id"},
        },
        "@graph": items,
    }
