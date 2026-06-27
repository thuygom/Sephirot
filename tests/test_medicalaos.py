import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sephirot.medicalaos import compile_medicalaos_ontology, validate_medicalaos_ontology


class MedicalAOSCompilerTests(unittest.TestCase):
    def test_compiles_source_kgs_into_executable_ontology(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            cekg = root / "G_ICD.csv"
            aipatient = root / "CORAL_KG_Export.json"
            cekg.write_text(
                "ICD_Code,ICD_Version,ICD_Code_Title\n"
                "J96,10,Acute respiratory failure\n"
                "A41,10,Sepsis due to unspecified organism\n",
                encoding="utf-8",
            )
            aipatient.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {"labels": ["Patient"], "properties": {"SUBJECT_ID": "100"}},
                            {"labels": ["History"], "properties": {"name": "respiratory failure"}},
                        ],
                        "relationships": [{"relationship": "HAS_HISTORY"}],
                    }
                ),
                encoding="utf-8",
            )

            ontology = compile_medicalaos_ontology(cekg_paths=[cekg], aipatient_paths=[aipatient])

        self.assertEqual(ontology["name"], "Sephirot")
        self.assertEqual(ontology["domain_profile"], "medical")
        self.assertTrue(ontology["validation"]["ok"])
        self.assertEqual(len(ontology["diagnostic_ascent_contract"]["nodes"]), 10)
        self.assertEqual(len(ontology["diagnostic_ascent_contract"]["paths"]), 22)
        self.assertIn(
            "clear, reviewable patient diagnosis",
            ontology["diagnostic_ascent_contract"]["diagnostic_goal"],
        )
        self.assertTrue(
            all(path["scc_reentry_condition"] for path in ontology["diagnostic_ascent_contract"]["paths"])
        )
        self.assertEqual(ontology["source_graphs"]["cekg"]["category_counts"]["respiratory"], 1)
        self.assertEqual(ontology["source_graphs"]["cekg"]["category_counts"]["sepsis"], 1)
        self.assertTrue(any(item["criterion_id"] == "aipatient_structural_prior" for item in ontology["decision_criteria"]))
        self.assertIn("direct_label_override", ontology["runtime_bounds"]["forbidden_actions"])
        self.assertTrue(ontology["scc_contract_templates"][0]["required_edges"])
        self.assertIn("scc_cycle_ontology", ontology)
        self.assertEqual(
            ontology["scc_cycle_ontology"]["graph_model"]["component_type"],
            "nontrivial_strongly_connected_component",
        )
        self.assertGreaterEqual(
            len(ontology["scc_cycle_ontology"]["template_witnesses"][0]["nontrivial_scc_witness_nodes"]),
            2,
        )
        domain_contracts = {
            item["task_id"]: item for item in ontology["domain_runtime_cq_contracts"]
        }
        self.assertEqual(
            set(domain_contracts),
            {
                "phenotyping",
                "in-hospital-mortality",
                "decompensation",
                "length-of-stay",
                "radiology",
            },
        )
        self.assertEqual(domain_contracts["length-of-stay"]["evidence_mode"], "label_free_runtime_cq")
        self.assertEqual(domain_contracts["radiology"]["evidence_mode"], "label_free_runtime_cq")
        self.assertIn(
            "runtime_los_premature_close_pressure",
            domain_contracts["length-of-stay"]["runtime_fields"],
        )
        self.assertIn(
            "runtime_rad_no_finding_conflict_pressure",
            domain_contracts["radiology"]["runtime_fields"],
        )
        self.assertTrue(
            all(
                contract["label_policy"] == "labels_are_offline_audit_targets_only"
                for contract in domain_contracts.values()
            )
        )

    def test_validation_rejects_unbounded_criteria(self):
        ontology = {
            "activation_formula": {},
            "decision_criteria": [
                {
                    "criterion_id": "bad",
                    "source_provenance": [],
                    "allowed_actions": ["direct_label_override"],
                    "forbidden_actions": [],
                    "bounded_effect": {},
                }
            ],
            "clinical_triggers": [],
            "scc_contract_templates": [],
            "runtime_bounds": {},
        }

        report = validate_medicalaos_ontology(ontology)

        self.assertFalse(report["ok"])
        self.assertIn("bad:missing_source_provenance", report["errors"])
        self.assertIn("bad:allows_direct_label_override", report["errors"])


if __name__ == "__main__":
    unittest.main()
