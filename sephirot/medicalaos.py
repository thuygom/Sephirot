"""MedicalAOS domain compiler for Sephirot executable ontologies."""

from __future__ import annotations

import csv
import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .canon import ASCENT_SEPHIROT, PATHS


SCHEMA_VERSION = "2026-06-23.sephirot.medical_executable_ontology.v1"
DEFAULT_THRESHOLD = 0.35

FORBIDDEN_ACTIONS = [
    "direct_label_override",
    "weak_provenance_strong_positive_override",
    "override_safety_or_hitl_gate",
    "use_future_outcome_or_test_label",
]


@dataclass(frozen=True)
class ClinicalPathwayRule:
    category: str
    activation_weight: float
    raw_hint_weight: float
    terms: tuple[str, ...]
    failure_regime: str
    trigger: str
    required_roles: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    risk_floor_candidate: float
    force_cxr_candidate: bool = False


CLINICAL_PATHWAY_RULES: tuple[ClinicalPathwayRule, ...] = (
    ClinicalPathwayRule(
        category="respiratory",
        activation_weight=0.45,
        raw_hint_weight=0.18,
        terms=("pneumonia", "respiratory failure", "hypox", "pulmonary", "copd"),
        failure_regime="unresolved_respiratory_compromise",
        trigger="Respiratory CEKG pathway or raw diagnosis hint indicates unresolved oxygenation or ventilation risk.",
        required_roles=("respiratory_agent", "trajectory_agent", "evidence_planner", "safety_checker"),
        allowed_actions=(
            "diagnosis_grounding",
            "provenance_attribution",
            "contradiction_hint",
            "imaging_escalation_support",
            "bounded_risk_floor",
        ),
        risk_floor_candidate=0.45,
        force_cxr_candidate=True,
    ),
    ClinicalPathwayRule(
        category="sepsis",
        activation_weight=0.55,
        raw_hint_weight=0.22,
        terms=("sepsis", "septic", "shock", "bacteremia", "infection"),
        failure_regime="sepsis_or_shock_deterioration",
        trigger="CEKG or raw diagnosis evidence indicates infection, sepsis, shock, or unstable source-control risk.",
        required_roles=("sepsis_agent", "fluid_agent", "trajectory_agent", "safety_checker"),
        allowed_actions=(
            "diagnosis_grounding",
            "provenance_attribution",
            "contradiction_hint",
            "bounded_risk_floor",
        ),
        risk_floor_candidate=0.55,
    ),
    ClinicalPathwayRule(
        category="cardiopulmonary",
        activation_weight=0.40,
        raw_hint_weight=0.16,
        terms=("heart failure", "congestive heart failure", "cardiogenic", "pulmonary edema"),
        failure_regime="cardiopulmonary_overlap_or_modality_conflict",
        trigger="Cardiopulmonary CEKG evidence indicates overlapping cardiac and respiratory deterioration risk.",
        required_roles=("respiratory_agent", "fluid_agent", "trajectory_agent", "evidence_planner"),
        allowed_actions=(
            "diagnosis_grounding",
            "provenance_attribution",
            "contradiction_hint",
            "bounded_risk_floor",
        ),
        risk_floor_candidate=0.40,
    ),
    ClinicalPathwayRule(
        category="renal_metabolic",
        activation_weight=0.35,
        raw_hint_weight=0.14,
        terms=("renal failure", "kidney", "acidosis", "metabolic", "dialysis"),
        failure_regime="renal_metabolic_instability",
        trigger="Renal or metabolic CEKG evidence indicates organ-support or acid-base instability.",
        required_roles=("fluid_agent", "trajectory_agent", "evidence_planner", "safety_checker"),
        allowed_actions=(
            "diagnosis_grounding",
            "provenance_attribution",
            "contradiction_hint",
            "bounded_risk_floor",
        ),
        risk_floor_candidate=0.38,
    ),
)


