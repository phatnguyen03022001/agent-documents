# Agent Documents V1 Model

This document is the normative human-readable specification for the V1 candidate. The candidate remains unreleased and pending independent audit.

## 1. Purpose and system boundaries

`agent-documents` defines **what must be describable** about a project and **when documentation is closed for a milestone**. It does not define how agents receive authority, how engineering quality levels are named, or how execution is hosted.

Repository boundaries are strict:

- `agent-documents` = describable project truth, identities/relationships, coverage, and documentation closure.
- `agent-standards` = engineering quality meaning and any quality/maturity semantics.
- `agent-skills` = working method, handoff, authority, review, and Git protocol.
- `agent-runtime` = optional bounded execution infrastructure.
- target repository = actual product truth and instantiated documentation.

There is no runtime dependency among these repositories.

V1 follows: **BROAD BY DEFAULT. DEEP BY EVIDENCE. CLOSED WHEN BLOCKERS REACH ZERO.** It also follows: **DESIGN TO CLOSURE, NOT TO EXHAUSTION.**

## 2. Eight-document ownership model

A target repository uses exactly eight canonical Markdown documents plus one project catalog:

| Document | Owns |
| --- | --- |
| `docs/PRODUCT.md` | objective, actors/roles semantics, scope, non-goals, domain/external constraints |
| `docs/BEHAVIOR.md` | feature behavior, state/transitions, invariants/observable permissions, failures/edges, critical flows, acceptance text, safety/human-control behavior |
| `docs/ARCHITECTURE.md` | system responsibilities, runtime topology, communication boundaries, technology implications, capability boundaries, build/buy consequences |
| `docs/DATA.md` | material data semantics/ownership, lifecycle/persistence, retention/deletion, consistency/transactions, migration/backfill, provenance/lineage/quality |
| `docs/INTERFACES.md` | interface contracts, async/job/command/protocol details, external dependency assumptions, exchange/trust assumptions, dependency failure/fallback/exit treatment |
| `docs/QUALITY.md` | authentication constraints, authorization enforcement/trust boundaries, secrets/sensitive operations, privacy constraints, reliability, concurrency/failure boundaries, performance, observability, evidence strategy, cost/resource constraints |
| `docs/DELIVERY.md` | environments, configuration, deployment, migration/rollback, backup/restore, compatibility/versioning/platforms, operational ownership |
| `docs/DECISIONS.md` | context, alternatives, rationale, consequences, and reversibility explanation for material `DEC-*` choices |

The catalog is `docs/catalog/project.json`. No per-entity or per-feature catalog files exist in V1.

## 3. Field-level source-of-truth rules

Authority is intentionally split by field, not duplicated by convenience.

The project catalog is authoritative for inventory, IDs, names where modeled, typed relationships, milestone state, coverage applicability/depth state, capability status/disposition, decision kind/short outcome/reversibility, and unknown question/reason/status/resolution fields. Markdown is authoritative for normative project explanation and specification.

Specific rules:

- `FTR-*` inventory and relationships live in the catalog; feature behavior specification lives only under the feature's `spec_ref` in `BEHAVIOR.md`.
- `ACC-*` identity lives in the catalog; criterion text lives only in `BEHAVIOR.md`.
- `DEC-*` short selected `outcome` lives in the catalog; context, alternatives, rationale, consequences, and reversibility explanation live in `DECISIONS.md`.
- `CAP-*` status/disposition and typed references live in the catalog; architectural boundary and build/buy consequences live in `ARCHITECTURE.md`.
- `DAT-*` catalog records identify material data and owner; detailed lifecycle semantics live in `DATA.md`.
- `IFC-*` and `EXT-*` catalogs are the only inventories for material interfaces and external dependencies; contract/dependency explanation lives in `INTERFACES.md`.
- behavioral permission matrices belong in `BEHAVIOR.md`; `QUALITY.md` may describe enforcement/trust constraints but must reference rather than restate behavioral permissions.
- retention/deletion values belong in `DATA.md`; `QUALITY.md` may describe privacy constraints but must reference rather than duplicate those values.

## 4. The 45 coverage concerns

