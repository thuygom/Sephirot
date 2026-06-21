import unittest

from sephirot.ambiguity import next_questions, score_spec
from sephirot.models import blank_spec, load_json


class AmbiguityTests(unittest.TestCase):
    def test_blank_spec_is_ambiguous(self):
        spec = blank_spec("vague")

        self.assertGreater(score_spec(spec), 0.8)
        self.assertTrue(next_questions(spec, limit=2))

    def test_example_spec_is_below_threshold(self):
        spec = load_json("examples/revenue_leader.seed.json")

        self.assertLessEqual(score_spec(spec), 0.2)


if __name__ == "__main__":
    unittest.main()
