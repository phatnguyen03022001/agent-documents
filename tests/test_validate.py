import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate.py"

CONCERNS = [
    "product.objective",
    "product.actors_roles",
    "product.features_capabilities",
    "product.scope_non_goals",
    "product.domain_external_constraints",
    "behavior.functional",
    "behavior.state_transitions",
    "behavior.invariants_permissions",
    "behavior.errors_edges_failures",
    "behavior.critical_flows",
    "behavior.acceptance",
    "behavior.safety_human_control",
    "architecture.components_ownership",
    "architecture.runtime_topology",
    "architecture.communication_boundaries",
    "architecture.technology_choices",
    "architecture.build_buy",
    "data.entities_ownership",
    "data.lifecycle_persistence",
    "data.retention_deletion",
    "data.consistency_transactions",
    "data.migration_backfill",
    "data.provenance_lineage_quality",
    "interfaces.contracts",
    "interfaces.async_jobs_commands",
    "interfaces.external_dependencies",
    "interfaces.data_exchange_trust",
    "interfaces.dependency_failure_exit",
    "quality.authentication",
    "quality.authorization_trust_boundaries",
    "quality.secrets_sensitive_operations",
    "quality.privacy_sensitive_data",
    "quality.timeouts_retries_idempotency_recovery",
    "quality.concurrency_failure_boundaries",
    "quality.performance_load_resources",
    "quality.observability",
    "quality.testing_evidence",
    "quality.cost_usage_bounds",
    "delivery.environments_config",
    "delivery.deployment_migration_rollback",
    "delivery.backup_restore",
    "delivery.compatibility_versioning_platforms",
    "delivery.operational_ownership",
    "decisions.material_choices",
    "unknowns.open_questions",
]

DOCS = {
    "PRODUCT.md": """# Product\n\n## Scope\nClosed test scope.\n\n## ACT-001 Customer\nActor.\n\n## ROL-001 Administrator\nRole.\n""",
    "BEHAVIOR.md": """# Behavior\n\n## FTR-001 Example feature\nBehavior.\n\n## FLW-001 Create account\nFlow.\n\n## ACC-001 Acceptance\nCriterion.\n""",
    "ARCHITECTURE.md": """# Architecture\n\n## SYS-001 Application\nSystem.\n\n## CAP-001 Identity\nBoundary.\n\n## CAP-001-EXIT Identity exit\nExit.\n\n## CAP-001-DEFER Deferred identity\nDeferral.\n""",
    "DATA.md": """# Data\n\n## DAT-001 Account\nData.\n""",
    "INTERFACES.md": """# Interfaces\n\n## IFC-001 Public account API\nInterface.\n\n## EXT-001 External provider\nDependency.\n""",
    "QUALITY.md": "# Quality\n",
    "DELIVERY.md": "# Delivery\n",
    "DECISIONS.md": """# Decisions\n\n## DEC-001 Primary language\nDecision.\n""",
}


def applicable(required="L1", actual="L1", rationale=""):
    return {
        "applicability": "APPLICABLE",
        "required_depth": required,
        "actual_depth": actual,
        "evidence_refs": [],
        "rationale": rationale,
    }


