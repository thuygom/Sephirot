import unittest

from sephirot.builder import build_dual_tree
from sephirot.models import blank_spec, load_json


class BuilderTests(unittest.TestCase):
    def test_build_requires_low_ambiguity_by_default(self):
        with self.assertRaises(ValueError):
            build_dual_tree(blank_spec(), threshold=0.2)

    def test_build_dual_tree_from_example(self):
        spec = load_json("examples/revenue_leader.seed.json")
        graph = build_dual_tree(spec, threshold=0.2)

        self.assertEqual(graph["journey"]["from"], "Malkuth")
        self.assertEqual(graph["journey"]["to"], "Kether")
        self.assertEqual(len(graph["sephirot_tree"]["nodes"]), 10)
        self.assertEqual(len(graph["qliphoth_tree"]["nodes"]), 10)
        self.assertEqual(len(graph["sephirot_tree"]["edges"]), 22)
        self.assertEqual(len(graph["qliphoth_tree"]["edges"]), 22)
        self.assertLessEqual(graph["ambiguity"], 0.2)


if __name__ == "__main__":
    unittest.main()
