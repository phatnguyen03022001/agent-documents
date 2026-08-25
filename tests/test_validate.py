import copy
import json
import contextlib
import importlib.util
import io
import types
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate.py"
spec = importlib.util.spec_from_file_location("agent_documents_validate", VALIDATOR)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

CONCERNS = [
    "product.objective", "product.actors_roles", "product.features_capabilities",
    "product.scope_non_goals", "product.domain_external_constraints",
    "behavior.functional", "behavior.state_transitions", "behavior.invariants_permissions",
    "behavior.errors_edges_failures", "behavior.critical_flows", "behavior.acceptance",
    "behavior.safety_human_control", "architecture.components_ownership",
    "architecture.runtime_topology", "architecture.communication_boundaries",
    "architecture.technology_choices", "architecture.build_buy", "data.entities_ownership",
    "data.lifecycle_persistence", "data.retention_deletion", "data.consistency_transactions",
    "data.migration_backfill", "data.provenance_lineage_quality", "interfaces.contracts",
    "interfaces.async_jobs_commands", "interfaces.external_dependencies",
    "interfaces.data_exchange_trust", "interfaces.dependency_failure_exit",
    "quality.authentication", "quality.authorization_trust_boundaries",
    "quality.secrets_sensitive_operations", "quality.privacy_sensitive_data",
    "quality.timeouts_retries_idempotency_recovery", "quality.concurrency_failure_boundaries",
    "quality.performance_load_resources", "quality.observability", "quality.testing_evidence",
    "quality.cost_usage_bounds", "delivery.environments_config",
    "delivery.deployment_migration_rollback", "delivery.backup_restore",
    "delivery.compatibility_versioning_platforms", "delivery.operational_ownership",
    "decisions.material_choices", "unknowns.open_questions",
]

DOMAIN = {}
for concern in CONCERNS:
    prefix = concern.split(".", 1)[0]
    DOMAIN[concern] = {
        "product": "PRODUCT", "behavior": "BEHAVIOR", "architecture": "ARCHITECTURE",
        "data": "DATA", "interfaces": "INTERFACES", "quality": "QUALITY",
        "delivery": "DELIVERY", "decisions": "DECISIONS", "unknowns": "DECISIONS",
    }[prefix]

ROOT_TOKEN = {
    "PRODUCT": "Product", "BEHAVIOR": "Behavior", "ARCHITECTURE": "Architecture",
    "DATA": "Data", "INTERFACES": "Interfaces", "QUALITY": "Quality",
    "DELIVERY": "Delivery", "DECISIONS": "Decisions",
}

DOCS = {
    "PRODUCT.md": """# Product\nProduct support.\n\n## Scope\nClosed test scope.\n\n## ACT-001 Customer\nActor.\n\n## ROL-001 Administrator\nRole.\n""",
    "BEHAVIOR.md": """# Behavior\nBehavior support.\n\n## FTR-001 Example feature\nBehavior.\n\n## FLW-001 Create account\nFlow.\n\n## ACC-001 Acceptance\nCriterion.\n""",
    "ARCHITECTURE.md": """# Architecture\nArchitecture support.\n\n## SYS-001 Application\nSystem.\n\n## CAP-001 Identity\nBoundary.\n\n## CAP-001-EXIT Identity exit\nExit.\n\n## CAP-001-DEFER Deferred identity\nDeferral.\n""",
    "DATA.md": """# Data\nData support.\n\n## DAT-001 Account\nData.\n""",
    "INTERFACES.md": """# Interfaces\nInterface support.\n\n## IFC-001 Public account API\nInterface.\n\n## EXT-001 External provider\nDependency.\n""",
    "QUALITY.md": "# Quality\nQuality support.\n",
    "DELIVERY.md": "# Delivery\nDelivery support.\n",
    "DECISIONS.md": """# Decisions\nDecision support.\n\n## DEC-001 Primary language\nDecision.\n""",
}


def support_ref(concern):
    domain = DOMAIN[concern]
    return f"docs/{domain}.md#{ROOT_TOKEN[domain]}"


def applicable(required="L1", actual="L1", rationale="", refs=None):
    if refs is None:
        refs = [] if actual == "NONE" else ["__AUTO__"]
    return {
        "applicability": "APPLICABLE",
        "required_depth": required,
        "actual_depth": actual,
        "support_refs": refs,
        "rationale": rationale,
    }


