import unittest

from sephirot.builder import build_dual_tree
from sephirot.models import load_json
from sephirot.visualization import graph_to_html, graph_to_mermaid, graph_to_svg


class VisualizationTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_dual_tree(load_json("examples/revenue_leader.seed.json"))

    def test_graph_to_svg_contains_dual_tree(self):
        svg = graph_to_svg(self.graph)

        self.assertIn("<svg", svg)
        self.assertIn("Sephirot", svg)
        self.assertIn("Qliphoth", svg)
        self.assertIn("Malkuth", svg)

    def test_graph_to_html_contains_embedded_svg(self):
        html = graph_to_html(self.graph)

        self.assertIn("<!doctype html>", html)
        self.assertIn("<svg", html)

    def test_graph_to_mermaid_contains_paths(self):
        mermaid = graph_to_mermaid(self.graph)

        self.assertIn("flowchart TB", mermaid)
        self.assertIn("-->|11|", mermaid)


if __name__ == "__main__":
    unittest.main()
