"""Framework manifest for Sephirot ontology design."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .canon import PATHS, SEPHIROT


def framework_manifest() -> dict[str, Any]:
    """Return the canonical Sephirot framework contract.

    This is the shared contract for the CLI, agent skills, editor shells, and
    graph exports. It keeps the occult source schema visible while making the
    ontology/KG engineering surface explicit.
    """

    return {
        "name": "Sephirot",
        "schema_version": "0.1",
        "kind": "single-ontology-design-framework",
        "tagline": "Malkuth-to-Kether ontology design through 10 value nodes and 22 CQ paths.",
        "source_schema": {
            "lineage": "Mystical Qabalah / Tree of Life / Qliphoth mirror",
            "stance": "Do not erase the occult grammar. Compile it.",
            "ascent": "Malkuth is the embodied current state; Kether is the coherent target state.",
            "duality": "Every positive value and path has a Qliphoth mirror risk.",
        },
        "engineering_contract": {
            "kernel": "python3 -m sephirot.cli",
            "seed_spec": "JSON artifact with malkuth, kether, sephira, and paths.",
            "ambiguity_gate": "Build is allowed when ambiguity <= threshold, default 0.2.",
            "dual_graph": "JSON artifact with sephirot_tree and qliphoth_tree.",
            "agent_plan": "Multi-agent refinement/build plan generated from validation state.",
            "visualization": "Dependency-free HTML, SVG, or Mermaid artifact for graph inspection.",
            "graph_export": "Neo4j Cypher, GraphML, plus ontology exchange through Turtle and JSON-LD.",
            "template_registry": "Built-in and external template pack manifests.",
        },
        "integration_surfaces": [
            {
                "surface": "cli",
                "entrypoint": "python3 -m sephirot.cli",
                "role": "Canonical kernel for framework operations.",
            },
            {
                "surface": "codex-skill",
                "entrypoint": "skills/sephirot-tree-builder/SKILL.md",
                "role": "Agent workflow wrapper for Codex-style skill execution.",
            },
            {
                "surface": "claude-code-skill",
                "entrypoint": ".claude/skills/sephirot-tree-builder/SKILL.md",
                "role": "Project-local Claude Code skill target.",
            },
            {
                "surface": "vscode-extension",
                "entrypoint": "integrations/vscode",
                "role": "Editor command shell over the CLI kernel.",
            },
            {
                "surface": "neo4j",
                "entrypoint": "python3 -m sephirot.cli export-neo4j",
                "role": "Graph database export path.",
            },
            {
                "surface": "rdf-jsonld",
                "entrypoint": "python3 -m sephirot.cli export-rdf",
                "role": "Semantic web and ontology exchange path.",
            },
            {
                "surface": "graphml",
                "entrypoint": "python3 -m sephirot.cli export-graphml",
                "role": "Generic graph tooling exchange path.",
            },
        ],
        "workflow": [
            "profile",
            "templates",
            "template-packs",
            "template-registry",
            "template",
            "new",
            "init",
            "validate",
            "plan",
            "questions",
            "build",
            "visualize",
            "export-neo4j",
            "export-rdf",
            "export-graphml",
        ],
        "node_types": [
            {
                "label": "Journey",
                "role": "Holds the Malkuth-to-Kether transformation context.",
            },
            {
                "label": "Sephira",
                "role": "Positive ontology node: focus value, desired state, and evidence.",
            },
            {
                "label": "Qliphoth",
                "role": "Negative mirror node: distortion, anti-pattern, or corrupted value.",
            },
        ],
        "relationship_types": [
            {
                "label": "SEPHIROT_PATH",
                "role": "Competency Question path between Sephira nodes.",
            },
            {
                "label": "QLIPHOTH_PATH",
                "role": "Mirror-risk path between Qliphoth nodes.",
            },
            {
                "label": "MIRRORS",
                "role": "Links a Qliphoth node to its positive Sephira source.",
            },
            {
                "label": "STARTS_AT",
                "role": "Connects a Journey to Malkuth.",
            },
            {
                "label": "TARGETS",
                "role": "Connects a Journey to Kether.",
            },
        ],
        "sephirot": [
            {
                **asdict(profile),
                "node_id": profile.name,
                "node_type": "Sephira",
            }
            for profile in SEPHIROT
        ],
        "paths": [
            {
                **asdict(profile),
                "id": f"path-{profile.number}",
                "edge_type": "CompetencyQuestionPath",
            }
            for profile in PATHS
        ],
    }
