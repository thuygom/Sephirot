import unittest

from sephirot.profile import framework_manifest


class ProfileTests(unittest.TestCase):
    def test_framework_manifest_exposes_canonical_contract(self):
        manifest = framework_manifest()

        self.assertEqual(manifest["kind"], "single-ontology-design-framework")
        self.assertEqual(len(manifest["sephirot"]), 10)
        self.assertEqual(len(manifest["paths"]), 22)
        self.assertIn("ambiguity_gate", manifest["engineering_contract"])
        self.assertIn("validate", manifest["workflow"])
        self.assertIn("visualize", manifest["workflow"])
        self.assertIn("export-rdf", manifest["workflow"])
        self.assertIn("export-graphml", manifest["workflow"])
        self.assertIn(
            "vscode-extension",
            {surface["surface"] for surface in manifest["integration_surfaces"]},
        )


if __name__ == "__main__":
    unittest.main()
