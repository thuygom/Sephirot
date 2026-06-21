---
name: sephirot-tree-builder
description: Build spec-first Sephirot/Qliphoth ontology and knowledge graphs from a Malkuth-to-Kether goal. Use when a user wants a Socratic ambiguity-reduction interview, built-in or external domain templates, 10 Sephira value capture, 22 path Competency Questions, dual positive/negative tree construction, visualization, Neo4j/Cypher export, GraphML export, RDF/Turtle or JSON-LD ontology export, or a Claude Code/Codex/Hermes-style agent workflow for the Sephirot CLI.
---

# Sephirot Tree Builder

## Workflow

Use this skill as an agent shell around the `sephirot` CLI.
The user is trying to make **Malkuth** (the embodied human/current state) become **Kether** (the target archetypal state).

1. Start from the framework profile and a seed spec, not implementation.
2. Use a built-in template when it matches the domain.
3. Fill the Malkuth and Kether fields first.
4. Sweep all 10 Sephira in ascent order from Malkuth to Kether.
5. Sweep all 22 path CQs.
6. Validate the seed against the canonical framework contract.
7. Create an agent plan when work should be split across roles.
8. Ask only the highest-impact missing questions until ambiguity is `<= 0.2`.
9. Build both the Sephirot tree and the Qliphoth mirror tree.
10. Visualize and export graph DB artifacts when requested.

## Commands

Run commands from the Sephirot repository root.

```bash
python3 -m sephirot.cli profile
python3 -m sephirot.cli templates
python3 -m sephirot.cli template-packs
python3 -m sephirot.cli template-registry
python3 -m sephirot.cli template --name succession-agent --out sephirot.seed.json
python3 -m sephirot.cli new --context "current human state -> target state" --out sephirot.seed.json
python3 -m sephirot.cli init "current human state -> target state" --out sephirot.seed.json
python3 -m sephirot.cli validate --input sephirot.seed.json
python3 -m sephirot.cli plan --input sephirot.seed.json
python3 -m sephirot.cli score --input sephirot.seed.json
python3 -m sephirot.cli questions --input sephirot.seed.json --limit 8
python3 -m sephirot.cli build --input sephirot.seed.json --out sephirot.graph.json
python3 -m sephirot.cli visualize --input sephirot.graph.json --format html --out sephirot.graph.html
python3 -m sephirot.cli export-neo4j --input sephirot.graph.json --out sephirot.cypher
python3 -m sephirot.cli export-graphml --input sephirot.graph.json --out sephirot.graphml
python3 -m sephirot.cli export-rdf --input sephirot.graph.json --format turtle --out sephirot.ttl
python3 -m sephirot.cli export-rdf --input sephirot.graph.json --format jsonld --out sephirot.jsonld
```

If the package is installed, `sephirot` can replace `python3 -m sephirot.cli`.

## Agent Behavior

Treat ambiguity as a gate, not a metric for reporting only.
Run `validate` before `build`.
Do not build the final graph when validation is blocked or ambiguity is above `0.2` unless the user explicitly asks for a draft with `--allow-ambiguous`.

Preserve the occult-to-KG correspondence.
Do not flatten Sephira into generic tasks or Qliphoth into generic risks.
Keep the symbolic source schema visible: Sephira, Qliphoth, pillars, paths, ascent, descent, correspondence.

For detailed command semantics and expected artifacts, read [references/cli.md](references/cli.md).
