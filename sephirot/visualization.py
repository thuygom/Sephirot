"""Dependency-free graph visualization exporters."""

from __future__ import annotations

import html
import re
from typing import Any

from .canon import SEPHIROT


TREE_COORDS = {
    "Kether": (240, 64),
    "Chokmah": (370, 158),
    "Binah": (110, 158),
    "Chesed": (370, 286),
    "Geburah": (110, 286),
    "Tiferet": (240, 390),
    "Netzach": (370, 522),
    "Hod": (110, 522),
    "Yesod": (240, 650),
    "Malkuth": (240, 780),
}


def _safe_id(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_]+", "_", value)
    return text.strip("_") or "node"


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _node_label(node: dict[str, Any]) -> str:
    focus = node.get("focus_value") or node.get("failure_mode") or node.get("domain_risk") or ""
    if focus:
        return f"{node.get('id', '')}\\n{focus}"
    return str(node.get("id", ""))


def graph_to_mermaid(graph: dict[str, Any]) -> str:
    """Return a Mermaid flowchart for quick Markdown rendering."""

    lines = ["flowchart TB"]
    for node in graph.get("sephirot_tree", {}).get("nodes", []):
        node_id = _safe_id(str(node["id"]))
        lines.append(f'  {node_id}["{_esc(_node_label(node))}"]')
    for node in graph.get("qliphoth_tree", {}).get("nodes", []):
        node_id = _safe_id(str(node["id"]))
        lines.append(f'  {node_id}["{_esc(_node_label(node))}"]')
    for edge in graph.get("sephirot_tree", {}).get("edges", []):
        lines.append(f"  {_safe_id(edge['from'])} -->|{edge['path']}| {_safe_id(edge['to'])}")
    for edge in graph.get("qliphoth_tree", {}).get("edges", []):
        lines.append(f"  {_safe_id(edge['from'])} -. {edge['path']} .-> {_safe_id(edge['to'])}")
    for node in graph.get("qliphoth_tree", {}).get("nodes", []):
        mirror = node.get("mirror_of")
        if mirror:
            lines.append(f"  {_safe_id(str(node['id']))} -. mirrors .-> {_safe_id(str(mirror))}")
    return "\n".join(lines) + "\n"


def _svg_line(x1: int, y1: int, x2: int, y2: int, css_class: str) -> str:
    return f'<line class="{css_class}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'


def _svg_node(x: int, y: int, title: str, subtitle: str, css_class: str) -> str:
    title = _esc(title)
    subtitle = _esc(subtitle)
    return "\n".join(
        [
            f'<g class="node {css_class}" transform="translate({x} {y})">',
            '<circle r="43" />',
            f'<text class="title" text-anchor="middle" y="-4">{title}</text>',
            f'<text class="subtitle" text-anchor="middle" y="17">{subtitle}</text>',
            "</g>",
        ]
    )


