# Sephirot CLI Reference

## Artifact Contract

- Seed spec: JSON file with `malkuth`, `kether`, `sephira`, and `paths`.
- Framework profile: JSON manifest with the canonical source schema, ontology contract, node types, relationships, 10 Sephirot, and 22 paths.
- Domain template: Seed spec generated from a reusable ontology pattern such as `succession-agent` or `agent-runtime`.
- Template pack: Marketplace-style manifest that groups reusable templates.
- Validation report: JSON or text report with structural errors, warnings, ambiguity, threshold, and next questions.
- Agent plan: Multi-agent work assignment for Malkuth, Kether, Sephira, CQ paths, Qliphoth red-team checks, and graph outputs.
- Ambiguity score: float from `0.0` to `1.0`; graph build is gated at `<= 0.2`.
- Dual graph: JSON file with `sephirot_tree` and `qliphoth_tree`.
- Visualization: HTML, SVG, or Mermaid graph artifact.
- Neo4j export: Cypher file with `Journey`, `Sephira`, `Qliphoth`, `SEPHIROT_PATH`, `QLIPHOTH_PATH`, and `MIRRORS`.
- GraphML export: generic graph exchange file for graph tooling.
- Ontology export: Turtle or JSON-LD with `Journey`, `Sephira`, `Qliphoth`, `CompetencyQuestionPath`, and `QliphothRiskPath` resources.

## Recommended Agent Loop

1. Use `profile` when the agent needs the canonical framework contract.
2. Use `templates` and `template` when a reusable domain ontology fits.
3. Use `new` to create a blank seed when the user has a rough goal.
4. Ask the user for Malkuth, Kether, each Sephira, and each path CQ answer.
5. Use `validate` to catch structural errors and gate incomplete specs.
6. Use `plan` to split work across agent roles when refinement is non-trivial.
7. Use `questions` to select follow-up questions.
8. Repeat until `validate` passes and score is `<= 0.2`.
9. Use `build` to create the dual graph JSON.
10. Use `visualize` for inspection, `export-neo4j` for graph database loading, `export-graphml` for graph tooling, and `export-rdf` for ontology exchange.

## Framework Profile

```bash
python3 -m sephirot.cli profile
python3 -m sephirot.cli profile --out sephirot.profile.json
```

Use this when another agent shell, editor extension, or graph pipeline needs to discover the canonical contract instead of reading the README.

## Domain Templates

```bash
python3 -m sephirot.cli templates
python3 -m sephirot.cli templates --json
python3 -m sephirot.cli template-packs
python3 -m sephirot.cli template-packs --json
python3 -m sephirot.cli template-registry
python3 -m sephirot.cli template-registry --source path/to/registry.json
python3 -m sephirot.cli template --name succession-agent --out sephirot.seed.json
python3 -m sephirot.cli template --name agent-runtime --out sephirot.seed.json
python3 -m sephirot.cli templates --pack path/to/pack.json
python3 -m sephirot.cli template --pack path/to/pack.json --name my-template --out sephirot.seed.json
```

Templates are starting points, not truth.
Validate and adapt them to the user's domain before final build.
External pack templates use manifest entries with `source: file:relative-seed.json` or `source: builtin:template-name`.
Registry manifests list packs with `source: file:relative-pack.json`, `source: builtin:sephirot-core`, or a remote URL for discovery.

## Validation Gate

```bash
python3 -m sephirot.cli validate --input sephirot.seed.json
python3 -m sephirot.cli validate --input sephirot.seed.json --json
```

Exit code `0` means the seed is structurally valid and ambiguity is below threshold.
Exit code `2` means the agent should keep interviewing or repair the seed before final graph construction.

## Agent Plan

```bash
python3 -m sephirot.cli plan --input sephirot.seed.json
python3 -m sephirot.cli plan --input sephirot.seed.json --json
```

Use this for Hermes/Codex/Claude-style orchestration.
It assigns work to roles such as Malkuth Witness, Kether Architect, Sephira Mapper, Path Auditor, Qliphoth Red Team, and Graph Scribe.

## Visualization

```bash
python3 -m sephirot.cli visualize --input sephirot.graph.json --format html --out sephirot.graph.html
python3 -m sephirot.cli visualize --input sephirot.graph.json --format svg --out sephirot.graph.svg
python3 -m sephirot.cli visualize --input sephirot.graph.json --format mermaid --out sephirot.graph.mmd
```

Visualization can read either a seed spec or a built graph.
Seed input still respects the ambiguity gate unless `--allow-ambiguous` is used.

## GraphML Export

```bash
python3 -m sephirot.cli export-graphml --input sephirot.graph.json --out sephirot.graphml
```

Use GraphML when the output needs to enter graph analysis, graph drawing, or generic graph exchange tools.

## Ontology Export

```bash
python3 -m sephirot.cli export-rdf --input sephirot.graph.json --format turtle --out sephirot.ttl
python3 -m sephirot.cli export-rdf --input sephirot.graph.json --format jsonld --out sephirot.jsonld
```

Use Turtle and JSON-LD when the output needs to enter RDF stores, semantic-web tooling, or ontology review workflows.

## Neo4j Load Example

```bash
python3 -m sephirot.cli export-neo4j --input sephirot.graph.json --out sephirot.cypher
cypher-shell -u neo4j -p "$NEO4J_PASSWORD" -f sephirot.cypher
```

## Draft Mode

Use `--allow-ambiguous` only when the user explicitly wants a rough graph before the spec is ready.
Label the result as a draft and continue collecting answers.
