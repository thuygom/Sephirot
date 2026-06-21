import unittest

from sephirot.builder import build_dual_tree
from sephirot.models import load_json
from sephirot.rdf import graph_to_jsonld, graph_to_turtle


class RdfExportTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_dual_tree(load_json("examples/revenue_leader.seed.json"))

    def test_graph_to_turtle_contains_core_classes(self):
        turtle = graph_to_turtle(self.graph)

        self.assertIn("@prefix seph:", turtle)
        self.assertIn("rdf:type seph:Journey", turtle)
        self.assertIn("rdf:type seph:Sephira", turtle)
        self.assertIn("rdf:type seph:Qliphoth", turtle)
        self.assertIn("rdf:type seph:CompetencyQuestionPath", turtle)

    def test_graph_to_jsonld_contains_graph(self):
        jsonld = graph_to_jsonld(self.graph)

        self.assertIn("@context", jsonld)
        self.assertIn("@graph", jsonld)
        self.assertTrue(any(item.get("@type") == "Journey" for item in jsonld["@graph"]))


if __name__ == "__main__":
    unittest.main()