def minimal_catalog():
    return {
        "model_version": 1,
        "milestone": {
            "id": "M1",
            "name": "Closed milestone",
            "scope_state": "FROZEN",
            "scope_ref": "docs/PRODUCT.md#Scope",
        },
        "coverage": {key: applicable() for key in CONCERNS},
        "actors": [
            {
                "id": "ACT-001",
                "name": "Customer",
                "kind": "HUMAN",
                "doc_ref": "docs/PRODUCT.md#ACT-001",
            }
        ],
        "roles": [
            {
                "id": "ROL-001",
                "name": "Administrator",
                "actor_refs": ["ACT-001"],
                "doc_ref": "docs/PRODUCT.md#ROL-001",
            }
        ],
        "features": [
            {
                "id": "FTR-001",
                "name": "Example feature",
                "actor_refs": ["ACT-001"],
                "spec_ref": "docs/BEHAVIOR.md#FTR-001",
                "acceptance_refs": ["ACC-001"],
                "relations": {
                    "roles": {"refs": ["ROL-001"]},
                    "flows": {"refs": ["FLW-001"]},
                    "data": {"refs": ["DAT-001"]},
                    "interfaces": {"refs": ["IFC-001"]},
                    "dependencies": {"refs": ["EXT-001"]},
                    "capabilities": {"refs": ["CAP-001"]},
                },
                "decision_refs": [],
            }
        ],
        "acceptance": [
            {"id": "ACC-001", "doc_ref": "docs/BEHAVIOR.md#ACC-001"}
        ],
        "systems": [
            {
                "id": "SYS-001",
                "name": "Application",
                "doc_ref": "docs/ARCHITECTURE.md#SYS-001",
                "decision_refs": ["DEC-001"],
            }
        ],
        "data": [
            {
                "id": "DAT-001",
                "name": "Account",
                "kind": "PERSISTENT",
                "owner_system_ref": "SYS-001",
                "doc_ref": "docs/DATA.md#DAT-001",
            }
        ],
        "interfaces": [
            {
                "id": "IFC-001",
                "name": "Public account API",
                "kind": "API",
                "owner_system_ref": "SYS-001",
                "peer_refs": ["ACT-001"],
                "doc_ref": "docs/INTERFACES.md#IFC-001",
            }
        ],
        "flows": [
            {
                "id": "FLW-001",
                "name": "Create account",
                "kind": "USER",
                "critical": True,
                "doc_ref": "docs/BEHAVIOR.md#FLW-001",
                "system_refs": ["SYS-001"],
                "interface_refs": ["IFC-001"],
                "data_refs": ["DAT-001"],
                "dependency_refs": ["EXT-001"],
            }
        ],
        "dependencies": [
            {
                "id": "EXT-001",
                "name": "External provider",
                "kind": "SERVICE",
                "critical": True,
                "doc_ref": "docs/INTERFACES.md#EXT-001",
            }
        ],
        "capabilities": [
            {
                "id": "CAP-001",
                "name": "Identity",
                "status": "RESOLVED",
                "disposition": "BUY",
                "system_refs": [],
                "dependency_refs": ["EXT-001"],
                "decision_ref": "DEC-001",
                "boundary_ref": "docs/ARCHITECTURE.md#CAP-001",
                "exit": {"ref": "docs/ARCHITECTURE.md#CAP-001-EXIT"},
            }
        ],
        "decisions": [
            {
                "id": "DEC-001",
                "kind": "TECHNOLOGY",
                "subject": "Primary application language",
                "outcome": "Python 3.12",
                "reversibility": "COSTLY",
                "doc_ref": "docs/DECISIONS.md#DEC-001",
            }
        ],
        "unknowns": [],
    }


