import unittest

from sephirot.models import blank_spec, load_json
from sephirot.validation import report_as_dict, validate_spec


class ValidationTests(unittest.TestCase):
    def test_example_spec_validates(self):
        report = validate_spec(load_json("examples/revenue_leader.seed.json"))

        self.assertTrue(report.ok)
        self.assertFalse(report.errors)
        self.assertLessEqual(report.ambiguity, report.threshold)

    def test_blank_spec_is_blocked_by_ambiguity(self):
        report = validate_spec(blank_spec("vague"))

        self.assertFalse(report.ok)
        self.assertFalse(report.errors)
        self.assertGreater(report.ambiguity, report.threshold)
        self.assertTrue(report.next_questions)

    def test_path_endpoint_mismatch_is_error(self):
        spec = load_json("examples/revenue_leader.seed.json")
        spec["paths"]["32"]["from"] = "Kether"

        report = validate_spec(spec)
        payload = report_as_dict(report)

        self.assertFalse(report.ok)
        self.assertEqual(payload["errors"][0]["key"], "paths.32.from")


if __name__ == "__main__":
    unittest.main()
