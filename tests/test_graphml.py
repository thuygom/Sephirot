import unittest
import xml.etree.ElementTree as ET

from sephirot.builder import build_dual_tree
from sephirot.graphml import graph_to_graphml
from sephirot.models import load_json


class GraphMlExportTests(unittest.TestCase):
    def test_graph_to_graphml_is_parseable_and_contains_core_nodes(self):
        graph = build_dual_tree(load_json("examples/revenue_leader.seed.json"))
        graphml = graph_to_graphml(graph)
        root = ET.fromstring(graphml)
        xml = ET.tostring(root, encoding="unicode")

        self.assertIn("graphml", root.tag)
        self.assertIn("Malkuth", xml)
        self.assertIn("Kether", xml)
        self.assertIn("SEPHIROT_PATH", xml)


if __name__ == "__main__":
    unittest.main()