def compile_medicalaos_ontology(
    *,
    cekg_paths: Iterable[str | Path] | None = None,
    aipatient_paths: Iterable[str | Path] | None = None,
    mode: str = "advisory",
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    """Compile source clinical KGs into MedicalAOS runtime criteria."""

    cekg_sources = _load_cekg_sources(cekg_paths or [])
    aipatient_sources = _load_aipatient_sources(aipatient_paths or [])
    criteria = _build_decision_criteria(cekg_sources, aipatient_sources)
    scc_templates = _build_scc_contract_templates()
    ascent_contract = _build_diagnostic_ascent_contract()
    scc_cycle_ontology = _build_scc_cycle_ontology(scc_templates)
    ontology = {
        "schema_version": SCHEMA_VERSION,
        "name": "Sephirot",
        "domain_profile": "medical",
        "product_position": "Sephirot(medical) executable ontology generator for MedicalAOS",
        "runtime_role": (
            "Compile CEKG and AI Patient KG source evidence into bounded runtime criteria "
            "for Clinical Harness triggers, SCC orchestration, MAS role contracts, and KG use."
        ),
        "source_graphs": {
            "cekg": cekg_sources,
            "aipatient": aipatient_sources,
        },
        "diagnostic_ascent_contract": ascent_contract,
        "activation_formula": _build_activation_formula(mode=mode, threshold=threshold),
        "decision_criteria": criteria,
        "clinical_triggers": _build_clinical_triggers(),
        "domain_runtime_cq_contracts": _build_domain_runtime_cq_contracts(),
        "scc_cycle_ontology": scc_cycle_ontology,
        "scc_contract_templates": scc_templates,
        "mas_role_cards": _build_mas_role_cards(),
        "prompt_cards": _build_prompt_cards(),
        "qliphoth_failure_mirrors": _build_failure_mirrors(),
        "runtime_bounds": {
            "allowed_global_actions": sorted(
                {
                    action
                    for criterion in criteria
                    for action in criterion.get("allowed_actions", [])
                }
            ),
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "max_delta_rule": "abs(delta_kg) <= lambda_kg(c, provenance, corroboration)",
            "safety_gate_rule": "KG, MAS, and SCC evidence cannot override HITL or safety-stop gates.",
        },
    }
    ontology["validation"] = validate_medicalaos_ontology(ontology)
    return ontology


def validate_medicalaos_ontology(ontology: dict[str, Any]) -> dict[str, Any]:
    """Validate that compiled criteria are executable, bounded, and source-backed."""

    errors: list[str] = []
    required_top = [
        "diagnostic_ascent_contract",
        "activation_formula",
        "decision_criteria",
        "clinical_triggers",
        "domain_runtime_cq_contracts",
        "scc_cycle_ontology",
        "scc_contract_templates",
        "runtime_bounds",
    ]
    for key in required_top:
        if key not in ontology:
            errors.append(f"missing_top_level:{key}")

    for criterion in ontology.get("decision_criteria", []):
        criterion_id = criterion.get("criterion_id", "<missing>")
        if not criterion.get("source_provenance"):
            errors.append(f"{criterion_id}:missing_source_provenance")
        if not criterion.get("allowed_actions"):
            errors.append(f"{criterion_id}:missing_allowed_actions")
        if not criterion.get("forbidden_actions"):
            errors.append(f"{criterion_id}:missing_forbidden_actions")
        if not criterion.get("bounded_effect"):
            errors.append(f"{criterion_id}:missing_bounded_effect")
        if "direct_label_override" in criterion.get("allowed_actions", []):
            errors.append(f"{criterion_id}:allows_direct_label_override")

    ascent = ontology.get("diagnostic_ascent_contract", {})
    if len(ascent.get("nodes", [])) != 10:
        errors.append("diagnostic_ascent_contract:requires_10_nodes")
    if len(ascent.get("paths", [])) != 22:
        errors.append("diagnostic_ascent_contract:requires_22_paths")
    for node in ascent.get("nodes", []):
        node_id = node.get("id", "<missing>")
        if not node.get("clinical_obligation"):
            errors.append(f"diagnostic_ascent_node:{node_id}:missing_clinical_obligation")
        if not node.get("qliphoth_failure_if_neglected"):
            errors.append(f"diagnostic_ascent_node:{node_id}:missing_qliphoth_failure")
    for path in ascent.get("paths", []):
        path_id = path.get("id", "<missing>")
        if not path.get("competency_question"):
            errors.append(f"diagnostic_ascent_path:{path_id}:missing_competency_question")
        if not path.get("scc_reentry_condition"):
            errors.append(f"diagnostic_ascent_path:{path_id}:missing_scc_reentry_condition")

    for template in ontology.get("scc_contract_templates", []):
        template_id = template.get("template_id", "<missing>")
        cyclic_nodes = _largest_nontrivial_scc_nodes(
            template.get("review_nodes", []),
            template.get("required_edges", []),
        )
        if len(template.get("review_nodes", [])) < 2:
            errors.append(f"{template_id}:nontrivial_scc_requires_two_review_nodes")
        if len(cyclic_nodes) < 2:
            errors.append(f"{template_id}:required_edges_do_not_form_nontrivial_scc")
        if not any(edge.get("relation") == "challenge_or_revise" for edge in template.get("required_edges", [])):
            errors.append(f"{template_id}:missing_challenge_or_revise_edge")

    domain_contracts = ontology.get("domain_runtime_cq_contracts", [])
    required_tasks = {
        "phenotyping",
        "in-hospital-mortality",
        "decompensation",
        "length-of-stay",
        "radiology",
    }
    by_task = {
        str(contract.get("task_id")): contract
        for contract in domain_contracts
        if isinstance(contract, dict)
    }
    missing_tasks = sorted(required_tasks - set(by_task))
    if missing_tasks:
        errors.append(f"domain_runtime_cq_contracts:missing_tasks:{','.join(missing_tasks)}")
    for task_id, contract in by_task.items():
        if not contract.get("runtime_fields"):
            errors.append(f"domain_runtime_cq_contract:{task_id}:missing_runtime_fields")
        if not contract.get("competency_questions"):
            errors.append(f"domain_runtime_cq_contract:{task_id}:missing_competency_questions")
        if not contract.get("qliphoth_risks_if_failed"):
            errors.append(f"domain_runtime_cq_contract:{task_id}:missing_qliphoth_risks")
        if contract.get("label_policy") != "labels_are_offline_audit_targets_only":
            errors.append(f"domain_runtime_cq_contract:{task_id}:invalid_label_policy")
    for task_id in ("length-of-stay", "radiology"):
        contract = by_task.get(task_id) or {}
        if contract.get("evidence_mode") != "label_free_runtime_cq":
            errors.append(f"domain_runtime_cq_contract:{task_id}:requires_label_free_runtime_cq")

    return {
        "ok": not errors,
        "errors": errors,
        "criterion_count": len(ontology.get("decision_criteria", [])),
        "scc_template_count": len(ontology.get("scc_contract_templates", [])),
    }


def dump_medicalaos_ontology(ontology: dict[str, Any], path: str | Path | None = None) -> str:
    text = json.dumps(ontology, ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    return text


def _build_activation_formula(*, mode: str, threshold: float) -> dict[str, Any]:
    return {
        "schema_version": "2026-06-23.sephirot.kg_activation_formula.v1",
        "mode": mode,
        "formula": "open_KG = 1[mode in {advisory, control}] and KG_use_score >= theta_kg",
        "kg_use_score": (
            "min(1.0, max(CEKG_pathway_score, raw_diagnosis_hint_score) "
            "+ provenance_score + AI_Patient_case_prior_score)"
        ),
        "threshold": round(float(threshold), 4),
        "component_rules": {
            "CEKG_pathway_score": "Max weight among CEKG-grounded clinical pathway criteria.",
            "raw_diagnosis_hint_score": "Lower-weight fallback from diagnosis text when CEKG concept grounding is absent.",
            "provenance_score": "Bounded bonus for explicit source, matched concept, and confidence evidence.",
            "AI_Patient_case_prior_score": "Case-level exact, structural, or demographic AI Patient KG prior; loaded corpus alone is insufficient.",
        },
    }


def _build_diagnostic_ascent_contract() -> dict[str, Any]:
    node_obligations = {
        "Malkuth": "Observe the material patient state: EHR time series, demographics, diagnoses, CXR availability, and current predictor evidence.",
        "Yesod": "Prepare a reliable evidence substrate: interfaces, provenance, modality readiness, KG availability, and no corpus-only readiness claims.",
        "Hod": "Formalize the case into analyzable criteria: thresholds, scores, trace metrics, KG activation formula, and explanation artifacts.",
        "Netzach": "Track persistence and trajectory: deterioration, repeated instability, unresolved uncertainty, and temporal pressure.",
        "Tiferet": "Integrate competing agent claims into a coherent clinical judgment without erasing calibrated predictor evidence.",
        "Geburah": "Apply discipline and judgment: safety gates, forbidden actions, HITL escalation, and rejection of unsafe finalization.",
        "Chesed": "Expand only with justification: CXR lane, KG verification, SCC review, or specialist agents when triggers require them.",
        "Binah": "Constrain meaning: clinical category boundaries, CEKG provenance, AI Patient KG linkage, and bounded decision effects.",
        "Chokmah": "Generate plausible differential hypotheses and deterioration pathways for specialist review.",
        "Kether": "Reach a reviewable diagnostic/termination state: clear diagnosis or bounded residual-risk state with traceable evidence.",
    }
    qliphoth_if_neglected = {
        "Malkuth": "Surface-level diagnosis disconnected from observed patient evidence.",
        "Yesod": "Illusion of readiness, such as treating a loaded KG corpus as case-level evidence.",
        "Hod": "Poisoned logic: metrics, prompts, or explanations rationalize an unsupported decision.",
        "Netzach": "Trajectory blindness: persistent deterioration is ignored as a one-shot prediction problem.",
        "Tiferet": "False center: weak synthesized assessment overrides calibrated base-risk evidence.",
        "Geburah": "Safety collapse: KG, MAS, or SCC bypasses HITL, safety stop, or forbidden-action constraints.",
        "Chesed": "Over-expansion: all agents, KG paths, or imaging lanes open without trigger evidence.",
        "Binah": "Hidden assumption: clinical category, provenance, or leakage boundary is left implicit.",
        "Chokmah": "Ungrounded hypothesis generation without structural validation.",
        "Kether": "Split goal: apparent final answer without reviewable diagnosis, residual risk, or termination artifact.",
    }
    path_actions = {
        11: "Generate alternative deterioration hypotheses only after the target diagnostic goal is fixed.",
        12: "Bind the diagnostic target to explicit clinical constraints and verification requirements.",
        13: "Keep every decision aligned with the central diagnostic and safety principle.",
        14: "Filter hypotheses through clinical category and provenance constraints.",
        15: "Select which hypothesis deserves central review by the SCC or assessment lane.",
        16: "Expand resources only for hypotheses that justify extra evidence or specialist review.",
        17: "Integrate clinical constraints into the main judgment rather than treating them as side notes.",
        18: "Convert constraints into enforceable safety, leakage, and forbidden-action rules.",
        19: "Balance review expansion against discipline so the harness does not become fullmesh by default.",
        20: "Use expansions only when they serve integrated diagnosis and runtime governance.",
        21: "Sustain review for persistent clinical signals, not transient or decorative evidence.",
        22: "Let high-risk constraints reshape central judgment and termination state.",
        23: "Represent controls as data: metrics, traces, edge coverage, policy checks, and artifacts.",
        24: "Carry integrated judgment across repeated instability and bounded re-entry.",
        25: "Ensure the evidence substrate is ready before final diagnosis or termination.",
        26: "Explain why the integrated judgment is coherent, bounded, and reviewable.",
        27: "Use temporal persistence and analysis to correct each other.",
        28: "Convert persistent uncertainty into readiness checks and bounded next actions.",
        29: "Verify that sustained claims are visible in real patient evidence.",
        30: "Turn analysis into executable SCC/KG/Clinical Harness protocols.",
        31: "Confirm or falsify analysis against material case evidence.",
        32: "Define the minimum executable foundation for the next concrete diagnostic step.",
    }
    nodes = [
        {
            "id": profile.name,
            "number": profile.number,
            "ascent_order": profile.ascent_order,
            "clinical_obligation": node_obligations[profile.name],
            "agent_responsibility": _agent_responsibility_for_node(profile.name),
            "qliphoth_failure_if_neglected": qliphoth_if_neglected[profile.name],
            "must_emit_or_check": _artifact_obligation_for_node(profile.name),
        }
        for profile in ASCENT_SEPHIROT
    ]
    paths = [
        {
            "id": f"path-{path.number}",
            "number": path.number,
            "from": path.source,
            "to": path.target,
            "competency_question": path.cq,
            "diagnostic_action": path_actions[path.number],
            "scc_reentry_condition": (
                "Open or re-enter a local SCC when this path exposes contradiction, missing evidence, "
                "unsafe finalization, modality conflict, KG provenance failure, or persistent deterioration."
            ),
            "qliphoth_failure_if_skipped": (
                f"The ascent from {path.source} to {path.target} becomes implicit, making the diagnosis "
                "unreviewable or vulnerable to unsafe shortcut reasoning."
            ),
        }
        for path in PATHS
    ]
    return {
        "schema_version": "2026-06-23.sephirot.diagnostic_ascent_contract.v1",
        "diagnostic_goal": "Move from Malkuth to Kether by producing a clear, reviewable patient diagnosis or bounded residual-risk termination state.",
        "global_graph": "The 10-node/22-path Sephirot ascent is treated as an auditable DAG of diagnostic obligations.",
        "local_cycle_rule": (
            "Between DAG steps, local SCCs provide bounded agent-to-agent cyclic review. "
            "The global ascent must remain condensible to a DAG, while local failures may require cyclic mutual revision."
        ),
        "all_nodes_required": True,
        "all_paths_required": True,
        "nodes": nodes,
        "paths": paths,
    }


def _build_decision_criteria(
    cekg_sources: dict[str, Any],
    aipatient_sources: dict[str, Any],
) -> list[dict[str, Any]]:
    criteria = []
    category_terms = cekg_sources.get("category_terms", {})
    for rule in CLINICAL_PATHWAY_RULES:
        matched_terms = category_terms.get(rule.category, [])
        provenance = [
            {
                "source_graph": "MIMIC-IV-Ext-CEKG",
                "path": item.get("path", ""),
                "matched_field": item.get("matched_field", "ICD_Code_Title"),
                "matched_value": item.get("matched_value", ""),
                "category": rule.category,
            }
            for item in matched_terms[:8]
        ]
        if not provenance:
            provenance = [
                {
                    "source_graph": "Sephirot-MedicalAOS",
                    "path": "compiler_default",
                    "matched_field": "clinical_pathway_rule",
                    "matched_value": ", ".join(rule.terms),
                    "category": rule.category,
                }
            ]
        criteria.append(
            {
                "criterion_id": f"cekg_{rule.category}_pathway",
                "criterion_type": "clinical_pathway",
                "source_provenance": provenance,
                "trigger": rule.trigger,
                "activation_weight": rule.activation_weight,
                "raw_hint_weight": rule.raw_hint_weight,
                "matched_terms": [item.get("matched_value", "") for item in matched_terms[:12]],
                "failure_regime": rule.failure_regime,
                "required_scc_roles": list(rule.required_roles),
                "allowed_actions": sorted(set(rule.allowed_actions)),
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "bounded_effect": {
                    "risk_floor_candidate": rule.risk_floor_candidate,
                    "force_cxr_candidate": rule.force_cxr_candidate,
                    "label_override_allowed": False,
                    "safety_gate_override_allowed": False,
                },
            }
        )

    criteria.extend(_build_aipatient_criteria(aipatient_sources))
    return criteria


def _build_aipatient_criteria(aipatient_sources: dict[str, Any]) -> list[dict[str, Any]]:
    provenance = []
    for dataset in aipatient_sources.get("datasets", []):
        provenance.append(
            {
                "source_graph": "AI Patient KG",
                "path": dataset.get("path", ""),
                "matched_field": "dataset",
                "matched_value": dataset.get("dataset", ""),
            }
        )
    if not provenance:
        provenance = [
            {
                "source_graph": "Sephirot-MedicalAOS",
                "path": "compiler_default",
                "matched_field": "case_prior_rule",
                "matched_value": "exact_patient, structural_analog, demographic_context",
            }
        ]
    return [
        {
            "criterion_id": "aipatient_exact_patient_prior",
            "criterion_type": "case_prior",
            "source_provenance": provenance,
            "trigger": "Exact patient linkage exists in AI Patient KG.",
            "activation_weight": 0.35,
            "allowed_actions": ["case_packet_enrichment", "provenance_attribution"],
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "bounded_effect": {
                "risk_floor_candidate": 0.0,
                "force_cxr_candidate": False,
                "label_override_allowed": False,
                "safety_gate_override_allowed": False,
            },
        },
        {
            "criterion_id": "aipatient_structural_prior",
            "criterion_type": "case_prior",
            "source_provenance": provenance,
            "trigger": "History, symptom, diagnosis, or admission structure overlaps with the current case.",
            "activation_weight": 0.25,
            "allowed_actions": ["case_packet_enrichment", "contradiction_hint"],
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "bounded_effect": {
                "risk_floor_candidate": 0.0,
                "force_cxr_candidate": False,
                "label_override_allowed": False,
                "safety_gate_override_allowed": False,
            },
        },
        {
            "criterion_id": "aipatient_demographic_context",
            "criterion_type": "case_prior",
            "source_provenance": provenance,
            "trigger": "Demographic analogs exist without stronger patient or structural linkage.",
            "activation_weight": 0.10,
            "allowed_actions": ["case_packet_enrichment"],
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "bounded_effect": {
                "risk_floor_candidate": 0.0,
                "force_cxr_candidate": False,
                "label_override_allowed": False,
                "safety_gate_override_allowed": False,
            },
        },
    ]


def _build_clinical_triggers() -> list[dict[str, Any]]:
    return [
        {
            "trigger_id": f"trigger_{rule.category}",
            "category": rule.category,
            "opens": ["kg_verification", "scc_re_review"],
            "failure_regime": rule.failure_regime,
            "signal_terms": list(rule.terms),
            "scc_roster": list(rule.required_roles),
            "termination_bounds": [
                "budget_exhausted",
                "planner_no_further_escalation",
                "safety_stop",
                "hitl_required",
            ],
        }
        for rule in CLINICAL_PATHWAY_RULES
    ]


def _build_domain_runtime_cq_contracts() -> list[dict[str, Any]]:
    common_gate = {
        "same_review_budget_required": True,
        "task_exclusion_forbidden": True,
        "labels_are_trigger_inputs": False,
        "must_track": [
            "KTrig",
            "TrigErr",
            "ErrLift",
            "BurdenCap",
            "DeltaLift",
            "top_error_recall",
            "unsafe_close_candidate_rate",
        ],
    }
    return [
        {
            "task_id": "phenotyping",
            "evidence_mode": "runtime_trigger",
            "sephirot_nodes": ["Malkuth", "Yesod", "Hod", "Binah", "Tiferet"],
            "sephirot_paths": ["path-32", "path-28", "path-15", "path-14", "path-25"],
            "runtime_fields": [
                "runtime_pheno_path32_yesod_malkuth_cq",
                "source_yesod_minimum_substrate_pressure",
                "source_path_32_malkuth_yesod_review_bridge",
                "source_path_15_review_ready_absence",
            ],
            "competency_questions": [
                "Does observed patient evidence form a minimum reviewable substrate before multilabel closure?",
                "Does a high-burden label set require central review before Kether closure?",
            ],
            "qliphoth_risks_if_failed": [
                "multilabel close without evidence substrate",
                "central review absent despite high condition burden",
            ],
            "scc_reentry_lane": "path32_evidence_substrate_review",
            "label_policy": "labels_are_offline_audit_targets_only",
            "promotion_gate": common_gate,
        },
        {
            "task_id": "in-hospital-mortality",
            "evidence_mode": "runtime_trigger",
            "sephirot_nodes": ["Malkuth", "Netzach", "Yesod", "Hod", "Geburah", "Kether"],
            "sephirot_paths": ["path-28", "path-30", "path-22", "path-26", "path-32"],
            "runtime_fields": [
                "runtime_core_source_path_28_netzach_yesod_bridge",
                "runtime_core_node_hod_pressure",
                "runtime_core_path_15_chokmah_tiferet_cq",
                "runtime_core_node_binah_pressure",
            ],
            "competency_questions": [
                "Does persistent deterioration become an evidence-readiness recheck before mortality closure?",
                "Can the close be reviewed without bypassing safety and HITL gates?",
            ],
            "qliphoth_risks_if_failed": [
                "trajectory blindness before terminal decision",
                "unsafe mortality close without bounded review packet",
            ],
            "scc_reentry_lane": "bounded_clinical_verification_scc",
            "label_policy": "labels_are_offline_audit_targets_only",
            "promotion_gate": common_gate,
        },
        {
            "task_id": "decompensation",
            "evidence_mode": "runtime_trigger",
            "sephirot_nodes": ["Netzach", "Hod", "Tiferet", "Geburah", "Yesod"],
            "sephirot_paths": ["path-28", "path-26", "path-22", "path-24", "path-30"],
            "runtime_fields": [
                "runtime_decomp_hod_executable_pressure",
                "runtime_core_node_hod_pressure",
                "runtime_core_source_hod_protocolized_review_gap",
                "runtime_core_source_hod_executable_analysis_gap",
            ],
            "competency_questions": [
                "Is deterioration translated into executable analysis rather than a score-only close?",
                "Does the central judgment return to metric evidence before direct closure?",
            ],
            "qliphoth_risks_if_failed": [
                "deterioration review without executable criterion",
                "metric explanation gap hidden by direct close",
            ],
            "scc_reentry_lane": "hod_executable_deterioration_review",
            "label_policy": "labels_are_offline_audit_targets_only",
            "promotion_gate": common_gate,
        },
        {
            "task_id": "length-of-stay",
            "evidence_mode": "label_free_runtime_cq",
            "sephirot_nodes": ["Malkuth", "Yesod", "Netzach", "Hod", "Geburah"],
            "sephirot_paths": ["path-32", "path-28", "path-26", "path-22", "path-30"],
            "runtime_fields": [
                "runtime_los_low_bin_late_pressure",
                "runtime_los_underestimate_pressure",
                "runtime_los_elapsed_bin_mismatch_pressure",
                "runtime_los_confident_underestimate_pressure",
                "runtime_los_premature_close_pressure",
            ],
            "competency_questions": [
                "Does observed stay duration contradict the predicted close bin?",
                "Is a low-bin or underestimated LOS prediction being closed while elapsed evidence remains late or unresolved?",
                "Does the case need path-28 re-entry because persistence was not converted into readiness evidence?",
            ],
            "qliphoth_risks_if_failed": [
                "premature LOS close",
                "elapsed-stay contradiction left outside review",
                "large-task residual burden masked by aggregate lift",
            ],
            "scc_reentry_lane": "los_premature_close_domain_cq_refinement",
            "label_policy": "labels_are_offline_audit_targets_only",
            "promotion_gate": common_gate,
        },
        {
            "task_id": "radiology",
            "evidence_mode": "label_free_runtime_cq",
            "sephirot_nodes": ["Malkuth", "Yesod", "Chokmah", "Binah", "Geburah", "Tiferet"],
            "sephirot_paths": ["path-32", "path-14", "path-15", "path-22", "path-25"],
            "runtime_fields": [
                "runtime_rad_evidence_readiness_pressure",
                "runtime_rad_lung_uncertainty_pressure",
                "runtime_rad_hard_label_uncertainty_pressure",
                "runtime_rad_multifinding_pressure",
                "runtime_rad_safety_gate_pressure",
                "runtime_rad_no_finding_conflict_pressure",
            ],
            "competency_questions": [
                "Does report evidence support a direct no-finding or finding-positive close?",
                "Do uncertain lung or hard-label findings require central review before finalization?",
                "Does the safety gate reshape central judgment when multiple findings or rare positives are present?",
            ],
            "qliphoth_risks_if_failed": [
                "no-finding conflict closed as certainty",
                "finding uncertainty hidden by report-level shortcut",
                "safety-gated abnormality finalized without review packet",
            ],
            "scc_reentry_lane": "radiology_report_closure_domain_cq_refinement",
            "label_policy": "labels_are_offline_audit_targets_only",
            "promotion_gate": common_gate,
        },
    ]


def _build_scc_cycle_ontology(scc_templates: list[dict[str, Any]]) -> dict[str, Any]:
    templates = []
    for template in scc_templates:
        cyclic_nodes = _largest_nontrivial_scc_nodes(
            template.get("review_nodes", []),
            template.get("required_edges", []),
        )
        templates.append(
            {
                "template_id": template.get("template_id"),
                "nontrivial_scc_witness_nodes": cyclic_nodes,
                "condensation_rule": (
                    "After SCC execution, strongly connected role components are condensed into a DAG "
                    "so the global workflow remains auditable and terminating."
                ),
                "cycle_witness_rule": (
                    "A valid opened SCC must contain at least two non-system review agents with bidirectional "
                    "or longer cyclic reachability over required review edges."
                ),
            }
        )
    return {
        "schema_version": "2026-06-23.sephirot.scc_cycle_ontology.v1",
        "definition": (
            "SCC is a local strongly connected component over the MedicalAOS agent role-interaction graph. "
            "It is opened only by clinical failure triggers and encodes mutual revision among agents, "
            "not unrestricted conversation or global workflow cyclicity."
        ),
        "graph_model": {
            "node_type": "agent_role_or_runtime_state",
            "edge_type": "required_review_relation",
            "component_type": "nontrivial_strongly_connected_component",
            "minimum_review_nodes": 2,
            "algorithm": "Tarjan strongly connected components",
            "global_structure": "DAG with local failure-triggered SCC and condensation artifact",
        },
        "opening_formula": {
            "formula": (
                "open_SCC = direct_finalization_unsafe and mutual_revision_required "
                "and single_lane_insufficient and budget_available"
            ),
            "components": {
                "direct_finalization_unsafe": "Safety concern, deterioration, high opening score, or insufficient support.",
                "mutual_revision_required": "At least two review agents must be in the cyclic component.",
                "single_lane_insufficient": "One-pass KG, imaging, or assessment lane cannot resolve the active failure regime.",
                "budget_available": "k_max and evidence budget allow bounded re-review.",
            },
        },
        "sephirot_projection": {
            "Malkuth": "Observed patient evidence, runtime trace, and material trigger state.",
            "Yesod": "Executable SCC contract, required edges, budgets, and interface readiness.",
            "Hod": "Graph witness, Tarjan component evidence, edge coverage, and trace metrics.",
            "Netzach": "Bounded persistence through k_max re-entry and convergence pressure.",
            "Tiferet": "Integrated clinical judgment after competing agent claims are reconciled.",
            "Geburah": "Safety gates, forbidden edges, HITL escalation, and rejection of unsafe finalization.",
            "Chesed": "Controlled expansion from single lane to specialist roster only when trigger evidence justifies it.",
            "Binah": "Clinical constraints, source provenance, and bounded KG decision criteria.",
            "Chokmah": "Alternative clinical hypotheses proposed by specialist agents.",
            "Kether": "Reviewable termination state with explicit residual risk or safe containment.",
        },
        "qliphoth_mirrors": [
            {
                "failure_id": "unbounded_agent_loop",
                "mirror_of": "Yesod",
                "failure_mode": "Agent discussion cycles without a graph contract, budget, or termination condition.",
                "containment": "Require nontrivial SCC witness, k_max, required edges, condensation artifact, and stop state.",
            },
            {
                "failure_id": "fake_scc_fullmesh",
                "mirror_of": "Chesed",
                "failure_mode": "Every agent talks to every other agent, hiding a lack of trigger-specific structure.",
                "containment": "Use trigger-to-roster mappings and compare against random/fullmesh SCC ablations.",
            },
            {
                "failure_id": "acyclic_review_mislabeled_as_scc",
                "mirror_of": "Hod",
                "failure_mode": "A linear or one-pass review path is reported as SCC without cyclic reachability.",
                "containment": "Compute Tarjan SCC on required role edges and reject contracts without >=2 cyclic review nodes.",
            },
        ],
        "template_witnesses": templates,
    }


def _build_scc_contract_templates() -> list[dict[str, Any]]:
    return [
        {
            "template_id": "bounded_clinical_verification_scc",
            "purpose": "Non-trivial SCC for contested clinical evidence, KG grounding, and safety termination.",
            "component_semantics": {
                "definition": (
                    "A local strongly connected component among review agents where each participating role "
                    "can reach and be reached by another role through required review edges."
                ),
                "not_a": [
                    "global workflow loop",
                    "unbounded deliberation",
                    "fullmesh committee by default",
                    "predictor replacement",
                ],
            },
            "review_nodes": [
                "evidence_planner",
                "trajectory_agent",
                "safety_checker",
                "external_kg",
            ],
            "required_edges": [
                {"source": "evidence_planner", "target": "trajectory_agent", "relation": "request_temporal_support"},
                {"source": "trajectory_agent", "target": "safety_checker", "relation": "risk_trajectory_challenge"},
                {"source": "safety_checker", "target": "evidence_planner", "relation": "gate_reopen"},
                {"source": "external_kg", "target": "evidence_planner", "relation": "bounded_verification"},
                {"source": "evidence_planner", "target": "external_kg", "relation": "challenge_or_revise"},
            ],
            "scc_validity_rule": {
                "nontrivial_component_required": True,
                "minimum_cyclic_review_nodes": 2,
                "cyclic_witness_nodes": [
                    "evidence_planner",
                    "trajectory_agent",
                    "safety_checker",
                ],
                "condensation_must_be_dag": True,
            },
            "edge_policy": {
                "external_kg_edges_require": "activation_formula.open_KG == true",
                "remove_kg_edges_when": "external_kg_mode == off or KG_use_score < theta_kg",
            },
            "termination_policy": {
                "k_max": 2,
                "must_emit": ["scc_manager_packet", "workflow_trace", "external_kg_decision_policy"],
                "unsafe_finalization_forbidden": True,
            },
        }
    ]


def _build_mas_role_cards() -> list[dict[str, Any]]:
    return [
        {
            "role_id": "external_kg",
            "objective": "Ground active clinical pathway evidence against CEKG and AI Patient KG criteria.",
            "allowed_actions": ["diagnosis_grounding", "provenance_attribution", "contradiction_hint", "case_packet_enrichment"],
            "forbidden_actions": FORBIDDEN_ACTIONS,
        },
        {
            "role_id": "evidence_planner",
            "objective": "Choose bounded next evidence action under active failure triggers and SCC contract state.",
            "allowed_actions": ["request_cxr", "proceed_to_assessment", "open_scc", "request_hitl"],
            "forbidden_actions": ["ignore_active_safety_stop", "skip_required_scc_artifact"],
        },
        {
            "role_id": "safety_checker",
            "objective": "Prevent unsafe autonomous finalization and enforce HITL/safety termination.",
            "allowed_actions": ["approve", "require_hitl", "safety_stop", "gate_reopen"],
            "forbidden_actions": ["approve_with_unresolved_critical_trigger"],
        },
    ]


def _build_prompt_cards() -> list[dict[str, Any]]:
    return [
        {
            "card_id": "clinical_harness_system_prompt",
            "target": "local_llm.system_prompt",
            "text": (
                "You are Sephirot(medical), an executable ontology layer for Clinical Harness. "
                "Preserve the base predictor as calibrated risk evidence. Use CEKG and AI Patient KG "
                "only as bounded criteria for grounding, contradiction, SCC routing, and safety review. "
                "Never directly override labels, future outcomes, safety stops, or HITL gates."
            ),
        },
        {
            "card_id": "scc_adjudicator_prompt",
            "target": "scc.adjudicator",
            "text": (
                "Evaluate whether active triggers justify SCC re-review, whether KG evidence is bounded, "
                "and whether termination is safe. Return schema-valid JSON only."
            ),
        },
    ]


def _build_failure_mirrors() -> list[dict[str, Any]]:
    return [
        {
            "mirror_id": "qliphoth_direct_override",
            "mirror_of": "Geburah",
            "failure_mode": "KG or MAS directly overrides the predictor label without bounded evidence.",
            "containment": "Forbid direct_label_override and preserve base score as primary calibrated evidence.",
        },
        {
            "mirror_id": "qliphoth_unbounded_loop",
            "mirror_of": "Yesod",
            "failure_mode": "SCC remains an unrestricted deliberation loop rather than a trigger-bounded contract.",
            "containment": "Require k_max, required edges, termination state, and trace artifact.",
        },
        {
            "mirror_id": "qliphoth_corpus_prior_leakage",
            "mirror_of": "Hod",
            "failure_mode": "AI Patient KG loaded status is treated as case-level evidence.",
            "containment": "Open KG only for exact, structural, or demographic case-level prior evidence.",
        },
    ]


def _load_cekg_sources(paths: Iterable[str | Path]) -> dict[str, Any]:
    source_files = _expand_input_paths(paths, suffixes=(".csv", ".csv.gz"))
    category_terms: dict[str, list[dict[str, str]]] = {rule.category: [] for rule in CLINICAL_PATHWAY_RULES}
    row_count = 0
    for path in source_files:
        for row in _iter_csv_rows(path):
            row_count += 1
            title = _row_text(row)
            norm_title = _normalize(title)
            for rule in CLINICAL_PATHWAY_RULES:
                if any(term in norm_title for term in rule.terms):
                    category_terms[rule.category].append(
                        {
                            "path": str(path),
                            "matched_field": _best_title_field(row),
                            "matched_value": title[:240],
                        }
                    )
    return {
        "loaded": bool(source_files),
        "files": [str(path) for path in source_files],
        "row_count": row_count,
        "category_counts": {category: len(items) for category, items in category_terms.items()},
        "category_terms": category_terms,
    }


def _load_aipatient_sources(paths: Iterable[str | Path]) -> dict[str, Any]:
    source_files = _expand_input_paths(paths, suffixes=(".json",))
    datasets = []
    for path in source_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        nodes = data.get("nodes", []) if isinstance(data, dict) else []
        relationships = data.get("relationships", []) if isinstance(data, dict) else []
        label_counts: dict[str, int] = {}
        for node in nodes:
            for label in node.get("labels", []):
                label_counts[label] = label_counts.get(label, 0) + 1
        datasets.append(
            {
                "dataset": path.name.replace("_KG_Export.json", "").replace(".json", "").lower(),
                "path": str(path),
                "nodes": len(nodes),
                "relationships": len(relationships),
                "top_labels": sorted(label_counts.items(), key=lambda item: item[1], reverse=True)[:10],
            }
        )
    return {
        "loaded": bool(datasets),
        "datasets": datasets,
    }


def _expand_input_paths(paths: Iterable[str | Path], *, suffixes: tuple[str, ...]) -> list[Path]:
    expanded: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            continue
        if path.is_file():
            expanded.append(path)
            continue
        for suffix in suffixes:
            expanded.extend(sorted(path.rglob(f"*{suffix}")))
    seen = set()
    result = []
    for path in expanded:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(path)
    return result


def _iter_csv_rows(path: Path) -> Iterable[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def _row_text(row: dict[str, Any]) -> str:
    for key in ("ICD_Code_Title", "title", "name", "label", "concept_name"):
        value = row.get(key)
        if value:
            return str(value)
    return " | ".join(str(value) for value in row.values() if value)


def _best_title_field(row: dict[str, Any]) -> str:
    for key in ("ICD_Code_Title", "title", "name", "label", "concept_name"):
        if row.get(key):
            return key
    return "row_text"


def _normalize(text: str) -> str:
    return " ".join(str(text).strip().lower().replace("-", " ").split())


def _agent_responsibility_for_node(node: str) -> list[str]:
    return {
        "Malkuth": ["ehr_agent", "cxr_agent", "external_scores"],
        "Yesod": ["evidence_planner", "external_kg", "gateway"],
        "Hod": ["assessment_agent", "xai_builder", "metrics_exporter"],
        "Netzach": ["trajectory_agent", "difficulty_estimator"],
        "Tiferet": ["assessment_agent", "evidence_planner"],
        "Geburah": ["safety_checker", "hitl_gate"],
        "Chesed": ["cxr_agent", "external_kg", "specialist_roster"],
        "Binah": ["external_kg", "clinical_trigger_policy"],
        "Chokmah": ["respiratory_agent", "sepsis_agent", "fluid_agent"],
        "Kether": ["clinical_harness", "scc_orchestrator", "termination_auditor"],
    }.get(node, [])


def _artifact_obligation_for_node(node: str) -> list[str]:
    return {
        "Malkuth": ["case_packet", "observed_window_evidence"],
        "Yesod": ["evidence_readiness", "kg_provenance_state"],
        "Hod": ["xai_packet", "metric_trace", "activation_formula"],
        "Netzach": ["trajectory_signal", "deterioration_trigger"],
        "Tiferet": ["assessment_packet", "integrated_rationale"],
        "Geburah": ["safety_verdict", "forbidden_action_checks"],
        "Chesed": ["escalation_decision", "opened_lanes"],
        "Binah": ["decision_criteria", "source_provenance"],
        "Chokmah": ["specialist_hypotheses"],
        "Kether": ["termination_state", "reviewable_diagnosis_or_residual_risk"],
    }.get(node, [])


def _largest_nontrivial_scc_nodes(nodes: list[str], edges: list[dict[str, Any]]) -> list[str]:
    node_set = set(str(node) for node in nodes if node)
    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        if source:
            node_set.add(source)
        if target:
            node_set.add(target)

    graph = {node: [] for node in node_set}
    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        if source and target:
            graph.setdefault(source, []).append(target)
            graph.setdefault(target, graph.get(target, []))

    index = 0
    stack: list[str] = []
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in indices:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])

        if lowlinks[node] == indices[node]:
            component = []
            while stack:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            components.append(component)

    for node in sorted(graph):
        if node not in indices:
            strongconnect(node)

    review_excluded = {"evidence_state", "decision_node"}
    nontrivial = [
        sorted(node for node in component if node not in review_excluded)
        for component in components
        if len([node for node in component if node not in review_excluded]) >= 2
    ]
    if not nontrivial:
        return []
    return max(nontrivial, key=len)
