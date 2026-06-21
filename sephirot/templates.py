"""Built-in domain templates for Sephirot ontology design."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from .canon import ASCENT_SEPHIROT, PATHS
from .models import Spec, blank_spec, load_json


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CORE_PACK_PATH = PACKAGE_ROOT / "template-packs" / "core.json"
CORE_REGISTRY_PATH = PACKAGE_ROOT / "template-packs" / "registry.json"


@dataclass(frozen=True)
class DomainTemplate:
    name: str
    title: str
    description: str
    context: str
    malkuth: dict[str, Any]
    kether: dict[str, Any]
    sephira: dict[str, dict[str, Any]]
    path_theme: str


def _node(domain: str, desired: str, risk: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "domain_instantiation": domain,
        "desired_state": desired,
        "qliphoth_risk": risk,
        "evidence": evidence,
    }


TEMPLATES: dict[str, DomainTemplate] = {
    "succession-agent": DomainTemplate(
        name="succession-agent",
        title="Succession Agent",
        description="Turn tacit high-performer expertise into a reproducible leadership ontology.",
        context="High-performing individual contributor becoming reproducible team capability.",
        malkuth={
            "human_state": "A high-performing individual contributor with tacit expertise and hero-dependent execution.",
            "current_state": "The organization depends on one expert's judgment, habits, and relationships to reproduce outcomes.",
            "evidence": ["expert work samples", "incident history", "handoff failures"],
        },
        kether={
            "target_state": "A successor and team system that can reproduce the original performance through explicit judgment, process, and evidence.",
            "success_condition": "The capability continues when the original expert is absent, and successors can explain, execute, and improve the work.",
            "evidence": ["successor-led delivery", "runbook usage", "quality metrics"],
        },
        sephira={
            "Malkuth": _node(
                "Observable current tasks, outputs, dependencies, and hidden expert interventions.",
                "The current reality is visible enough to separate real capability from hero dependency.",
                "Surface-level activity hides the expert interventions that actually make success happen.",
                ["task inventory", "work samples", "dependency map"],
            ),
            "Yesod": _node(
                "Operating habits, runbooks, escalation routes, and repeatable work substrate.",
                "A successor has the minimum viable foundation to execute without constant rescue.",
                "Documentation creates an illusion of readiness without live use.",
                ["runbook", "escalation policy", "practice log"],
            ),
            "Hod": _node(
                "Shared language, metrics, decision records, and review artifacts.",
                "Tacit judgment becomes explainable enough for coaching and audit.",
                "Clean documents rationalize decisions that successors still cannot make.",
                ["decision log", "rubric", "review notes"],
            ),
            "Netzach": _node(
                "Sustained practice cadence, resilience, follow-through, and feedback loops.",
                "The successor repeats the behaviors long enough for real capability to form.",
                "Persistence becomes imitation or performative effort without learning.",
                ["practice cadence", "feedback history", "retry outcomes"],
            ),
            "Tiferet": _node(
                "Integrated judgment across quality, speed, people, and context.",
                "The successor can balance tradeoffs without copying the original expert mechanically.",
                "The original expert remains the false center of every important decision.",
                ["tradeoff memo", "independent decisions", "quality review"],
            ),
            "Geburah": _node(
                "Boundaries, quality gates, exception handling, and rejection criteria.",
                "The successor can say no, escalate, and protect standards.",
                "Standards become punitive control that prevents learning.",
                ["quality gates", "escalation cases", "rejection examples"],
            ),
            "Chesed": _node(
                "Coaching, delegation, mentoring, and resource creation.",
                "The expert expands capability through people and reusable assets.",
                "Generosity creates dependency instead of autonomy.",
                ["coaching notes", "delegated work", "resource library"],
            ),
            "Binah": _node(
                "Role design, process boundaries, domain categories, and system constraints.",
                "The capability has clear structure that a successor can inhabit.",
                "Structure hides assumptions and prevents adaptation.",
                ["role charter", "process map", "constraint list"],
            ),
            "Chokmah": _node(
                "Pattern recognition, opportunity sensing, and expert intuitions made explicit.",
                "The successor can generate plausible options before formal validation.",
                "Insight becomes mystical authority that cannot be tested.",
                ["pattern catalog", "option notes", "expert commentary"],
            ),
            "Kether": _node(
                "A coherent target for succession-ready capability.",
                "The succession goal is measurable, transferable, and not split by hidden incentives.",
                "The project confuses status replacement with real capability transfer.",
                ["success rubric", "capability charter", "absence test"],
            ),
        },
        path_theme="succession capability transfer",
    ),
    "agent-runtime": DomainTemplate(
        name="agent-runtime",
        title="Agent Runtime Framework",
        description="Shape a Hermes/Ouroboros-style agent framework from ad hoc prompts into a governed ontology runtime.",
        context="Ad hoc agent prompts becoming a single ontology design framework.",
        malkuth={
            "human_state": "A developer or research team using scattered agent prompts, scripts, and implicit process memory.",
            "current_state": "Agent work happens through local convention, partial docs, and manual judgment without one canonical ontology contract.",
            "evidence": ["prompt notes", "CLI scripts", "unfinished integration docs"],
        },
        kether={
            "target_state": "A Hermes/Ouroboros-grade framework where agents share a canonical ontology contract, validation gate, templates, visualization, and export paths.",
            "success_condition": "A new agent shell can discover the profile, create a seed, validate it, plan follow-up work, build the graph, visualize it, and export it without private context.",
            "evidence": ["profile manifest", "passing validation", "agent skill", "visual graph artifact"],
        },
        sephira={
            "Malkuth": _node(
                "Current repository state, installed commands, local files, and observed agent behavior.",
                "The material tool surface is inspectable and reproducible.",
                "The framework claims maturity while only README language exists.",
                ["git status", "CLI help", "test output"],
            ),
            "Yesod": _node(
                "CLI kernel, environment contract, install scripts, and file artifact conventions.",
                "The runtime foundation lets multiple shells invoke the same kernel.",
                "Integration works only in one local setup and collapses elsewhere.",
                ["doctor report", "env template", "install script"],
            ),
            "Hod": _node(
                "Schema, validation reports, docs, command references, and explicit semantics.",
                "Agents can reason from structured contracts instead of guessing from prose.",
                "Elegant language conceals missing validators or unverifiable behavior.",
                ["profile JSON", "validation JSON", "reference docs"],
            ),
            "Netzach": _node(
                "Repeatable agent loop, refinement cadence, and persistence through incomplete specs.",
                "The framework keeps asking the highest-impact questions until the seed crystallizes.",
                "Agent momentum turns into endless interviewing without build gates.",
                ["next questions", "ambiguity trend", "agent plan"],
            ),
            "Tiferet": _node(
                "Integrated judgment across occult correspondence, ontology design, and engineering deliverables.",
                "The system preserves the mystical schema while producing usable KG artifacts.",
                "The project becomes either sterile engineering or ungrounded occult vibe.",
                ["dual graph", "README concept", "graph visualization"],
            ),
            "Geburah": _node(
                "Validation gates, test suite, schema constraints, and explicit failure behavior.",
                "Bad specs are blocked before final graph construction.",
                "Strictness becomes friction that blocks useful drafts and iteration.",
                ["unit tests", "blocked validation", "error messages"],
            ),
            "Chesed": _node(
                "Domain templates, extensibility points, editor commands, and export targets.",
                "The framework expands into new domains without losing the source schema.",
                "Expansion creates disconnected adapters and incompatible conventions.",
                ["templates list", "VS Code commands", "Neo4j export"],
            ),
            "Binah": _node(
                "Ontology boundaries, node and relationship labels, profile manifest, and versioning.",
                "The system knows what belongs in the canonical contract.",
                "The schema becomes opaque and hard to evolve.",
                ["schema version", "node labels", "relationship labels"],
            ),
            "Chokmah": _node(
                "Creative agent strategies, domain instantiation patterns, and pathwork interpretations.",
                "The framework generates domain-specific ontology designs from the same glyph.",
                "Creativity becomes arbitrary prompt magic with no validation path.",
                ["template variants", "agent recommendations", "path answers"],
            ),
            "Kether": _node(
                "The coherent product identity of Sephirot as a single ontology design framework.",
                "All surfaces point to one framework, one contract, and one ascent loop.",
                "CLI, skill, docs, and editor shell drift into separate products.",
                ["framework profile", "roadmap", "integration docs"],
            ),
        },
        path_theme="agent runtime maturation",
    ),
}


def template_names() -> list[str]:
    return sorted(TEMPLATES)


def list_templates() -> list[dict[str, str]]:
    return [
        {
            "name": item.name,
            "title": item.title,
            "description": item.description,
        }
        for item in sorted(TEMPLATES.values(), key=lambda template: template.name)
    ]


def _builtin_pack_manifest() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "pack": "sephirot-core",
        "title": "Sephirot Core Domain Templates",
        "description": "Built-in ontology design templates shipped with Sephirot.",
        "templates": [
            {
                **template,
                "source": f"builtin:{template['name']}",
            }
            for template in list_templates()
        ],
    }


def _builtin_registry_manifest() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "registry": "sephirot-core-registry",
        "title": "Sephirot Core Template Registry",
        "description": "Default registry for Sephirot template packs.",
        "packs": [
            {
                "pack": "sephirot-core",
                "title": "Sephirot Core Domain Templates",
                "description": "Built-in ontology design templates shipped with Sephirot.",
                "source": "builtin:sephirot-core",
            }
        ],
    }


def _load_json_resource(source: str | Path) -> dict[str, Any]:
    text_source = str(source)
    if text_source.startswith(("http://", "https://")):
        with urlopen(text_source, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    with Path(source).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def template_pack_manifest(path: str | Path | None = None) -> dict[str, Any]:
    pack_path = Path(path) if path else CORE_PACK_PATH
    if not pack_path.exists() and path is None:
        return _builtin_pack_manifest()
    return _load_json_resource(pack_path)


def template_registry_manifest(source: str | Path | None = None) -> dict[str, Any]:
    registry_path = Path(source) if source and not str(source).startswith(("http://", "https://")) else source
    if not registry_path and not CORE_REGISTRY_PATH.exists():
        return _builtin_registry_manifest()
    return _load_json_resource(registry_path or CORE_REGISTRY_PATH)


def list_template_packs() -> list[dict[str, Any]]:
    return [template_pack_manifest()]


def list_registry_packs(source: str | Path | None = None) -> list[dict[str, Any]]:
    return template_registry_manifest(source).get("packs", [])


def list_pack_templates(path: str | Path) -> list[dict[str, Any]]:
    return template_pack_manifest(path).get("templates", [])


def build_template_from_pack(name: str, pack_path: str | Path) -> Spec:
    manifest = template_pack_manifest(pack_path)
    pack_root = Path(pack_path).resolve().parent
    templates = {item["name"]: item for item in manifest.get("templates", [])}
    if name not in templates:
        known = ", ".join(sorted(templates))
        raise KeyError(f"Unknown template '{name}' in pack '{manifest.get('pack', pack_path)}'. Known templates: {known}")

    template = templates[name]
    source = str(template.get("source", ""))
    if source.startswith("builtin:"):
        return build_template_spec(source.removeprefix("builtin:"))
    if source.startswith("file:"):
        spec = load_json(pack_root / source.removeprefix("file:"))
        spec.setdefault(
            "template",
            {
                "name": template.get("name", name),
                "title": template.get("title", name),
                "description": template.get("description", ""),
                "pack": manifest.get("pack", ""),
            },
        )
        return spec
    raise ValueError(f"Unsupported template source for '{name}': {source}")


def build_template_spec(name: str) -> Spec:
    if name not in TEMPLATES:
        known = ", ".join(template_names())
        raise KeyError(f"Unknown template '{name}'. Known templates: {known}")

    template = TEMPLATES[name]
    spec = blank_spec(template.context)
    spec["template"] = {
        "name": template.name,
        "title": template.title,
        "description": template.description,
    }
    spec["malkuth"].update(deepcopy(template.malkuth))
    spec["kether"].update(deepcopy(template.kether))

    for profile in ASCENT_SEPHIROT:
        node = spec["sephira"][profile.name]
        node.update(deepcopy(template.sephira[profile.name]))

    for path in PATHS:
        item = spec["paths"][str(path.number)]
        item["answer"] = (
            f"For {template.path_theme}, answer this transition by turning '{path.cq}' "
            "into an owned artifact, an observable behavior, and a measurable evidence check."
        )
        item["evidence"] = [
            f"{template.path_theme} path {path.number} artifact",
            f"{template.path_theme} path {path.number} review note",
        ]
        item["qliphoth_check"] = (
            f"Reject this path if {template.path_theme} is asserted without live evidence, owner clarity, "
            "or a visible change in behavior."
        )

    return spec
