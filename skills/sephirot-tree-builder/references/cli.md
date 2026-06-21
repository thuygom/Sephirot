# Sephirot CLI Reference

## Artifact Contract

- Seed spec: JSON file with `malkuth`, `kether`, `sephira`, and `paths`.
- Ambiguity score: float from `0.0` to `1.0`; graph build is gated at `<= 0.2`.
- Dual graph: JSON file with `sephirot_tree` and `qliphoth_tree`.
- Neo4j export: Cypher file with `Journey`, `Sephira`, `Qliphoth`, `SEPHIROT_PATH`, `QLIPHOTH_PATH`, and `MIRRORS`.

## Recommended Agent Loop

1. Use `new` to create a blank seed when the user has a rough goal.
2. Ask the user for Malkuth, Kether, each Sephira, and each path CQ answer.
3. Use `score` to compute ambiguity.
4. Use `questions` to select follow-up questions.
5. Repeat until score is `<= 0.2`.
6. Use `build` to create the dual graph JSON.
7. Use `export-neo4j` when graph database compatibility is needed.

## Neo4j Load Example

```bash
python3 -m sephirot.cli export-neo4j --input sephirot.graph.json --out sephirot.cypher
cypher-shell -u neo4j -p "$NEO4J_PASSWORD" -f sephirot.cypher
```

## Draft Mode

Use `--allow-ambiguous` only when the user explicitly wants a rough graph before the spec is ready.
Label the result as a draft and continue collecting answers.
