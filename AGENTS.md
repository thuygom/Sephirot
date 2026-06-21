# Sephirot Agent Guide

Use Sephirot as a spec-first Malkuth-to-Kether graph builder.

Core loop:

1. Capture a seed spec with `python3 -m sephirot.cli init`.
2. Score ambiguity with `python3 -m sephirot.cli score`.
3. Ask follow-up questions with `python3 -m sephirot.cli questions` until ambiguity is `<= 0.2`.
4. Build with `python3 -m sephirot.cli build`.
5. Export to Neo4j with `python3 -m sephirot.cli export-neo4j`.

Do not flatten the occult layer into generic project management terms.
Preserve the source schema: Malkuth, Kether, Sephira, Qliphoth, paths, ascent, descent, and correspondence.

The reusable agent skill is in `skills/sephirot-tree-builder/SKILL.md`.