`model/coverage.v1.json` is the canonical finite machine-readable taxonomy. The V1 key set is exactly the following; this list must not drift from that file.

**Product**

- `product.objective`
- `product.actors_roles`
- `product.features_capabilities`
- `product.scope_non_goals`
- `product.domain_external_constraints`

**Behavior**

- `behavior.functional`
- `behavior.state_transitions`
- `behavior.invariants_permissions`
- `behavior.errors_edges_failures`
- `behavior.critical_flows`
- `behavior.acceptance`
- `behavior.safety_human_control`

**Architecture**

- `architecture.components_ownership`
- `architecture.runtime_topology`
- `architecture.communication_boundaries`
- `architecture.technology_choices`
- `architecture.build_buy`

**Data**

- `data.entities_ownership`
- `data.lifecycle_persistence`
- `data.retention_deletion`
- `data.consistency_transactions`
- `data.migration_backfill`
- `data.provenance_lineage_quality`

**Interfaces**

- `interfaces.contracts`
- `interfaces.async_jobs_commands`
- `interfaces.external_dependencies`
- `interfaces.data_exchange_trust`
- `interfaces.dependency_failure_exit`

**Quality**

- `quality.authentication`
- `quality.authorization_trust_boundaries`
- `quality.secrets_sensitive_operations`
- `quality.privacy_sensitive_data`
- `quality.timeouts_retries_idempotency_recovery`
- `quality.concurrency_failure_boundaries`
- `quality.performance_load_resources`
- `quality.observability`
- `quality.testing_evidence`
- `quality.cost_usage_bounds`

**Delivery**

- `delivery.environments_config`
- `delivery.deployment_migration_rollback`
- `delivery.backup_restore`
- `delivery.compatibility_versioning_platforms`
- `delivery.operational_ownership`

**Decision/unknown closure**

- `decisions.material_choices`
- `unknowns.open_questions`

The taxonomy does not encode target maturity, required security levels, required reliability levels, or similar quality grading.

## 5. Depth semantics

Depth is concern-specific documentation depth, not project maturity.

- `L0` — bounded acknowledgement: the concern is applicable and the project records the minimal explicit treatment needed to avoid ambiguity. Choosing `L0` as **required** depth requires a non-empty rationale explaining why bounded treatment is sufficient.
- `L1` — design-sufficient treatment: the concern is described enough to support the current milestone's design, traceability, and implementation decisions. This is the normal broad-by-default depth.
- `L2` — evidence-driven detail: the concern needs deeper treatment because current evidence, risk, irreversible cost, external contract, or other material pressure requires it. Choosing `L2` as **required** depth requires a non-empty rationale.
- `NONE` — no actual treatment has been established. `NONE` is allowed only as an unfinished `actual_depth`, never as `required_depth`.

For applicable concerns, `actual_depth` must be at least `required_depth` for closure. N/A concerns have neither depth nor evidence fields and require a non-empty rationale.

## 6. Identity classes

IDs are globally unique across the catalog and use these classes:

| Class | Pattern | Meaning |
| --- | --- | --- |
| Actor | `ACT-[0-9]{3,}` | human, system, or external actor |
| Role | `ROL-[0-9]{3,}` | role associated with actors |
| Feature | `FTR-[0-9]{3,}` | in-scope product behavior unit |
| Acceptance | `ACC-[0-9]{3,}` | acceptance criterion identity |
| System | `SYS-[0-9]{3,}` | owned system/component responsibility |
| Data | `DAT-[0-9]{3,}` | persistent or material ephemeral data entity |
| Interface | `IFC-[0-9]{3,}` | material interface/contract |
| Flow | `FLW-[0-9]{3,}` | user, system, or failure flow |
| External dependency | `EXT-[0-9]{3,}` | material external dependency |
| Capability | `CAP-[0-9]{3,}` | build/buy/defer decision boundary |
| Decision | `DEC-[0-9]{3,}` | material resolved decision |
| Unknown | `UNK-[0-9]{3,}` | unresolved/resolved question or conflict record |

Ordinary DTOs, transient local variables, trivial dependencies, and immaterial choices do not receive identities merely for completeness.

