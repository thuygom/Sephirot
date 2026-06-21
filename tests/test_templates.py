import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sephirot.models import dump_json
from sephirot.templates import (
    build_template_from_pack,
    build_template_spec,
    list_registry_packs,
    list_template_packs,
    list_templates,
    template_registry_manifest,
)
from sephirot.validation import validate_spec


class TemplateTests(unittest.TestCase):
    def test_succession_agent_template_validates(self):
        spec = build_template_spec("succession-agent")
        report = validate_spec(spec)

        self.assertTrue(report.ok)
        self.assertEqual(spec["template"]["name"], "succession-agent")

    def test_agent_runtime_template_is_available(self):
        names = {template["name"] for template in list_templates()}

        self.assertIn("agent-runtime", names)

    def test_core_template_pack_manifest_lists_builtin_templates(self):
        packs = list_template_packs()
        templates = {item["name"] for item in packs[0]["templates"]}

        self.assertEqual(packs[0]["pack"], "sephirot-core")
        self.assertIn("succession-agent", templates)

    def test_core_template_registry_lists_core_pack(self):
        registry = template_registry_manifest()
        packs = {item["pack"] for item in list_registry_packs()}

        self.assertEqual(registry["registry"], "sephirot-core-registry")
        self.assertIn("sephirot-core", packs)

    def test_external_template_pack_loads_file_source(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = build_template_spec("succession-agent")
            dump_json(spec, root / "succession.json")
            (root / "pack.json").write_text(
                json.dumps(
                    {
                        "schema_version": "0.1",
                        "pack": "local-pack",
                        "title": "Local Pack",
                        "description": "Local template pack.",
                        "templates": [
                            {
                                "name": "local-succession",
                                "title": "Local Succession",
                                "description": "Loaded from file.",
                                "source": "file:succession.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            loaded = build_template_from_pack("local-succession", root / "pack.json")

        self.assertEqual(loaded["template"]["name"], "succession-agent")
        self.assertTrue(validate_spec(loaded).ok)


if __name__ == "__main__":
    unittest.main()
