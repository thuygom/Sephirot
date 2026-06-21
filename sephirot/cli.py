"""Command-line interface for Sephirot."""

from __future__ import annotations

import argparse
import sys

from .ambiguity import next_questions, score_spec
from .builder import build_dual_tree
from .interview import collect_full_sweep, refine_until_threshold
from .models import blank_spec, dump_json, load_json
from .neo4j import graph_to_cypher


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sephirot",
        description="Spec-first Sephirot/Qliphoth knowledge graph builder.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