def minimal_catalog():
    coverage = {}
    for key in CONCERNS:
        entry = applicable()
        entry["support_refs"] = [support_ref(key)]
        coverage[key] = entry
    return {
        "model_version": 1,
        "milestone": {
            "id": "M1", "name": "Closed milestone", "scope_state": "FROZEN",
            "scope_ref": "docs/PRODUCT.md#Scope", "root_refs": [],
        },
        "coverage": coverage,
        "actors": [{"id": "ACT-001", "name": "Customer", "kind": "HUMAN", "doc_ref": "docs/PRODUCT.md#ACT-001"}],
        "roles": [{"id": "ROL-001", "name": "Administrator", "actor_refs": ["ACT-001"], "doc_ref": "docs/PRODUCT.md#ROL-001"}],
        "features": [{
            "id": "FTR-001", "name": "Example feature", "actor_refs": ["ACT-001"],
            "spec_ref": "docs/BEHAVIOR.md#FTR-001", "acceptance_refs": ["ACC-001"],
            "relations": {
                "roles": {"refs": ["ROL-001"]}, "flows": {"refs": ["FLW-001"]},
                "data": {"refs": ["DAT-001"]}, "interfaces": {"refs": ["IFC-001"]},
                "dependencies": {"refs": ["EXT-001"]}, "capabilities": {"refs": ["CAP-001"]},
            },
            "decision_refs": [],
        }],
        "acceptance": [{"id": "ACC-001", "doc_ref": "docs/BEHAVIOR.md#ACC-001"}],
        "systems": [{"id": "SYS-001", "name": "Application", "doc_ref": "docs/ARCHITECTURE.md#SYS-001", "decision_refs": ["DEC-001"]}],
        "data": [{"id": "DAT-001", "name": "Account", "kind": "PERSISTENT", "owner_system_ref": "SYS-001", "doc_ref": "docs/DATA.md#DAT-001"}],
        "interfaces": [{"id": "IFC-001", "name": "Public account API", "kind": "API", "owner_system_ref": "SYS-001", "peer_refs": ["ACT-001"], "doc_ref": "docs/INTERFACES.md#IFC-001"}],
        "flows": [{"id": "FLW-001", "name": "Create account", "kind": "USER", "critical": True, "doc_ref": "docs/BEHAVIOR.md#FLW-001", "system_refs": ["SYS-001"], "interface_refs": ["IFC-001"], "data_refs": ["DAT-001"], "dependency_refs": ["EXT-001"]}],
        "dependencies": [{"id": "EXT-001", "name": "External provider", "kind": "SERVICE", "critical": True, "doc_ref": "docs/INTERFACES.md#EXT-001"}],
        "capabilities": [{
            "id": "CAP-001", "name": "Identity", "status": "RESOLVED", "disposition": "BUY",
            "system_refs": [], "dependency_refs": ["EXT-001"], "decision_ref": "DEC-001",
            "boundary_ref": "docs/ARCHITECTURE.md#CAP-001",
            "exit": {"ref": "docs/ARCHITECTURE.md#CAP-001-EXIT"},
        }],
        "decisions": [{"id": "DEC-001", "kind": "TECHNOLOGY", "subject": "Primary application language", "outcome": "Python 3.12", "reversibility": "COSTLY", "doc_ref": "docs/DECISIONS.md#DEC-001"}],
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
            (target / "docs" / "catalog" / "project.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
            docs = copy.deepcopy(DOCS)
            if docs_mutate:
                docs_mutate(docs)
            for name, content in docs.items():
                path = target / "docs" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                returncode = validator.main([str(target)])
            return types.SimpleNamespace(returncode=returncode, stdout=output.getvalue(), stderr="")

    def assert_case(self, expected_rc, category=None, mutate=None, docs_mutate=None, contains=None):
        result = self.run_case(mutate=mutate, docs_mutate=docs_mutate)
        self.assertEqual(expected_rc, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"DOCS_READY = {'TRUE' if expected_rc == 0 else 'FALSE'}", result.stdout)
        if category:
            self.assertIn(f"[{category}]", result.stdout)
        if contains:
            self.assertIn(contains, result.stdout)
        return result

    # Revision-1 invariants remain mandatory.
    def test_fully_closed_minimal_target_is_ready(self): self.assert_case(0)
    def test_open_scope_is_not_ready(self): self.assert_case(1, "SCOPE_OPEN", lambda c: c["milestone"].update(scope_state="OPEN"))
    def test_missing_coverage_key_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"].pop(CONCERNS[0]))
    def test_unsupported_coverage_key_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"].update({"extra.concern": applicable(refs=["docs/PRODUCT.md#Product"])}))
    def test_na_without_rationale_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"].update({CONCERNS[0]: {"applicability": "NA", "rationale": ""}}))
    def test_actual_depth_below_required_is_coverage_gap(self): self.assert_case(1, "COVERAGE_GAP", lambda c: c["coverage"][CONCERNS[0]].update(required_depth="L2", actual_depth="L1", rationale="Deep evidence required."))
    def test_l0_without_rationale_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"][CONCERNS[0]].update(required_depth="L0", actual_depth="L0", rationale=""))
    def test_l2_without_rationale_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"][CONCERNS[0]].update(required_depth="L2", actual_depth="L2", rationale=""))

    def test_duplicate_global_id_is_model_error(self):
        def mutate(c):
            duplicate = copy.deepcopy(c["actors"][0]); duplicate["name"] = "Other actor"; c["actors"].append(duplicate)
        self.assert_case(2, "MODEL_ERROR", mutate)

    def test_invalid_prefix_for_class_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["actors"][0].update(id="SYS-999"))
    def test_unknown_reference_is_reference_error(self): self.assert_case(2, "REFERENCE_ERROR", lambda c: c["features"][0].update(actor_refs=["ACT-999"]))
    def test_missing_feature_actor_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0].update(actor_refs=[]))
    def test_missing_feature_spec_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0].pop("spec_ref"))
    def test_missing_acceptance_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0].update(acceptance_refs=[]))
    def test_malformed_relation_state_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["features"][0]["relations"].update(roles={"refs": ["ROL-001"], "na": "bad"}))
    def test_flow_relation_must_be_subset_of_feature_interface_mapping(self): self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["features"][0]["relations"].update(interfaces={"na": "No direct interface."}))

    def test_orphan_entity_is_not_ready(self):
        def mutate(c): c["data"].append({"id": "DAT-002", "name": "Unused", "kind": "PERSISTENT", "owner_system_ref": "SYS-001", "doc_ref": "docs/DATA.md#DAT-002"})
        def docs_mutate(d): d["DATA.md"] += "\n## DAT-002 Unused\nUnused.\n"
        self.assert_case(1, "ORPHAN", mutate, docs_mutate)

    def test_open_cap_requires_matching_blocking_unknown(self):
        def mutate(c):
            c["capabilities"][0] = {"id": "CAP-001", "name": "Identity", "status": "OPEN", "disposition": None, "system_refs": [], "dependency_refs": [], "blocking_unknown_ref": "UNK-001"}
            c["unknowns"] = [{"id": "UNK-001", "kind": "QUESTION", "question": "Which identity path?", "affected_refs": ["FTR-001"], "affected_coverage": ["architecture.build_buy"], "blocking": False, "reason": "Needs exploration.", "resolution_phase": "IMPLEMENTATION", "status": "OPEN"}]
        self.assert_case(1, "BUILD_BUY_GAP", mutate)

    def test_buy_requires_dependency(self): self.assert_case(1, "BUILD_BUY_GAP", lambda c: c["capabilities"][0].update(dependency_refs=[]))
    def test_build_requires_system(self): self.assert_case(1, "BUILD_BUY_GAP", lambda c: c["capabilities"][0].update(disposition="BUILD", system_refs=[], dependency_refs=[]))
    def test_hybrid_requires_both_sides(self): self.assert_case(1, "BUILD_BUY_GAP", lambda c: c["capabilities"][0].update(disposition="HYBRID", system_refs=["SYS-001"], dependency_refs=[]))

    def test_defer_cannot_be_referenced_by_feature(self):
        def mutate(c): c["capabilities"][0] = {"id": "CAP-001", "name": "Identity", "status": "RESOLVED", "disposition": "DEFER", "system_refs": [], "dependency_refs": [], "defer_ref": "docs/ARCHITECTURE.md#CAP-001-DEFER"}
        self.assert_case(1, "BUILD_BUY_GAP", mutate)

    def test_open_blocking_unknown_is_not_ready(self):
        def mutate(c): c["unknowns"].append({"id": "UNK-001", "kind": "QUESTION", "question": "Open question?", "affected_refs": ["FTR-001"], "affected_coverage": ["architecture.technology_choices"], "blocking": True, "reason": "Design depends on answer.", "resolution_phase": "DESIGN", "status": "OPEN"})
        self.assert_case(1, "BLOCKING_UNKNOWN", mutate)

    def test_open_authority_conflict_is_not_ready(self):
        def mutate(c): c["unknowns"].append({"id": "UNK-001", "kind": "AUTHORITY_CONFLICT", "question": "Which authority wins?", "affected_refs": ["FTR-001"], "affected_coverage": [], "blocking": True, "reason": "Authorities conflict.", "resolution_phase": "DESIGN", "status": "OPEN"})
        self.assert_case(1, "AUTHORITY_CONFLICT", mutate)

    def test_open_contradiction_is_not_ready(self):
        def mutate(c): c["unknowns"].append({"id": "UNK-001", "kind": "CONTRADICTION", "question": "Which statement is true?", "affected_refs": ["FTR-001"], "affected_coverage": [], "blocking": True, "reason": "Statements conflict.", "resolution_phase": "DESIGN", "status": "OPEN"})
        self.assert_case(1, "RESOLUTION_GAP", mutate)

    def test_decision_required_resolution_must_point_to_decision(self):
        def mutate(c): c["unknowns"].append({"id": "UNK-001", "kind": "DECISION_REQUIRED", "question": "Choose path?", "affected_refs": ["FTR-001"], "affected_coverage": [], "blocking": False, "reason": "Choice required.", "resolution_phase": "DESIGN", "status": "RESOLVED", "resolved_by_ref": "FTR-001"})
        self.assert_case(2, "REFERENCE_ERROR", mutate)

    def test_actor_inventory_contradicts_na_actor_coverage(self): self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"product.actors_roles": {"applicability": "NA", "rationale": "No actors."}}))
    def test_cap_inventory_contradicts_na_build_buy_coverage(self): self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"architecture.build_buy": {"applicability": "NA", "rationale": "No capabilities."}}))
    def test_dependency_inventory_contradicts_na_external_dependency_coverage(self): self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"interfaces.external_dependencies": {"applicability": "NA", "rationale": "No dependencies."}}))
    def test_decision_inventory_contradicts_na_decisions_coverage(self): self.assert_case(1, "TRACEABILITY_GAP", lambda c: c["coverage"].update({"decisions.material_choices": {"applicability": "NA", "rationale": "No decisions."}}))

    def test_unknown_inventory_contradicts_na_unknown_coverage(self):
        def mutate(c):
            c["unknowns"].append({"id": "UNK-001", "kind": "QUESTION", "question": "Historical question?", "affected_refs": ["FTR-001"], "affected_coverage": [], "blocking": False, "reason": "Resolved for record.", "resolution_phase": "DESIGN", "status": "RESOLVED", "resolved_by_ref": "DEC-001"})
            c["coverage"]["unknowns.open_questions"] = {"applicability": "NA", "rationale": "No unknowns."}
        self.assert_case(1, "TRACEABILITY_GAP", mutate)

    def test_missing_referenced_markdown_heading_is_reference_error(self):
        def docs_mutate(d): d["PRODUCT.md"] = d["PRODUCT.md"].replace("## ACT-001 Customer\nActor.\n\n", "")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=docs_mutate)

    def test_unsupported_model_version_is_model_error(self): self.assert_case(2, "MODEL_ERROR", lambda c: c.update(model_version=2))
    def test_invalid_document_path_is_reference_error(self): self.assert_case(2, "REFERENCE_ERROR", lambda c: c["actors"][0].update(doc_ref="docs/OTHER.md#ACT-001"))
    def test_applicable_none_is_coverage_gap(self): self.assert_case(1, "COVERAGE_GAP", lambda c: c["coverage"][CONCERNS[0]].update(actual_depth="NONE", support_refs=[]))

    # H1: structural support linkage.
    def test_resolved_depth_requires_support_ref(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"][CONCERNS[0]].update(support_refs=[]))
    def test_none_depth_forbids_support_ref(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"][CONCERNS[0]].update(actual_depth="NONE"))
    def test_support_ref_must_match_authority_domain(self): self.assert_case(2, "REFERENCE_ERROR", lambda c: c["coverage"]["product.objective"].update(support_refs=["docs/BEHAVIOR.md#Behavior"]))

    def _dedicated_support(self, body):
        def mutate(c): c["coverage"]["product.objective"].update(support_refs=["docs/PRODUCT.md#ObjectiveSupport"])
        def docs_mutate(d): d["PRODUCT.md"] += "\n## ObjectiveSupport\n" + body
        return mutate, docs_mutate

    def test_heading_only_support_section_does_not_establish_support(self):
        m, d = self._dedicated_support("")
        self.assert_case(1, "COVERAGE_GAP", m, d)

    def test_whitespace_only_support_section_does_not_establish_support(self):
        m, d = self._dedicated_support("   \n\t\n")
        self.assert_case(1, "COVERAGE_GAP", m, d)

    def test_html_comment_only_support_section_does_not_establish_support(self):
        m, d = self._dedicated_support("<!-- hidden support -->\n<!--\nmultiline\n-->\n")
        self.assert_case(1, "COVERAGE_GAP", m, d)

    def test_real_content_line_establishes_support(self):
        m, d = self._dedicated_support("A material objective is described here.\n")
        self.assert_case(0, mutate=m, docs_mutate=d)

    # H2: eight authority domains with optional one-level physical shards.
    def test_root_document_reference_remains_valid(self): self.assert_case(0)

    def test_one_level_support_shard_is_valid(self):
        def mutate(c): c["coverage"]["product.objective"].update(support_refs=["docs/product/objective.md#Objective"])
        def docs_mutate(d): d["product/objective.md"] = "# Objective\nObjective support.\n"
        self.assert_case(0, mutate=mutate, docs_mutate=docs_mutate)

    def test_one_level_entity_shard_is_valid(self):
        def mutate(c): c["data"][0]["doc_ref"] = "docs/data/account.md#DAT-001"
        def docs_mutate(d): d["data/account.md"] = "# DAT-001 Account\nAccount semantics.\n"
        self.assert_case(0, mutate=mutate, docs_mutate=docs_mutate)

    def test_entity_ref_wrong_authority_domain_fails(self): self.assert_case(2, "REFERENCE_ERROR", lambda c: c["data"][0].update(doc_ref="docs/architecture/account.md#DAT-001"))
    def test_nested_support_shard_fails(self): self.assert_case(2, "REFERENCE_ERROR", lambda c: c["coverage"]["product.objective"].update(support_refs=["docs/product/nested/objective.md#Objective"]))
    def test_nested_entity_shard_fails(self): self.assert_case(2, "REFERENCE_ERROR", lambda c: c["data"][0].update(doc_ref="docs/data/nested/account.md#DAT-001"))

    # H3: explicit roots and directed reachability.
    def test_explicit_root_makes_cross_cutting_entity_reachable(self):
        def mutate(c):
            c["data"].append({"id": "DAT-002", "name": "Audit record", "kind": "PERSISTENT", "owner_system_ref": "SYS-001", "doc_ref": "docs/DATA.md#DAT-002"})
            c["milestone"]["root_refs"] = ["DAT-002"]
        def docs_mutate(d): d["DATA.md"] += "\n## DAT-002 Audit record\nCross-cutting data.\n"
        self.assert_case(0, mutate=mutate, docs_mutate=docs_mutate)

    def test_unknown_root_ref_fails(self): self.assert_case(2, "REFERENCE_ERROR", lambda c: c["milestone"].update(root_refs=["DAT-999"]))
    def test_feature_root_ref_is_forbidden(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["milestone"].update(root_refs=["FTR-001"]))

    def test_unknown_record_root_ref_is_forbidden(self):
        def mutate(c):
            c["unknowns"].append({"id": "UNK-001", "kind": "QUESTION", "question": "Historical?", "affected_refs": ["FTR-001"], "affected_coverage": [], "blocking": False, "reason": "Recorded.", "resolution_phase": "DESIGN", "status": "RESOLVED", "resolved_by_ref": "DEC-001"})
            c["milestone"]["root_refs"] = ["UNK-001"]
        self.assert_case(2, "MODEL_ERROR", mutate)

    def test_duplicate_root_refs_fail(self): self.assert_case(2, "MODEL_ERROR", lambda c: c["milestone"].update(root_refs=["DAT-001", "DAT-001"]))

    def test_defer_capability_cannot_be_root(self):
        def mutate(c):
            c["features"][0]["relations"]["capabilities"] = {"na": "Capability deferred beyond this milestone."}
            c["capabilities"][0] = {"id": "CAP-001", "name": "Identity", "status": "RESOLVED", "disposition": "DEFER", "system_refs": [], "dependency_refs": [], "defer_ref": "docs/ARCHITECTURE.md#CAP-001-DEFER"}
            c["milestone"]["root_refs"] = ["CAP-001"]
        self.assert_case(2, "MODEL_ERROR", mutate)

    def test_disconnected_referenced_cluster_remains_orphaned(self):
        def mutate(c):
            c["systems"].append({"id": "SYS-002", "name": "Detached system", "doc_ref": "docs/ARCHITECTURE.md#SYS-002", "decision_refs": ["DEC-002"]})
            c["decisions"].append({"id": "DEC-002", "kind": "ARCHITECTURE", "subject": "Detached choice", "outcome": "Detached", "reversibility": "REVERSIBLE", "doc_ref": "docs/DECISIONS.md#DEC-002"})
            c["data"].append({"id": "DAT-002", "name": "Detached data", "kind": "PERSISTENT", "owner_system_ref": "SYS-002", "doc_ref": "docs/DATA.md#DAT-002"})
        def docs_mutate(d):
            d["ARCHITECTURE.md"] += "\n## SYS-002 Detached system\nDetached.\n"
            d["DECISIONS.md"] += "\n## DEC-002 Detached choice\nDetached.\n"
            d["DATA.md"] += "\n## DAT-002 Detached data\nDetached.\n"
        result = self.assert_case(1, "ORPHAN", mutate, docs_mutate)
        self.assertIn("SYS-002", result.stdout)
        self.assertIn("DAT-002", result.stdout)
        self.assertIn("DEC-002", result.stdout)

    # Revision-3 false-green regressions.
    def test_fenced_heading_does_not_satisfy_reference(self):
        def docs_mutate(d): d["PRODUCT.md"] = d["PRODUCT.md"].replace("## ACT-001 Customer\nActor.\n", "```md\n## ACT-001 Customer\n```\n")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=docs_mutate, contains="ACT-001.doc_ref")

    def test_html_commented_heading_does_not_satisfy_reference(self):
        def docs_mutate(d): d["PRODUCT.md"] = d["PRODUCT.md"].replace("## ACT-001 Customer\nActor.\n", "<!--\n## ACT-001 Customer\n-->\n")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=docs_mutate, contains="ACT-001.doc_ref")

    def test_duplicate_heading_token_is_reference_error(self):
        def docs_mutate(d): d["PRODUCT.md"] += "\n## ACT-001 Duplicate\nOther actor text.\n"
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=docs_mutate, contains="matches multiple canonical headings")

    def test_scope_ref_requires_structural_content(self):
        def docs_mutate(d): d["PRODUCT.md"] = d["PRODUCT.md"].replace("## Scope\nClosed test scope.\n", "## Scope\n<!-- hidden -->\n")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=docs_mutate, contains="milestone.scope_ref")

    def test_all_entity_doc_refs_require_structural_content(self):
        cases = [
            ("PRODUCT.md", "## ACT-001 Customer\nActor.\n", "## ACT-001 Customer\n<!-- hidden -->\n", "ACT-001.doc_ref"),
            ("PRODUCT.md", "## ROL-001 Administrator\nRole.\n", "## ROL-001 Administrator\n<!-- hidden -->\n", "ROL-001.doc_ref"),
            ("BEHAVIOR.md", "## ACC-001 Acceptance\nCriterion.\n", "## ACC-001 Acceptance\n<!-- hidden -->\n", "ACC-001.doc_ref"),
            ("ARCHITECTURE.md", "## SYS-001 Application\nSystem.\n", "## SYS-001 Application\n<!-- hidden -->\n", "SYS-001.doc_ref"),
            ("DATA.md", "## DAT-001 Account\nData.\n", "## DAT-001 Account\n<!-- hidden -->\n", "DAT-001.doc_ref"),
            ("INTERFACES.md", "## IFC-001 Public account API\nInterface.\n", "## IFC-001 Public account API\n<!-- hidden -->\n", "IFC-001.doc_ref"),
            ("BEHAVIOR.md", "## FLW-001 Create account\nFlow.\n", "## FLW-001 Create account\n<!-- hidden -->\n", "FLW-001.doc_ref"),
            ("INTERFACES.md", "## EXT-001 External provider\nDependency.\n", "## EXT-001 External provider\n<!-- hidden -->\n", "EXT-001.doc_ref"),
            ("DECISIONS.md", "## DEC-001 Primary language\nDecision.\n", "## DEC-001 Primary language\n<!-- hidden -->\n", "DEC-001.doc_ref"),
        ]
        for filename, before, after, ref_label in cases:
            with self.subTest(ref_label=ref_label):
                def docs_mutate(d, filename=filename, before=before, after=after): d[filename] = d[filename].replace(before, after)
                self.assert_case(1, "REFERENCE_ERROR", docs_mutate=docs_mutate, contains=ref_label)

    def test_spec_boundary_exit_and_defer_refs_require_structural_content(self):
        def spec_docs(d): d["BEHAVIOR.md"] = d["BEHAVIOR.md"].replace("## FTR-001 Example feature\nBehavior.\n", "## FTR-001 Example feature\n<!-- hidden -->\n")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=spec_docs, contains="FTR-001.spec_ref")

        def boundary_docs(d): d["ARCHITECTURE.md"] = d["ARCHITECTURE.md"].replace("## CAP-001 Identity\nBoundary.\n", "## CAP-001 Identity\n<!-- hidden -->\n")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=boundary_docs, contains="CAP-001.boundary_ref")

        def exit_docs(d): d["ARCHITECTURE.md"] = d["ARCHITECTURE.md"].replace("## CAP-001-EXIT Identity exit\nExit.\n", "## CAP-001-EXIT Identity exit\n<!-- hidden -->\n")
        self.assert_case(1, "REFERENCE_ERROR", docs_mutate=exit_docs, contains="CAP-001.exit.ref")

        def defer_mutate(c):
            c["features"][0]["relations"]["capabilities"] = {"na": "Capability deferred beyond this milestone."}
            c["capabilities"][0] = {"id": "CAP-001", "name": "Identity", "status": "RESOLVED", "disposition": "DEFER", "system_refs": [], "dependency_refs": [], "defer_ref": "docs/ARCHITECTURE.md#CAP-001-DEFER"}
        def defer_docs(d): d["ARCHITECTURE.md"] = d["ARCHITECTURE.md"].replace("## CAP-001-DEFER Deferred identity\nDeferral.\n", "## CAP-001-DEFER Deferred identity\n<!-- hidden -->\n")
        self.assert_case(1, "REFERENCE_ERROR", mutate=defer_mutate, docs_mutate=defer_docs, contains="CAP-001.defer_ref")

    def test_minimal_non_comment_content_satisfies_canonical_reference(self):
        def docs_mutate(d): d["PRODUCT.md"] = d["PRODUCT.md"].replace("## Scope\nClosed test scope.\n", "## Scope\nx\n")
        self.assert_case(0, docs_mutate=docs_mutate)

    def test_open_design_decision_required_must_be_blocking(self):
        def mutate(c): c["unknowns"].append({"id": "UNK-001", "kind": "DECISION_REQUIRED", "question": "Choose path?", "affected_refs": ["FTR-001"], "affected_coverage": [], "blocking": False, "reason": "Choice required.", "resolution_phase": "DESIGN", "status": "OPEN"})
        self.assert_case(2, "MODEL_ERROR", mutate, contains="must be blocking")

    def test_product_objective_cannot_be_na(self):
        self.assert_case(2, "MODEL_ERROR", lambda c: c["coverage"].update({"product.objective": {"applicability": "NA", "rationale": "Not applicable."}}), contains="always APPLICABLE")

    def test_product_objective_does_not_imply_minimum_inventory_count(self):
        catalog = minimal_catalog()
        for collection in validator.COL:
            catalog[collection] = []
        taxonomy = {key: {"authority_domain": DOMAIN[key], "description": "x"} for key in CONCERNS}
        problems = validator.P()
        validator.structure(catalog, taxonomy, problems)
        self.assertEqual([], problems.e)


