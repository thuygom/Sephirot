import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from sephirot.cli import main


class CliTests(unittest.TestCase):
    def test_missing_input_returns_error_without_traceback(self):
        stderr = StringIO()
        with redirect_stderr(stderr):
            code = main(["validate", "--input", "/tmp/sephirot-missing-input.json"])

        self.assertEqual(code, 1)
        self.assertIn("sephirot:", stderr.getvalue())

    def test_template_build_visualize_cli_path(self):
        with TemporaryDirectory() as tmp:
            seed = Path(tmp) / "seed.json"
            graph = Path(tmp) / "graph.json"
            svg = Path(tmp) / "graph.svg"
            ttl = Path(tmp) / "graph.ttl"
            graphml = Path(tmp) / "graph.graphml"
            stdout = StringIO()

            with redirect_stdout(stdout):
                self.assertEqual(main(["template", "--name", "succession-agent", "--out", str(seed)]), 0)
                self.assertEqual(main(["validate", "--input", str(seed)]), 0)
                self.assertEqual(main(["build", "--input", str(seed), "--out", str(graph)]), 0)
                self.assertEqual(
                    main(["visualize", "--input", str(graph), "--format", "svg", "--out", str(svg)]),
                    0,
                )
                self.assertEqual(
                    main(["export-rdf", "--input", str(graph), "--format", "turtle", "--out", str(ttl)]),
                    0,
                )
                self.assertEqual(
                    main(["export-graphml", "--input", str(graph), "--out", str(graphml)]),
                    0,
                )
            self.assertIn("<svg", svg.read_text(encoding="utf-8"))
            self.assertIn("seph:Journey", ttl.read_text(encoding="utf-8"))
            self.assertIn("<graphml", graphml.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
