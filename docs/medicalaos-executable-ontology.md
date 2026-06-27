# Sephirot-MedicalAOS Executable Ontology Direction

This fork adapts Sephirot for MedicalAOS without modifying the upstream Sephirot repository.

The goal is not to replace CEKG or AI Patient KG. Those remain source knowledge graphs. The goal is to compile them into an executable ontology that MedicalAOS can use as runtime judgment criteria for Clinical Harness and SCC orchestration.

For the medical domain, the ascent from Malkuth to Kether is the process of making a clear, reviewable patient diagnosis or a bounded residual-risk termination. The agents must care about all 10 Sephirot nodes and all 22 paths. If a node or path is neglected, the corresponding Qliphoth failure appears: unsupported evidence, false readiness, poisoned metrics, unsafe control, over-expansion, hidden leakage, or an unreviewable final answer.

## Role

Sephirot-MedicalAOS should produce machine-readable artifacts:

- diagnostic ascent contract for 10 nodes and 22 paths
- KG activation formula
- KG decision criteria
- allowed and forbidden KG actions
- clinical failure regime mappings
- SCC cycle ontology
- SCC contract templates
- system prompt cards for local LLM roles
- Qliphoth-style failure mirrors for audit
- per-case Sephirot execution graph artifacts produced by MedicalAOS

## MedicalAOS Claim

CEKG and AI Patient KG are not LLM control ontologies by themselves. Sephirot-MedicalAOS converts their concepts and patient/admission structures into bounded rules:

```text
open_KG = 1[mode in {advisory, control}] and KG_use_score >= theta_kg

KG_use_score =
  max(CEKG_pathway_score, raw_diagnosis_hint_score)
  + provenance_score
  + AI_Patient_case_prior_score
```

The compiled ontology may support diagnosis grounding, provenance attribution, contradiction hints, imaging escalation support, bounded risk floors, and case packet enrichment. It must not directly override labels, use future outcome fields, or override safety/HITL gates.

## SCC in Sephirot

SCC is a first-class Sephirot(medical) structure, not just a MedicalAOS implementation detail.

In this fork, SCC means a local strongly connected component over the agent role-interaction graph. It opens only when direct finalization is unsafe, a single review lane is insufficient, mutual revision among at least two review agents is required, and budget remains.

```text
open_SCC =
  direct_finalization_unsafe
  and mutual_revision_required
  and single_lane_insufficient
  and budget_available
```

The compiled ontology emits:

- SCC opening criteria
- role-interaction required edges
- non-trivial SCC witness rules
- condensation-to-DAG requirements
- forbidden edges such as KG-only label override or future-outcome leakage
- Qliphoth failure mirrors for unbounded loops, fullmesh expansion, and acyclic review mislabeled as SCC

Sephirot projection:

| Sephirot slot | SCC executable meaning |
| --- | --- |
| Malkuth | observed patient evidence and runtime trace |
| Yesod | SCC contract, required edges, and budget interface |
| Hod | Tarjan witness, edge coverage, trace metrics |
| Netzach | bounded re-entry and convergence pressure |
| Tiferet | integrated clinical judgment after mutual revision |
| Geburah | safety gate, forbidden edges, HITL escalation |
| Chesed | controlled specialist expansion |
| Binah | clinical criteria and provenance boundaries |
| Chokmah | alternative deterioration hypotheses |
| Kether | reviewable termination state |

## Diagnostic Ascent Contract

The global graph is a diagnostic DAG:

```text
Malkuth -> ... -> Kether
```

Its meaning is:

- Malkuth: material patient evidence.
- Kether: clear diagnosis or bounded residual-risk termination.
- 10 nodes: clinical obligations that must not be skipped.
- 22 paths: competency-question transitions that agents must traverse.
- Qliphoth: the failure state that appears when a node/path is ignored or simulated.

The important graph-theoretic move is that local SCC cycles live inside this ascent. The global diagnostic process remains auditable as a DAG after condensation, while failure-triggered local regions become SCCs where agents mutually challenge and revise each other.

So the structure is not:

```text
one linear diagnosis chain
```

It is:

```text
diagnostic DAG + local trigger-bounded SCC cycles + condensation back to DAG
```

That is why SCC belongs in Sephirot rather than being a side mechanism in MedicalAOS.

## Per-Case Execution Graph

The compiler emits the ontology. MedicalAOS, as Sephirot(medical), then emits a patient-level execution graph:

```text
sephirot_execution_graph.json
```

This artifact materializes:

- the 10 Sephirot diagnostic nodes
- the 22 competency-question paths
- observed MAS agents
- Clinical Harness triggers
- matched compiled KG criteria
- SCC graph-theory evidence
- workflow and knowledge-graph artifacts
- coverage over the diagnostic ascent
- Qliphoth risks for every uncovered node/path

This matters because not every run should claim full ascent. A direct single-model path can emit a low-coverage graph with Qliphoth risks, while a trigger-aware MAS/SCC path should cover more of the ascent and expose local SCC cycles when needed.

## Minimum Fork Tasks

Implemented minimum:

1. `sephirot.medicalaos` compiler module.
2. CEKG CSV/CSV.GZ and AI Patient KG JSON readers.
3. Executable ontology JSON generation.
4. Validation for source provenance, allowed actions, forbidden actions, bounded effects, 10 nodes, 22 paths, and non-trivial SCC contract witnesses.
5. Prompt cards, MAS role cards, SCC cycle ontology, SCC contract templates, and Qliphoth failure mirrors.
6. Unit tests with synthetic CEKG and AI Patient KG fixtures.

CLI:

```bash
sephirot compile-medicalaos \
  --cekg /path/to/G_ICD.csv.gz \
  --aipatient /path/to/CORAL_KG_Export.json \
  --aipatient /path/to/MIMICIII_KG_Export.json \
  --out sephirot_medical_ontology.json
```

## Paper Position

Use this fork as an engineering contribution only when MedicalAOS consumes its outputs in runtime artifacts. Avoid presenting Sephirot as a decorative ontology layer.