class ValidatorTests(unittest.TestCase):
    def run_case(self, mutate=None, docs_mutate=None):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            (target / "docs" / "catalog").mkdir(parents=True)
            catalog = minimal_catalog()
            if mutate:
                mutate(catalog)
            (target / "docs" / "catalog" / "project.json").write_text(
                json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
            )
            docs = copy.deepcopy(DOCS)
            if docs_mutate:
                docs_mutate(docs)
            for name, content in docs.items():
                (target / "docs" / name).write_text(content, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(target)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def assert_case(self, expected_rc, category=None, mutate=None, docs_mutate=None):
        result = self.run_case(mutate=mutate, docs_mutate=docs_mutate)
        self.assertEqual(expected_rc, result.returncode, result.stdout + result.stderr)
        expected_ready = "TRUE" if expected_rc == 0 else "FALSE"
        self.assertIn(f"DOCS_READY = {expected_ready}", result.stdout)
        if category:
            self.assertIn(f"[{category}]", result.stdout)
        return result

    def test_fully_closed_minimal_target_is_ready(self):
        self.assert_case(0)

    def test_open_scope_is_not_ready(self):
        self.assert_case(1, "SCOPE_OPEN", lambda c: c["milestone"].update(scope_state="OPEN"))

    def test_missing_coverage_key_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"].pop(CONCERNS[0]))

    def test_unsupported_coverage_key_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"].update({"extra.concern": applicable()}))

    def test_na_without_rationale_is_model_error(self):
        def mutate(c):
            c["coverage"][CONCERNS[0]] = {"applicability": "NA", "rationale": ""}
        self.assert_case(2, "MODEL_ERROR", mutate)

    def test_actual_depth_below_required_is_coverage_gap(self):
        self.assert_case(1, "COVERAGE_GAP", lambda c: c["coverage"][CONCERNS[0]].update(required_depth="L2", actual_depth="L1", rationale="Deep evidence required."))

    def test_l0_without_rationale_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"][CONCERNS[0]].update(required_depth="L0", actual_depth="L0", rationale=""))

    def test_l2_without_rationale_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"][CONCERNS[0]].update(required_depth="L2", actual_depth="L2", rationale=""))

    def test_duplicate_global_id_is_model_error(self):
        def mutate(c):
            duplicate = copy.deepcopy(c["actors"][0])
            duplicate["name"] = "Other actor"
            c["actors"].append(duplicate)
        self.assert_case(2, "MODEL_ERROR", mutate)

    def test_invalid_prefix_for_class_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["actors"][0].update(id="SYS-999"))

    def test_unknown_reference_is_reference_error(self):
        self.assert_case(2, "REFERENCE_ERROR", lambda c: c["features"][0].update(actor_refs=["ACT-999"]))

    def test_missing_feature_actor_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0].update(actor_refs=[]))

    def test_missing_feature_spec_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0].pop("spec_ref"))

    def test_missing_acceptance_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0].update(acceptance_refs=[]))

    def test_malformed_relation_state_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0]["relations"].update(roles={"refs": ["ROL-001"], "na": "bad"}))

    def test_flow_relation_must_be_subset_of_feature_interface_mapping(self):
        self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["features"][0]["relations"].update(interfaces={"na": "No direct interface."}))

    def test_orphan_entity_is_not_ready(self):
        def mutate(c):
            c["data"].append({
                "id": "DAT-002",
                "name": "Unused",
                "kind": "PERSISTENT",
                "owner_system_ref": "SYS-001",
                "doc_ref": "docs/DATA.md#DAT-002",
            })
        def docs_mutate(d):
            d["DATA.md"] += "\n## DAT-002 Unused\nUnused.\n"
        self.assert_case(1, "ORPHAN", mutate, docs_mutate)

    def test_open_cap_requires_matching_blocking_unknown(self):
        def mutate(c):
            c["capabilities"][0] = {
                "id": "CAP-001", "name": "Identity", "status": "OPEN",
                "disposition": None, "system_refs": [], "dependency_refs": [],
                "blocking_unknown_ref": "UNK-001",
            }
            c["unknowns"] = [{
                "id": "UNK-001", "kind": "QUESTION", "question": "Which identity path?",
                "affected_refs": ["FTR-001"], "affected_coverage": ["architecture.build_buy"],
                "blocking": False, "reason": "Needs exploration.",
                "resolution_phase": "IMPLEMENTATION", "status": "OPEN",
            }]
        self.assert_case(1, "BUILD_BUY_GAP", mutate)

    def test_buy_requires_dependency(self):
        self.assert_case(1, "BUILD_BUY_GAP", lambda c: c["capabilities"][0].update(dependency_refs=[]))

    def test_build_requires_system(self):
        def mutate(c):
            cap = c["capabilities"][0]
            cap.update(disposition="BUILD", system_refs=[], dependency_refs=[])
        self.assert_case(1, "BUILD_BUY_GAP", mutate)

    def test_hybrid_requires_both_sides(self):
        def mutate(c):
            cap = c["capabilities"][0]
            cap.update(disposition="HYBRID", system_refs=["SYS-001"], dependency_refs=[])
        self.assert_case(1, "BUILD_BUY_GAP", mutate)

    def test_defer_cannot_be_referenced_by_feature(self):
        def mutate(c):
            c["capabilities"][0] = {
                "id": "CAP-001", "name": "Identity", "status": "RESOLVED",
                "disposition": "DEFER", "system_refs": [], "dependency_refs": [],
                "defer_ref": "docs/ARCHITECTURE.md#CAP-001-DEFER",
            }
        self.assert_case(1, "BUILD_BUY_GAP", mutate)

    def test_open_blocking_unknown_is_not_ready(self):
        def mutate(c):
            c["unknowns"].append({
                "id": "UNK-001", "kind": "QUESTION", "question": "Open question?",
                "affected_refs": ["FTR-001"], "affected_coverage": ["architecture.technology_choices"],
                "blocking": True, "reason": "Design depends on answer.",
                "resolution_phase": "DESIGN", "status": "OPEN",
            })
        self.assert_case(1, "BLOCKING_UNKNOWN", mutate)

    def test_open_authority_conflict_is_not_ready(self):
        def mutate(c):
            c["unknowns"].append({
                "id": "UNK-001", "kind": "AUTHORITY_CONFLICT", "question": "Which authority wins?",
                "affected_refs": ["FTR-001"], "affected_coverage": [],
                "blocking": True, "reason": "Authorities conflict.",
                "resolution_phase": "DESIGN", "status": "OPEN",
            })
        self.assert_case(1, "AUTHORITY_CONFLICT", mutate)

    def test_open_contradiction_is_not_ready(self):
        def mutate(c):
            c["unknowns"].append({
                "id": "UNK-001", "kind": "CONTRADICTION", "question": "Which statement is true?",
                "affected_refs": ["FTR-001"], "affected_coverage": [],
                "blocking": True, "reason": "Statements conflict.",
                "resolution_phase": "DESIGN", "status": "OPEN",
            })
        self.assert_case(1, "RESOLUTION_GAP", mutate)

    def test_decision_required_resolution_must_point_to_decision(self):
        def mutate(c):
            c["unknowns"].append({
                "id": "UNK-001", "kind": "DECISION_REQUIRED", "question": "Choose path?",
                "affected_refs": ["FTR-001"], "affected_coverage": [],
                "blocking": False, "reason": "Choice required.",
                "resolution_phase": "DESIGN", "status": "RESOLVED",
                "resolved_by_ref": "FTR-001",
            })
        self.assert_case(2, "REFERENCE_ERROR", mutate)

    def test_actor_inventory_contradicts_na_actor_coverage(self):
        self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"product.actors_roles": {"applicability": "NA", "rationale": "No actors."}}))

    def test_cap_inventory_contradicts_na_build_buy_coverage(self):
        self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"architecture.build_buy": {"applicability": "NA", "rationale": "No capabilities."}}))

    def test_dependency_inventory_contradicts_na_external_dependency_coverage(self):
        self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"interfaces.external_dependencies": {"applicability": "NA", "rationale": "No dependencies."}}))

    def test_decision_inventory_contradicts_na_decisions_coverage(self):
        self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"decisions.material_choices": {"applicability": "NA", "rationale": "No decisions."}}))

    def test_unknown_inventory_contradicts_na_unknown_coverage(self):
        def mutate(c):
            c["unknowns"].append({
                "id": "UNK-001", "kind": "QUESTION", "question": "Historical question?",
                "affected_refs": ["FTR-001"], "affected_coverage": [],
                "blocking": False, "reason": "Resolved for record.",
                "resolution_phase": "DESIGN", "status": "RESOLVED",
                "resolved_by_ref": "DEC-001",
            })
            c["coverage"]["unknowns.open_questions"] = {"applicability": "NA", "rationale": "No unknowns."}
        self.assert_case(1, "TRACEABILITY_GAP", mutate)

    def test_missing_referenced_markdown_heading_is_reference_error(self):
        def docs_mutate(d):
            d["PRODUCT.md"] = d["PRODUCT.md"].replace("## ACT-001 Customer\nActor.\n\n", "")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=docs_mutate)

    def test_unsupported_model_version_is_model_error(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c.update(model_version=2))

    def test_invalid_document_path_is_reference_error(self):
        self.assert_case(2, "REFERENCE_ERROR", lambda c: c["actors"][0].update(doc_ref="docs/OTHER.md#ACT-001"))

    def test_applicable_none_is_coverage_gap(self):
        self.assert_case(1, "COVERAGE_GAP", lambda c: c["coverage"][CONCERNS[0]].update(actual_depth="NONE"))


if __name__ == "__main__":
    unittest.main()
