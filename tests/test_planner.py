import unittest

from sephirot.models import blank_spec
from sephirot.planner import agent_plan, plan_as_markdown
from sephirot.templates import build_template_spec


class PlannerTests(unittest.TestCase):
    def test_blank_spec_plan_assigns_refinement_tasks(self):
        plan = agent_plan(blank_spec("vague"))

        self.assertEqual(plan["status"], "needs-refinement")
        self.assertTrue(plan["tasks"])
        self.assertIn("Malkuth Witness", {task["role"] for task in plan["tasks"]})

    def test_valid_template_plan_is_ready_to_build(self):
        plan = agent_plan(build_template_spec("agent-runtime"))
        text = plan_as_markdown(plan)

        self.assertEqual(plan["status"], "ready-to-build")
        self.assertIn("Graph Scribe", text)


if __name__ == "__main__":
    unittest.main()
