---
name: sephirot-tree-builder
description: Build spec-first Sephirot/Qliphoth knowledge graphs from a Malkuth-to-Kether goal. Use when a user wants a Socratic ambiguity-reduction interview, 10 Sephira value capture, 22 path Competency Questions, dual positive/negative tree construction, Neo4j/Cypher export, or a Claude Code/Codex/Hermes-style agent workflow for the Sephirot CLI.
---

# Sephirot Tree Builder

## Workflow

Use this skill as an agent shell around the `sephirot` CLI.
The user is trying to make **Malkuth** (the embodied human/current state) become **Kether** (the target archetypal state).

1. Start from a seed spec, not implementation.
2. Fill the Malkuth and Kether fields first.
3. Sweep all 10 Sephira in ascent order from Malkuth to Kether.
4. Sweep all 22 path CQs.
5. Score ambiguity.
6. Ask only the highest-impact missing questions until ambiguity is `<= 0.2`.
7. Build both the Sephirot tree and the Qliphoth mirror tree.
8. Export to graph DB formats when requested, starting with Neo4j Cypher.

## Commands

Run commands from the Sephirot repository root.

```bash
python3 -m sephirot.cli new --context "current human state -> target state" --out sephirot.seed.json
python3 -m sephirot.cli init "current human state -> target state" --out sephirot.seed.json
python3 -m sephirot.cli score --input sephirot.seed.json
python3 -m sephirot.cli questions --input sephirot.seed.json --limit 8
python3 -m sephirot.cli build --input sephirot.seed.json --out sephirot.graph.json
python3 -m sephirot.cli export-neo4j --input sephirot.graph.json --out sephirot.cypher
```

If the package is installed, `sephirot` can replace `python3 -m sephirot.cli`.

## Agent Behavior

Treat ambiguity as a gate, not a metric for reporting only.
Do not build the final graph when ambiguity is above `0.2` unless the user explicitly asks for a draft with `--allow-ambiguous`.

Preserve the occult-to-KG correspondence.
Do not flatten Sephira into generic tasks or Qliphoth into generic risks.
Keep the symbolic source schema visible: Sephira, Qliphoth, pillars, paths, ascent, descent, correspondence.

For detailed command semantics and expected artifacts, read [references/cli.md](references/cli.md).