class ModelArtifactTests(unittest.TestCase):
    def test_taxonomy_preserves_exact_45_keys_and_uses_authority_domains(self):
        taxonomy = json.loads((ROOT / "model" / "coverage.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(1, taxonomy["model_version"])
        self.assertEqual(CONCERNS, list(taxonomy["concerns"]))
        self.assertEqual(set(CONCERNS), set(taxonomy["concerns"]))
        self.assertEqual(45, len(taxonomy["concerns"]))
        for metadata in taxonomy["concerns"].values():
            self.assertEqual({"description", "authority_domain"}, set(metadata))
            self.assertIn(metadata["authority_domain"], set(ROOT_TOKEN))
            self.assertNotIn("home", metadata)

    def test_schema_is_draft_2020_12_and_models_support_and_roots(self):
        schema = json.loads((ROOT / "model" / "project.schema.v1.json").read_text(encoding="utf-8"))
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        milestone = schema["properties"]["milestone"]
        self.assertIn("root_refs", milestone["required"])
        self.assertTrue(milestone["properties"]["root_refs"]["uniqueItems"])
        entry = schema["$defs"]["coverageEntry"]
        encoded = json.dumps(entry)
        self.assertIn("support_refs", encoded)
        self.assertNotIn("evidence_refs", encoded)

    def test_schema_document_patterns_accept_root_and_one_level_shard_only(self):
        schema = json.loads((ROOT / "model" / "project.schema.v1.json").read_text(encoding="utf-8"))
        pattern = schema["$defs"]["data"]["properties"]["doc_ref"]["pattern"]
        import re
        rx = re.compile(pattern)
        self.assertRegex("docs/DATA.md#DAT-001", rx)
        self.assertRegex("docs/data/account.md#DAT-001", rx)
        self.assertNotRegex("docs/data/nested/account.md#DAT-001", rx)
        self.assertNotRegex("docs/ARCHITECTURE.md#DAT-001", rx)

    def test_schema_requires_product_objective_applicable_and_design_decision_blocking(self):
        schema = json.loads((ROOT / "model" / "project.schema.v1.json").read_text(encoding="utf-8"))
        objective = schema["properties"]["coverage"]["properties"]["product.objective"]
        self.assertEqual("APPLICABLE", objective["allOf"][1]["properties"]["applicability"]["const"])
        open_unknown = schema["$defs"]["unknown"]["oneOf"][0]
        rule = open_unknown["allOf"][0]
        self.assertEqual("DECISION_REQUIRED", rule["if"]["properties"]["kind"]["const"])
        self.assertEqual("DESIGN", rule["if"]["properties"]["resolution_phase"]["const"])
        self.assertIs(True, rule["then"]["properties"]["blocking"]["const"])

    def test_schema_has_no_arbitrary_inventory_minimums(self):
        schema = json.loads((ROOT / "model" / "project.schema.v1.json").read_text(encoding="utf-8"))
        for collection in ["actors", "roles", "features", "acceptance", "systems", "data", "interfaces", "flows", "dependencies", "capabilities", "decisions", "unknowns"]:
            self.assertNotIn("minItems", schema["properties"][collection])

    def test_starting_catalog_uses_open_scope_empty_roots_and_unfinished_support(self):
        catalog = json.loads((ROOT / "templates" / "docs" / "catalog" / "project.json").read_text(encoding="utf-8"))
        self.assertEqual("OPEN", catalog["milestone"]["scope_state"])
        self.assertEqual([], catalog["milestone"]["root_refs"])
        self.assertEqual(set(CONCERNS), set(catalog["coverage"]))
        for entry in catalog["coverage"].values():
            self.assertEqual("APPLICABLE", entry["applicability"])
            self.assertEqual("NONE", entry["actual_depth"])
            self.assertEqual([], entry["support_refs"])
            self.assertNotIn("evidence_refs", entry)
        for collection in ["actors", "roles", "features", "acceptance", "systems", "data", "interfaces", "flows", "dependencies", "capabilities", "decisions", "unknowns"]:
            self.assertEqual([], catalog[collection])



if __name__ == "__main__":
    unittest.main()
