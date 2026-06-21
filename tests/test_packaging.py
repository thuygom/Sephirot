import json
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback for local tests.
    tomllib = None


class PackagingTests(unittest.TestCase):
    def test_pyproject_declares_cli_and_template_pack_data(self):
        if tomllib is None:
            self.skipTest("tomllib is unavailable on this Python runtime")
        data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(data["project"]["scripts"]["sephirot"], "sephirot.cli:main")
        data_files = data["tool"]["setuptools"]["data-files"]["share/sephirot/template-packs"]
        self.assertIn("template-packs/core.json", data_files)
        self.assertIn("template-packs/registry.json", data_files)

    def test_template_pack_json_files_parse(self):
        for path in ("template-packs/core.json", "template-packs/registry.json"):
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "0.1")


if __name__ == "__main__":
    unittest.main()