def graph_to_svg(graph: dict[str, Any]) -> str:
    """Return an embedded SVG visualization of Sephirot and Qliphoth trees."""

    width = 960
    height = 900
    negative_offset = 480
    positive = {node["id"]: node for node in graph.get("sephirot_tree", {}).get("nodes", [])}
    negative = {node["mirror_of"]: node for node in graph.get("qliphoth_tree", {}).get("nodes", [])}
    qliphoth_coords = {name: (x + negative_offset, y) for name, (x, y) in TREE_COORDS.items()}

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Sephirot dual ontology graph</title>",
        "<desc id=\"desc\">Positive Sephirot tree mirrored by the Qliphoth risk tree.</desc>",
        "<style>",
        ".bg{fill:#f8f6f1}.axis{stroke:#888;stroke-width:1;stroke-dasharray:5 7}.edge{stroke:#333;stroke-width:2.2}.risk-edge{stroke:#111;stroke-width:2.2;stroke-dasharray:7 5}.mirror{stroke:#777;stroke-width:1.4;stroke-dasharray:3 7}.node circle{stroke:#1f1f1f;stroke-width:2}.positive circle{fill:#fffdf7}.negative circle{fill:#111}.negative text{fill:#fff}.title{font:700 14px serif}.subtitle{font:11px sans-serif}.heading{font:700 28px serif;fill:#111}.caption{font:13px sans-serif;fill:#444}",
        "</style>",
        '<rect class="bg" x="0" y="0" width="960" height="900" />',
        '<text class="heading" x="240" y="34" text-anchor="middle">Sephirot</text>',
        '<text class="heading" x="720" y="34" text-anchor="middle">Qliphoth</text>',
        _svg_line(480, 48, 480, 850, "axis"),
    ]

    for edge in graph.get("sephirot_tree", {}).get("edges", []):
        if edge["from"] in TREE_COORDS and edge["to"] in TREE_COORDS:
            x1, y1 = TREE_COORDS[edge["from"]]
            x2, y2 = TREE_COORDS[edge["to"]]
            lines.append(_svg_line(x1, y1, x2, y2, "edge"))
    for edge in graph.get("qliphoth_tree", {}).get("edges", []):
        source = positive.get(next((node for node, data in negative.items() if data["id"] == edge["from"]), ""), {})
        target = positive.get(next((node for node, data in negative.items() if data["id"] == edge["to"]), ""), {})
        source_name = source.get("id")
        target_name = target.get("id")
        if source_name in qliphoth_coords and target_name in qliphoth_coords:
            x1, y1 = qliphoth_coords[source_name]
            x2, y2 = qliphoth_coords[target_name]
            lines.append(_svg_line(x1, y1, x2, y2, "risk-edge"))
    for profile in SEPHIROT:
        if profile.name in TREE_COORDS:
            x1, y1 = TREE_COORDS[profile.name]
            x2, y2 = qliphoth_coords[profile.name]
            lines.append(_svg_line(x1 + 45, y1, x2 - 45, y2, "mirror"))

    for profile in SEPHIROT:
        node = positive.get(profile.name, {})
        x, y = TREE_COORDS[profile.name]
        lines.append(_svg_node(x, y, profile.name, str(node.get("focus_value", profile.focus_value))[:24], "positive"))

    for profile in SEPHIROT:
        node = negative.get(profile.name, {})
        x, y = qliphoth_coords[profile.name]
        title = str(node.get("id", profile.qliphoth))
        subtitle = str(node.get("failure_mode", profile.failure_mode))[:24]
        lines.append(_svg_node(x, y, title, subtitle, "negative"))

    journey = graph.get("journey", {})
    caption = (
        f"{journey.get('human_state', '')} -> {journey.get('target_state', '')}"
        if journey
        else "Malkuth -> Kether"
    )
    lines.append(f'<text class="caption" x="480" y="872" text-anchor="middle">{_esc(caption[:130])}</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def graph_to_html(graph: dict[str, Any]) -> str:
    """Return a standalone HTML visualization artifact."""

    journey = graph.get("journey", {})
    svg = graph_to_svg(graph)
    title = "Sephirot Dual Ontology Graph"
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{title}</title>",
            "<style>",
            "body{margin:0;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#f8f6f1;color:#191814}main{max-width:1120px;margin:0 auto;padding:32px 18px 42px}h1{font-family:Georgia,serif;font-size:32px;margin:0 0 8px}.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:18px 0 24px}.meta div{border:1px solid #d6d0c5;background:#fffdf8;padding:12px}.graph{overflow:auto;border:1px solid #d6d0c5;background:#f8f6f1}",
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>Sephirot Dual Ontology Graph</h1>",
            '<section class="meta">',
            f"<div><strong>Malkuth</strong><br>{_esc(journey.get('current_state', ''))}</div>",
            f"<div><strong>Kether</strong><br>{_esc(journey.get('target_state', ''))}</div>",
            f"<div><strong>Ambiguity</strong><br>{_esc(graph.get('ambiguity', ''))}</div>",
            "</section>",
            '<section class="graph">',
            svg,
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    ) + "\n"
