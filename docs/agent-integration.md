# Agent Integration

Sephirot should be packaged as three layers:

1. **CLI kernel**: `python3 -m sephirot.cli`
2. **Agent adapter**: `skills/sephirot-tree-builder/SKILL.md`
3. **Editor shell**: VS Code extension or Claude Code IDE integration

The recommended product name for the integration layer is **Sephirot Agent Adapter**.
It is not the graph engine itself; it is the wrapper that lets Claude Code, Codex, Hermes-style agents, or VS Code invoke the graph engine.

## Framework Contract

Every agent shell should treat the CLI as the source of truth.
Use `profile` to discover the canonical ontology framework contract:

```bash
python3 -m sephirot.cli profile
python3 -m sephirot.cli profile --out sephirot.profile.json
```

The profile contains the occult source schema, engineering contract, node labels, relationship labels, 10 Sephirot, Qliphoth mirrors, and 22 CQ paths.
This is the stable handshake for Codex, Claude Code, Hermes-style agents, VS Code, and graph database pipelines.

When the domain matches a reusable pattern, start from a template:

```bash
python3 -m sephirot.cli templates
python3 -m sephirot.cli template-packs
python3 -m sephirot.cli template-registry
python3 -m sephirot.cli template --name succession-agent --out sephirot.seed.json
python3 -m sephirot.cli template --name agent-runtime --out sephirot.seed.json
python3 -m sephirot.cli template --pack path/to/pack.json --name my-template --out sephirot.seed.json
```

Before building the graph, run:

```bash
python3 -m sephirot.cli validate --input sephirot.seed.json
python3 -m sephirot.cli validate --input sephirot.seed.json --json
```

`validate` exits with code `0` only when the seed is structurally valid and ambiguity is below threshold.
If it exits with code `2`, the agent should keep interviewing or repair the seed.

For Hermes/Codex/Claude-style work splitting, run:

```bash
python3 -m sephirot.cli plan --input sephirot.seed.json
python3 -m sephirot.cli plan --input sephirot.seed.json --json
```

After build, generate an inspection artifact:

```bash
python3 -m sephirot.cli visualize --input sephirot.graph.json --format html --out sephirot.graph.html
```

For generic graph tooling, export GraphML:

```bash
python3 -m sephirot.cli export-graphml --input sephirot.graph.json --out sephirot.graphml
```

For ontology exchange, export Turtle or JSON-LD:

```bash
python3 -m sephirot.cli export-rdf --input sephirot.graph.json --format turtle --out sephirot.ttl
python3 -m sephirot.cli export-rdf --input sephirot.graph.json --format jsonld --out sephirot.jsonld
```

## Keys and Environment

Local graph building does not require an LLM key.
Agent shells and graph DB loading may use these variables:

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=...
```

Run:

```bash
python3 -m sephirot.cli doctor
```

Use `.env.example` as the shared template. Do not commit real keys.

## Codex Skill Registration

Install the skill for the current user:

```bash
scripts/install-agent-skill.sh codex
```

This copies the skill to:

```text
${CODEX_HOME:-$HOME/.codex}/skills/sephirot-tree-builder
```

Then ask Codex to use `sephirot-tree-builder`, or invoke it naturally with a request such as:

```text
Use Sephirot to interview me from Malkuth to Kether and build a Neo4j graph.
```

## Claude Code Skill Registration

Claude Code skills can be personal or project-local.

Personal:

```bash
scripts/install-agent-skill.sh claude
```

Project-local:

```bash
scripts/install-agent-skill.sh project-claude
```

Claude Code exposes the skill as:

```text
/sephirot-tree-builder
```

Claude Code also supports project skills under `.claude/skills/<skill-name>/SKILL.md` and personal skills under `~/.claude/skills/<skill-name>/SKILL.md`.

## VS Code Extension

The VS Code extension should remain a thin shell over the CLI.
It should not own the graph logic.

Commands to expose:

- `Sephirot: New Seed`
- `Sephirot: Show Framework Profile`
- `Sephirot: New Seed From Template`
- `Sephirot: Validate Seed`
- `Sephirot: Plan Agent Work`
- `Sephirot: Score Ambiguity`
- `Sephirot: Build Dual Tree`
- `Sephirot: Visualize Graph`
- `Sephirot: Export Neo4j Cypher`
- `Sephirot: Export RDF/JSON-LD`
- `Sephirot: Export GraphML`
- `Sephirot: Doctor`

Package with:

```bash
cd integrations/vscode
npm install
npx @vscode/vsce package
code --install-extension sephirot-*.vsix
```

The extension can store user-facing settings such as the Python path and CLI module.
If the extension ever calls remote LLM APIs directly, store keys in VS Code SecretStorage rather than plain settings.
