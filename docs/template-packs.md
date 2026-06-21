# Template Packs

Template packs are marketplace-style manifests for reusable Sephirot seed specs.
They let teams distribute domain ontology starts without changing the core framework.

## Manifest

```json
{
  "schema_version": "0.1",
  "pack": "my-domain-pack",
  "title": "My Domain Pack",
  "description": "Reusable Sephirot templates for my domain.",
  "templates": [
    {
      "name": "my-template",
      "title": "My Template",
      "description": "A reusable Malkuth-to-Kether seed.",
      "source": "file:my-template.seed.json"
    }
  ]
}
```

`source` supports:

- `builtin:template-name`
- `file:relative-seed.json`

## Use

```bash
python3 -m sephirot.cli template-packs --path pack.json
python3 -m sephirot.cli templates --pack pack.json
python3 -m sephirot.cli template --pack pack.json --name my-template --out sephirot.seed.json
python3 -m sephirot.cli validate --input sephirot.seed.json
```

Pack templates are starting points.
They still pass through the same validation, ambiguity, Qliphoth mirror, build, visualization, and export gates as built-in templates.

## Registry

A registry lists template packs:

```json
{
  "schema_version": "0.1",
  "registry": "my-registry",
  "title": "My Registry",
  "description": "Team template packs.",
  "packs": [
    {
      "pack": "my-domain-pack",
      "title": "My Domain Pack",
      "description": "Reusable templates.",
      "source": "file:pack.json"
    }
  ]
}
```

Use:

```bash
python3 -m sephirot.cli template-registry
python3 -m sephirot.cli template-registry --source registry.json
python3 -m sephirot.cli template-registry --source https://example.com/sephirot/registry.json
```
