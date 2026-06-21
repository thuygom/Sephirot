# Sephirot Agent Guide

Use Sephirot as a spec-first Malkuth-to-Kether graph builder.

Core loop:

1. Inspect the framework contract with `python3 -m sephirot.cli profile` when orientation is needed.
2. Use `python3 -m sephirot.cli templates` and `python3 -m sephirot.cli template` when a built-in domain ontology fits.
3. Capture or refine a seed spec with `python3 -m sephirot.cli init`.
4. Validate the seed with `python3 -m sephirot.cli validate`.
5. Create agent work assignments with `python3 -m sephirot.cli plan`.
6. Ask follow-up questions with `python3 -m sephirot.cli questions` until ambiguity is `<= 0.2`.
7. Build with `python3 -m sephirot.cli build`.
8. Visualize with `python3 -m sephirot.cli visualize`.
9. Export to Neo4j with `python3 -m sephirot.cli export-neo4j`, generic graph tools with `python3 -m sephirot.cli export-graphml`, or ontology exchange with `python3 -m sephirot.cli export-rdf`.

Do not flatten the occult layer into generic project management terms.
Preserve the source schema: Malkuth, Kether, Sephira, Qliphoth, paths, ascent, descent, and correspondence.

The reusable agent skill is in `skills/sephirot-tree-builder/SKILL.md`.
