# Succession Agent Prototype

The Succession Agent is the first built-in Sephirot domain template.
It models the ascent from tacit expert dependency to reproducible team capability.

## Generate

```bash
python3 -m sephirot.cli template --name succession-agent --out succession.seed.json
python3 -m sephirot.cli validate --input succession.seed.json
python3 -m sephirot.cli plan --input succession.seed.json
python3 -m sephirot.cli build --input succession.seed.json --out succession.graph.json
python3 -m sephirot.cli visualize --input succession.graph.json --format html --out succession.graph.html
python3 -m sephirot.cli export-neo4j --input succession.graph.json --out succession.cypher
python3 -m sephirot.cli export-graphml --input succession.graph.json --out succession.graphml
python3 -m sephirot.cli export-rdf --input succession.graph.json --format turtle --out succession.ttl
```

## Ontology Shape

- **Malkuth**: the current expert-dependent work surface.
- **Yesod**: runbooks, practice substrate, escalation routes, and habits.
- **Hod**: shared language, metrics, rubrics, and review artifacts.
- **Netzach**: repeated practice and feedback cadence.
- **Tiferet**: integrated successor judgment.
- **Geburah**: quality gates, boundaries, and escalation criteria.
- **Chesed**: coaching, delegation, and resource creation.
- **Binah**: role design, process boundaries, and constraints.
- **Chokmah**: expert pattern recognition made testable.
- **Kether**: succession-ready transferable capability.

The Qliphoth mirror watches for hero dependency, fantasy documentation, punitive standards, false centers, and status replacement disguised as capability transfer.