## 7. Project catalog semantics

The top-level V1 catalog requires exactly:

`model_version`, `milestone`, `coverage`, `actors`, `roles`, `features`, `acceptance`, `systems`, `data`, `interfaces`, `flows`, `dependencies`, `capabilities`, `decisions`, `unknowns`.

No unknown top-level properties are permitted. `model_version` is `1`. There is no `docs_ready` field; readiness is derived.

`milestone` contains a non-empty `id`, non-empty `name`, `scope_state` (`OPEN` or `FROZEN`), and a `scope_ref` into `docs/PRODUCT.md`.

A logical document reference has the form `docs/<file>.md#<TOKEN>`. `TOKEN` resolves against an ATX Markdown heading beginning with that exact token. This is a model reference and does not promise to reproduce GitHub URL-slug behavior.

Entity records, enums, and conditional fields are exactly those described by `model/project.schema.v1.json`. The validator additionally enforces invariants that JSON Schema cannot express conveniently, including global uniqueness, cross-record references, subset relationships, heading resolution, orphan checks, and closure.

## 8. Feature traceability

Every in-scope feature has at least one `ACT-*` actor, exactly one behavioral `spec_ref`, and at least one `ACC-*` acceptance criterion. Behavioral specification is never N/A for an in-scope feature.

Each feature has six applicability-aware relation states: roles, flows, data, interfaces, dependencies, and capabilities. A relation state is exactly one of:

- `{"refs": ["..."]}` with at least one reference; or
- `{"na": "non-empty rationale"}`.

When a feature references a flow, every interface, data entity, and external dependency used by that flow must be included in the corresponding feature relation. This makes feature-to-flow traceability deterministic rather than inferred from prose.

## 9. Unknown semantics

`UNK-*` records represent `QUESTION`, `DECISION_REQUIRED`, `ASSUMPTION`, `AUTHORITY_CONFLICT`, or `CONTRADICTION`. They identify the question, affected record references, affected coverage concerns, whether the unknown blocks closure, why it matters, its resolution phase, and its status.

Resolution phases are `DESIGN`, `IMPLEMENTATION`, `VERIFICATION`, or `POST_MILESTONE`. Status is `OPEN` or `RESOLVED`.

A resolved unknown requires `resolved_by_ref`. A resolved `DECISION_REQUIRED` unknown must resolve to a `DEC-*` record. An open `AUTHORITY_CONFLICT` or `CONTRADICTION` must be blocking. Any open blocking unknown must have `resolution_phase: DESIGN`.

Open non-blocking unknowns may remain after documentation closure only because the catalog explicitly states they do not block the current milestone; they remain visible and traceable rather than being silently discarded.

## 10. Build/buy semantics

`CAP-*` records model material capability disposition.

An `OPEN` capability has `disposition: null` and must identify an open blocking `UNK-*`. A `RESOLVED` capability has one disposition: `BUILD`, `BUY`, `HYBRID`, or `DEFER`.

- `BUILD` requires at least one `SYS-*` reference.
- `BUY` requires at least one `EXT-*` reference.
- `HYBRID` requires at least one `SYS-*` and at least one `EXT-*` reference.
- `DEFER` requires a `defer_ref` and must not be referenced by an in-scope feature.

Every non-DEFER resolved capability requires a `decision_ref`, an architectural `boundary_ref`, and an `exit` state. `exit` is exactly either a document `ref` or an explicit N/A rationale. The catalog owns disposition; `ARCHITECTURE.md` explains boundary and consequences rather than redefining that disposition.

## 11. Closed-world milestone rule

`scope_state: OPEN` means scope is still changing and `DOCS_READY` is false.

`scope_state: FROZEN` means the milestone's in-scope world is closed for the purpose of this predicate: the catalog inventory, scope reference, concern applicability, and required depth are the set against which closure is evaluated. Frozen scope does not claim the product can never change; it means changes require an explicit reopening event rather than silent expansion.

## 12. Coverage, resolution, and detail gaps

A **coverage gap** exists when an applicable concern has `actual_depth: NONE`.

