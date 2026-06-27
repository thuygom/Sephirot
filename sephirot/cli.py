"""Command-line interface for Sephirot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ambiguity import next_questions, score_spec
from .builder import build_dual_tree
from .doctor import checks_as_dict, collect_checks
from .graphml import graph_to_graphml
from .interview import collect_full_sweep, refine_until_threshold
from .medicalaos import compile_medicalaos_ontology, dump_medicalaos_ontology
from .models import blank_spec, dump_json, load_json
from .neo4j import graph_to_cypher
from .planner import agent_plan, plan_as_markdown
from .profile import framework_manifest
from .rdf import graph_to_jsonld, graph_to_turtle
from .templates import (
    build_template_from_pack,
    build_template_spec,
    list_pack_templates,
    list_registry_packs,
    list_template_packs,
    list_templates,
    template_pack_manifest,
    template_registry_manifest,
)
from .validation import report_as_dict, validate_spec
from .visualization import graph_to_html, graph_to_mermaid, graph_to_svg


def cmd_new(args: argparse.Namespace) -> int:
    spec = blank_spec(args.context or "")
    dump_json(spec, args.out)
    print(f"Wrote blank seed spec: {args.out}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    spec = collect_full_sweep(args.context or "")
    spec = refine_until_threshold(
        spec,
        threshold=args.threshold,
        max_rounds=args.max_rounds,
        questions_per_round=args.questions_per_round,
    )
    spec["threshold"] = args.threshold
    spec["ambiguity"] = score_spec(spec)
    dump_json(spec, args.out)
    print(f"Wrote seed spec: {args.out}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    spec = load_json(args.input)
    ambiguity = score_spec(spec)
    print(f"{ambiguity:.3f}")
    return 0


def cmd_questions(args: argparse.Namespace) -> int:
    spec = load_json(args.input)
    for item in next_questions(spec, limit=args.limit):
        print(f"{item.key} [{item.weight:g}]: {item.question}")
    return 0


def cmd_profile(args: argparse.Namespace) -> int:
    manifest = framework_manifest()
    if args.out:
        dump_json(manifest, args.out)
        print(f"Wrote Sephirot framework profile: {args.out}")
    else:
        print(dump_json(manifest))
    return 0


def cmd_templates(args: argparse.Namespace) -> int:
    templates = list_pack_templates(args.pack) if args.pack else list_templates()
    if args.json:
        print(json.dumps(templates, ensure_ascii=False, indent=2))
    else:
        for template in templates:
            print(f"{template['name']}: {template['title']} - {template['description']}")
    return 0


def cmd_template_packs(args: argparse.Namespace) -> int:
    packs = [template_pack_manifest(args.path)] if args.path else list_template_packs()
    if args.json:
        print(json.dumps(packs, ensure_ascii=False, indent=2))
    else:
        for pack in packs:
            print(f"{pack['pack']}: {pack['title']} - {pack['description']}")
            for template in pack.get("templates", []):
                print(f"  - {template['name']}: {template['title']}")
    return 0


def cmd_template_registry(args: argparse.Namespace) -> int:
    registry = template_registry_manifest(args.source or None)
    if args.json:
        print(json.dumps(registry, ensure_ascii=False, indent=2))
    else:
        print(f"{registry['registry']}: {registry['title']} - {registry['description']}")
        for pack in list_registry_packs(args.source or None):
            print(f"  - {pack['pack']}: {pack['title']} ({pack['source']})")
    return 0


def cmd_template(args: argparse.Namespace) -> int:
    try:
        spec = build_template_from_pack(args.name, args.pack) if args.pack else build_template_spec(args.name)
    except KeyError as exc:
        print(str(exc).strip("'"), file=sys.stderr)
        return 2
    if args.context:
        spec["context"] = args.context
    dump_json(spec, args.out)
    print(f"Wrote {args.name} template seed spec: {args.out}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    spec = load_json(args.input)
    report = validate_spec(spec)
    if args.json:
        print(json.dumps(report_as_dict(report), ensure_ascii=False, indent=2))
    else:
        marker = "OK" if report.ok else "BLOCKED"
        print(f"{marker} ambiguity={report.ambiguity:.3f} threshold={report.threshold:.3f}")
        for issue in report.errors:
            print(f"ERROR {issue.key}: {issue.message}")
        for issue in report.warnings:
            print(f"WARN {issue.key}: {issue.message}")
        if report.next_questions:
            print("Next questions:")
            for item in report.next_questions:
                print(f"- {item['key']}: {item['question']}")
    return 0 if report.ok or args.allow_incomplete else 2


def cmd_plan(args: argparse.Namespace) -> int:
    spec = load_json(args.input)
    plan = agent_plan(spec)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(plan_as_markdown(plan), end="")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    spec = load_json(args.input)
    threshold = args.threshold if args.threshold is not None else float(spec.get("threshold", 0.2))
    try:
        graph = build_dual_tree(
            spec,
            threshold=threshold,
            allow_ambiguous=args.allow_ambiguous,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    dump_json(graph, args.out)
    print(f"Wrote dual tree graph: {args.out}")
    return 0


def _graph_from_input(args: argparse.Namespace) -> dict[str, object]:
    data = load_json(args.input)
    if "sephirot_tree" in data and "qliphoth_tree" in data:
        return data
    threshold = args.threshold if args.threshold is not None else float(data.get("threshold", 0.2))
    return build_dual_tree(
        data,
        threshold=threshold,
        allow_ambiguous=args.allow_ambiguous,
    )


def cmd_visualize(args: argparse.Namespace) -> int:
    try:
        graph = _graph_from_input(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.format == "html":
        output = graph_to_html(graph)
    elif args.format == "svg":
        output = graph_to_svg(graph)
    else:
        output = graph_to_mermaid(graph)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote {args.format} visualization: {args.out}")
    else:
        print(output)
    return 0


def cmd_export_neo4j(args: argparse.Namespace) -> int:
    data = load_json(args.input)
    if "sephirot_tree" in data and "qliphoth_tree" in data:
        graph = data
    else:
        threshold = args.threshold if args.threshold is not None else float(data.get("threshold", 0.2))
        try:
            graph = build_dual_tree(
                data,
                threshold=threshold,
                allow_ambiguous=args.allow_ambiguous,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    cypher = graph_to_cypher(graph)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(cypher)
        print(f"Wrote Neo4j Cypher: {args.out}")
    else:
        print(cypher)
    return 0


def cmd_export_rdf(args: argparse.Namespace) -> int:
    try:
        graph = _graph_from_input(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.format == "jsonld":
        output = json.dumps(graph_to_jsonld(graph), ensure_ascii=False, indent=2) + "\n"
    else:
        output = graph_to_turtle(graph)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote {args.format} ontology export: {args.out}")
    else:
        print(output)
    return 0


def cmd_export_graphml(args: argparse.Namespace) -> int:
    try:
        graph = _graph_from_input(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    output = graph_to_graphml(graph)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote GraphML export: {args.out}")
    else:
        print(output)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    if args.json:
        print(json.dumps(checks_as_dict(), ensure_ascii=False, indent=2))
        return 0
    for check in collect_checks():
        marker = "OK" if check.ok else "--"
        print(f"{marker} {check.name}: {check.detail}")
    return 0


def cmd_compile_medicalaos(args: argparse.Namespace) -> int:
    ontology = compile_medicalaos_ontology(
        cekg_paths=args.cekg,
        aipatient_paths=args.aipatient,
        mode=args.mode,
        threshold=args.threshold,
    )
    dump_medicalaos_ontology(ontology, args.out)
    print(f"Wrote Sephirot(medical) executable ontology: {args.out}")
    return 0 if ontology.get("validation", {}).get("ok") else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sephirot",
        description="Spec-first Sephirot/Qliphoth knowledge graph builder.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_parser = subparsers.add_parser(
        "profile",
        help="Print the canonical Sephirot ontology framework manifest.",
    )
    profile_parser.add_argument("--out", default="", help="Output profile JSON path. Prints to stdout if omitted.")
    profile_parser.set_defaults(func=cmd_profile)

    templates_parser = subparsers.add_parser(
        "templates",
        help="List built-in domain ontology templates.",
    )
    templates_parser.add_argument("--json", action="store_true", help="Print templates as JSON.")
    templates_parser.add_argument("--pack", default="", help="Optional template pack manifest path.")
    templates_parser.set_defaults(func=cmd_templates)

    template_packs_parser = subparsers.add_parser(
        "template-packs",
        help="List available template pack manifests.",
    )
    template_packs_parser.add_argument("--json", action="store_true", help="Print template packs as JSON.")
    template_packs_parser.add_argument("--path", default="", help="Optional external template pack manifest path.")
    template_packs_parser.set_defaults(func=cmd_template_packs)

    template_registry_parser = subparsers.add_parser(
        "template-registry",
        help="List template packs from a local or remote registry manifest.",
    )
    template_registry_parser.add_argument("--source", default="", help="Optional registry JSON path or URL.")
    template_registry_parser.add_argument("--json", action="store_true", help="Print registry as JSON.")
    template_registry_parser.set_defaults(func=cmd_template_registry)

    template_parser = subparsers.add_parser(
        "template",
        help="Write a seed spec from a built-in domain ontology template.",
    )
    template_parser.add_argument("--name", required=True, help="Template name, e.g. succession-agent.")
    template_parser.add_argument("--pack", default="", help="Optional template pack manifest path.")
    template_parser.add_argument("--context", default="", help="Optional context override.")
    template_parser.add_argument("--out", default="sephirot.seed.json", help="Output seed spec path.")
    template_parser.set_defaults(func=cmd_template)

    new_parser = subparsers.add_parser("new", help="Write a blank seed spec.")
    new_parser.add_argument("--context", default="", help="Initial vague idea or goal context.")
    new_parser.add_argument("--out", default="sephirot.seed.json", help="Output seed spec path.")
    new_parser.set_defaults(func=cmd_new)

    init_parser = subparsers.add_parser(
        "init",
        help="Run the Malkuth-to-Kether full sweep and ambiguity refinement loop.",
    )
    init_parser.add_argument("context", nargs="?", default="", help="Initial vague idea or goal context.")
    init_parser.add_argument("--out", default="sephirot.seed.json", help="Output seed spec path.")
    init_parser.add_argument("--threshold", type=float, default=0.2, help="Maximum allowed ambiguity.")
    init_parser.add_argument("--max-rounds", type=int, default=32, help="Maximum refinement rounds.")
    init_parser.add_argument("--questions-per-round", type=int, default=4, help="Follow-up questions per round.")
    init_parser.set_defaults(func=cmd_init)

    score_parser = subparsers.add_parser("score", help="Print ambiguity score for a seed spec.")
    score_parser.add_argument("--input", required=True, help="Input seed spec path.")
    score_parser.set_defaults(func=cmd_score)

    questions_parser = subparsers.add_parser(
        "questions",
        help="Print the next highest-impact questions for reducing ambiguity.",
    )
    questions_parser.add_argument("--input", required=True, help="Input seed spec path.")
    questions_parser.add_argument("--limit", type=int, default=8, help="Number of questions to print.")
    questions_parser.set_defaults(func=cmd_questions)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a seed spec against the canonical Sephirot framework contract.",
    )
    validate_parser.add_argument("--input", required=True, help="Input seed spec path.")
    validate_parser.add_argument("--json", action="store_true", help="Print validation report as JSON.")
    validate_parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Return success even when the report is blocked by ambiguity or errors.",
    )
    validate_parser.set_defaults(func=cmd_validate)

    plan_parser = subparsers.add_parser(
        "plan",
        help="Create a multi-agent refinement/build plan for a seed spec.",
    )
    plan_parser.add_argument("--input", required=True, help="Input seed spec path.")
    plan_parser.add_argument("--json", action="store_true", help="Print agent plan as JSON.")
    plan_parser.set_defaults(func=cmd_plan)

    build_tree_parser = subparsers.add_parser(
        "build",
        help="Build Sephirot and Qliphoth trees from a seed spec.",
    )
    build_tree_parser.add_argument("--input", required=True, help="Input seed spec path.")
    build_tree_parser.add_argument("--out", default="sephirot.graph.json", help="Output graph path.")
    build_tree_parser.add_argument("--threshold", type=float, default=None, help="Override ambiguity threshold.")
    build_tree_parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Build even if ambiguity is above threshold.",
    )
    build_tree_parser.set_defaults(func=cmd_build)

    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Render a seed spec or built graph as HTML, SVG, or Mermaid.",
    )
    visualize_parser.add_argument("--input", required=True, help="Input seed spec or graph JSON path.")
    visualize_parser.add_argument("--out", default="", help="Output visualization path. Prints to stdout if omitted.")
    visualize_parser.add_argument(
        "--format",
        choices=("html", "svg", "mermaid"),
        default="html",
        help="Visualization format.",
    )
    visualize_parser.add_argument("--threshold", type=float, default=None, help="Override ambiguity threshold for seed input.")
    visualize_parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Visualize from a seed even if ambiguity is above threshold.",
    )
    visualize_parser.set_defaults(func=cmd_visualize)

    neo4j_parser = subparsers.add_parser(
        "export-neo4j",
        help="Export a seed spec or built graph as Neo4j-compatible Cypher.",
    )
    neo4j_parser.add_argument("--input", required=True, help="Input seed spec or graph JSON path.")
    neo4j_parser.add_argument("--out", default="", help="Output .cypher path. Prints to stdout if omitted.")
    neo4j_parser.add_argument("--threshold", type=float, default=None, help="Override ambiguity threshold for seed input.")
    neo4j_parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Export from a seed even if ambiguity is above threshold.",
    )
    neo4j_parser.set_defaults(func=cmd_export_neo4j)

    rdf_parser = subparsers.add_parser(
        "export-rdf",
        help="Export a seed spec or built graph as Turtle or JSON-LD.",
    )
    rdf_parser.add_argument("--input", required=True, help="Input seed spec or graph JSON path.")
    rdf_parser.add_argument("--out", default="", help="Output .ttl or .jsonld path. Prints to stdout if omitted.")
    rdf_parser.add_argument(
        "--format",
        choices=("turtle", "jsonld"),
        default="turtle",
        help="RDF serialization format.",
    )
    rdf_parser.add_argument("--threshold", type=float, default=None, help="Override ambiguity threshold for seed input.")
    rdf_parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Export from a seed even if ambiguity is above threshold.",
    )
    rdf_parser.set_defaults(func=cmd_export_rdf)

    graphml_parser = subparsers.add_parser(
        "export-graphml",
        help="Export a seed spec or built graph as GraphML.",
    )
    graphml_parser.add_argument("--input", required=True, help="Input seed spec or graph JSON path.")
    graphml_parser.add_argument("--out", default="", help="Output .graphml path. Prints to stdout if omitted.")
    graphml_parser.add_argument("--threshold", type=float, default=None, help="Override ambiguity threshold for seed input.")
    graphml_parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Export from a seed even if ambiguity is above threshold.",
    )
    graphml_parser.set_defaults(func=cmd_export_graphml)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Check optional agent, API key, and Neo4j integration environment.",
    )
    doctor_parser.add_argument("--json", action="store_true", help="Print checks as JSON.")
    doctor_parser.set_defaults(func=cmd_doctor)

    medicalaos_parser = subparsers.add_parser(
        "compile-medicalaos",
        help="Compile CEKG and AI Patient KG sources into a Sephirot(medical) executable ontology.",
    )
    medicalaos_parser.add_argument(
        "--cekg",
        action="append",
        default=[],
        help="CEKG file or directory. May be supplied multiple times.",
    )
    medicalaos_parser.add_argument(
        "--aipatient",
        action="append",
        default=[],
        help="AI Patient KG JSON file or directory. May be supplied multiple times.",
    )
    medicalaos_parser.add_argument(
        "--mode",
        choices=("off", "advisory", "control"),
        default="advisory",
        help="Runtime KG mode encoded into the activation formula.",
    )
    medicalaos_parser.add_argument("--threshold", type=float, default=0.35, help="KG activation threshold.")
    medicalaos_parser.add_argument(
        "--out",
        default="sephirot.medicalaos.ontology.json",
        help="Output executable ontology JSON path.",
    )
    medicalaos_parser.set_defaults(func=cmd_compile_medicalaos)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"sephirot: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
