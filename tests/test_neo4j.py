import unittest

from sephirot.builder import build_dual_tree
from sephirot.models import load_json
from sephirot.neo4j import graph_to_cypher


class Neo4jExportTests(unittest.TestCase):
    def test_graph_to_cypher_contains_core_labels_and_relationships(self):
        graph = build_dual_tree(load_json("examples/revenue_leader.seed.json"))
        cypher = graph_to_cypher(graph)

        self.assertIn("CREATE CONSTRAINT sephira_id", cypher)
        self.assertIn(":Sephira", cypher)
        self.assertIn(":Qliphoth", cypher)
        self.assertIn(":SEPHIROT_PATH", cypher)
        self.assertIn(":QLIPHOTH_PATH", cypher)
        self.assertIn("Malkuth", cypher)
        self.assertIn("Kether", cypher)


if __name__ == "__main__":
    unittest.main()