A **detail gap** exists when an applicable concern has non-`NONE` actual treatment but `actual_depth` is below `required_depth`. The validator reports both coverage and detail failures under `COVERAGE_GAP` because both violate the same deterministic depth invariant.

A **resolution gap** exists when the model says a material design issue required for the milestone is unresolved, including blocking unknowns, unresolved contradictions/authority conflicts, or build/buy state that cannot yet close.

Reference, traceability, orphan, and structural N/A contradictions are separate deterministic blockers; they are not natural-language contradiction detection.

## 13. Deterministic `DOCS_READY` predicate

`DOCS_READY = TRUE` if and only if all of the following hold:

1. the V1 model is syntactically and structurally valid and uses the exact 45-key taxonomy;
2. all IDs and typed references are valid and globally unique;
3. required logical Markdown references resolve to the expected canonical documents and heading tokens;
4. milestone scope is `FROZEN`;
5. every applicable concern has actual depth other than `NONE` and at least its required depth;
6. every N/A and every required L0/L2 choice has its required non-empty rationale;
7. feature traceability and feature-flow subset invariants hold;
8. capability build/buy rules hold and no deferred capability is referenced by a current feature;
9. there is no unresolved blocking unknown, authority conflict, or contradiction;
10. there are no orphan active entities or obvious inventory-versus-N/A contradictions; and
11. no other deterministic validator blocker remains.

No field stores this answer. Readiness is recomputed from project truth each time.

## 14. Stop rule

Once a milestone is `FROZEN` and evaluates to `DOCS_READY = TRUE`, design-document expansion for that milestone must stop. The goal is closure, not exhaustive elaboration.

Expansion resumes only after a recognized reopening trigger: milestone scope is explicitly reopened; new material evidence invalidates an existing model claim; a new contradiction or authority conflict is recorded; or governing project authority explicitly changes the milestone's required project truth. A desire for more prose by itself is not a reopening trigger.

## 15. Validator boundary

`tools/validate.py` uses only the Python standard library, performs no network access, and writes nothing to the target repository. It reads `docs/catalog/project.json`, the target Markdown documents needed to resolve logical references, and its own adjacent V1 model definition.

The validator checks deterministic structure, references, traceability, build/buy, unknown, orphan, coverage/depth, and closed-world invariants. It does not judge whether prose is elegant, comprehensive, secure, reliable, mature, or factually wise. Those require human/design review and, where applicable, `agent-standards`.

Exit status is:

- `0` — model valid and `DOCS_READY = TRUE`;
- `1` — model valid but `DOCS_READY = FALSE`;
- `2` — malformed/unsupported model or validator usage error.

The validator never auto-fixes documentation.

## 16. Target-repository structure

The instantiated target structure is:

```text
docs/
  PRODUCT.md
  BEHAVIOR.md
  ARCHITECTURE.md
  DATA.md
  INTERFACES.md
  QUALITY.md
  DELIVERY.md
  DECISIONS.md
  catalog/
    project.json
```

Product truth stays in that target repository. `agent-documents` supplies reusable templates/model definitions, not project-specific truth.

## 17. Non-goals

V1 is not an orchestration platform, documentation CMS, API server, MCP server, database, release workflow, generated report system, maturity framework, engineering standards library, or agent authority protocol. It does not define project-specific feature content or split features into separate documentation files.

It does not perform natural-language contradiction detection. It does not infer undocumented requirements, target quality levels, security grades, reliability grades, or maturity levels.

## 18. Versioning and evolution rules

`model_version: 1` binds a catalog to these V1 semantics. `coverage.v1.json` is the finite V1 taxonomy and `project.schema.v1.json` is the V1 structural schema.

Backward-incompatible changes to fields, identity classes, relation semantics, depth meaning, build/buy rules, unknown rules, taxonomy membership, or closure semantics require a new model/taxonomy version rather than silent reinterpretation. Compatible wording clarifications may be made only when they preserve existing machine semantics and authority boundaries.

A future version must define an explicit migration/evolution path before it can replace V1. This V1 repository state is only an unreleased candidate pending independent design-review, gap-analysis, and adversarial audit; it must not be described as canonical solely because its deterministic tests pass.
