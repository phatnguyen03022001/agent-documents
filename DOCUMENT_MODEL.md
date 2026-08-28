# Agent Documents V1 Model

This document is the normative human-readable specification for the V1 candidate. The candidate remains unreleased and pending independent audit.

## 1. Purpose and system boundaries

`agent-documents` defines **what must be describable** about a project and **when documentation is closed for a milestone**. It does not define agent authority, engineering maturity levels, or execution infrastructure.

Repository boundaries are strict:

- `agent-documents` = describable project truth, stable identities/relationships, finite coverage, and documentation closure.
- `agent-standards` = engineering quality meaning and any quality/maturity semantics.
- `agent-skills` = working method, handoff, authority, review, and Git protocol.
- `agent-runtime` = optional bounded execution infrastructure.
- target repository = actual product truth and instantiated documentation.

There is no runtime dependency among these repositories.

V1 follows **BROAD BY DEFAULT. DEEP BY EVIDENCE. CLOSED WHEN BLOCKERS REACH ZERO.** It also follows **DESIGN TO CLOSURE, NOT TO EXHAUSTION.**

## 2. Eight-document ownership model

V1 has exactly eight canonical **authority domains**. A domain owns meaning regardless of whether its content is held in its root file or legal physical shards.

| Authority domain | Root document | Owns |
| --- | --- | --- |
| `PRODUCT` | `docs/PRODUCT.md` | objective, actor/role semantics, scope, non-goals, domain/external constraints |
| `BEHAVIOR` | `docs/BEHAVIOR.md` | feature behavior, state/transitions, invariants/observable permissions, failures/edges, critical flows, acceptance text, safety/human-control behavior |
| `ARCHITECTURE` | `docs/ARCHITECTURE.md` | system responsibilities, topology, communication boundaries, technology implications, capability boundaries, build/buy consequences |
| `DATA` | `docs/DATA.md` | material data semantics/ownership, lifecycle/persistence, retention/deletion, consistency/transactions, migration/backfill, provenance/lineage/quality |
| `INTERFACES` | `docs/INTERFACES.md` | interface contracts, async/job/command/protocol details, external dependency assumptions, exchange/trust assumptions, dependency failure/fallback/exit treatment |
| `QUALITY` | `docs/QUALITY.md` | authentication constraints, authorization enforcement/trust boundaries, secrets/sensitive operations, privacy constraints, reliability, concurrency/failure boundaries, performance, observability, evidence strategy, cost/resource constraints |
| `DELIVERY` | `docs/DELIVERY.md` | environments, configuration, deployment, migration/rollback, backup/restore, compatibility/versioning/platforms, operational ownership |
| `DECISIONS` | `docs/DECISIONS.md` | material decision explanation and unknown/open-question context |

The eight root templates are the default small-project physical shape. Physical sharding does not create a ninth authority domain and does not change semantic ownership.

## 3. Field-level source-of-truth rules

The project catalog is authoritative for inventory, IDs, names where modeled, typed relationships, milestone state and roots, coverage applicability/depth/support links, capability status/disposition, decision kind/short outcome/reversibility, and unknown question/reason/status/resolution attribution/reference fields. Markdown is authoritative for normative project explanation and specification.

Specific rules:

- `FTR-*` inventory and relationships live in the catalog; feature behavior specification lives under its `spec_ref` in `BEHAVIOR`.
- `ACC-*` identity lives in the catalog; criterion text lives only in `BEHAVIOR`.
- `DEC-*` short selected `outcome` lives in the catalog; context, alternatives, rationale, consequences, and reversibility explanation live in `DECISIONS`.
- `CAP-*` status/disposition and typed references live in the catalog; architectural boundary and build/buy consequences live in `ARCHITECTURE`.
- `DAT-*` records identify material data and owner; detailed lifecycle semantics live in `DATA`.
- `IFC-*` and `EXT-*` records are the only material interface/dependency inventories; explanation lives in `INTERFACES`.
- behavioral permission matrices belong in `BEHAVIOR`; `QUALITY` references rather than restates them.
- retention/deletion values belong in `DATA`; `QUALITY` references rather than duplicates them.
- a shard is canonical only because an authorized catalog or coverage reference points into it; merely creating a file does not create authority.

## 4. The 45 coverage concerns

`model/coverage.v1.json` is the canonical finite machine-readable taxonomy. Each concern declares one `authority_domain`, not one fixed physical file. The V1 key set is exactly:

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

- `L0` — bounded acknowledgement. Choosing `L0` as required depth needs a non-empty rationale explaining why bounded treatment is sufficient.
- `L1` — design-sufficient treatment for the current milestone. This is the normal broad-by-default depth.
- `L2` — evidence-driven detail required by current risk, irreversible cost, external contract, or another material pressure. Choosing `L2` as required depth needs a non-empty rationale.
- `NONE` — no actual treatment has been established. `NONE` is only an unfinished `actual_depth`; it is never a `required_depth`.

For an applicable concern, `actual_depth` must be at least `required_depth` for closure. N/A concerns have neither depth nor support fields and require a non-empty rationale. `product.objective` is always `APPLICABLE` in V1 and cannot use the N/A form; this rule does not impose a minimum number of features or other entity records.

An applicable coverage record uses `support_refs`. `actual_depth: NONE` requires `support_refs: []`. `actual_depth: L0`, `L1`, or `L2` requires at least one support reference. Support links are structural evidence that treatment exists; they are not proof that the prose is correct or good.

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

Ordinary DTOs, transient variables, trivial dependencies, and immaterial choices do not receive identities merely for completeness.

## 7. Project catalog semantics

The top-level V1 catalog requires exactly `model_version`, `milestone`, `coverage`, `actors`, `roles`, `features`, `acceptance`, `systems`, `data`, `interfaces`, `flows`, `dependencies`, `capabilities`, `decisions`, and `unknowns`. No unknown top-level properties are permitted. `model_version` is `1`; there is no `docs_ready` field.

`milestone` contains non-empty `id` and `name`, `scope_state` (`OPEN` or `FROZEN`), a `scope_ref` in `PRODUCT`, and `root_refs`.

A logical document reference has the form `docs/<file>.md#<TOKEN>` for a root document or `docs/<lowercase-domain>/<safe-file>.md#<TOKEN>` for a legal shard. `TOKEN` must resolve to exactly one canonical ATX Markdown heading beginning with that exact token. ATX-looking lines inside fenced code blocks or HTML comments are ignored, and multiple matching canonical headings are invalid. This is a model reference and does not promise GitHub URL-slug behavior.

Every `milestone.scope_ref`, entity `doc_ref`, feature `spec_ref`, capability `boundary_ref` or `defer_ref`, and `exit.ref` must resolve to a section containing at least one non-heading, non-whitespace, non-HTML-comment content line.

A resolved unknown additionally carries `resolution_ref`. This reference must stay in the `DECISIONS` authority domain, its fragment token must be exactly the record's own `UNK-*` identity, and the resolved section must contain structural content. This exact-token binding is specific to `resolution_ref`; ordinary document/specification references are not globally required to use their catalog ID as the heading token.

Legal root paths are the eight root documents in section 2. Legal shard paths are exactly one physical level below `docs/`: `docs/product/<safe-file>.md`, `docs/behavior/<safe-file>.md`, `docs/architecture/<safe-file>.md`, `docs/data/<safe-file>.md`, `docs/interfaces/<safe-file>.md`, `docs/quality/<safe-file>.md`, `docs/delivery/<safe-file>.md`, or `docs/decisions/<safe-file>.md`. A safe filename is one non-empty Markdown filename using letters, digits, `.`, `_`, or `-`, beginning with a letter or digit. A subdirectory below an authority shard directory is invalid.

Entity-specific document references must remain inside the entity's required authority domain even when sharded. The complete record shapes and enums are defined by `model/project.schema.v1.json`; the validator enforces cross-record invariants JSON Schema cannot conveniently express.

## 8. Feature traceability

Every in-scope feature has at least one actor, a `BEHAVIOR` specification reference, and at least one acceptance criterion. Behavior specification is never N/A for an in-scope feature.

Every `ROL-*` record has at least one `ACT-*` reference. When a feature relates to a role, the feature's `actor_refs` and that role's `actor_refs` must share at least one actor. Roles remain reusable and may include additional actors that are not attached to every feature using the role.

Applicability-aware relations (`roles`, `flows`, `data`, `interfaces`, `dependencies`, `capabilities`) contain exactly one of `{"refs": [...]}` with a non-empty array or `{"na": "reason"}` with a non-empty rationale. A feature's related flow may not use an interface, data entity, or external dependency omitted from the feature's corresponding relation mapping.

All current `FTR-*` records are implicit graph roots for the milestone.

## 9. Unknown semantics

An unknown is `QUESTION`, `DECISION_REQUIRED`, `ASSUMPTION`, `AUTHORITY_CONFLICT`, or `CONTRADICTION`; its resolution phase is `DESIGN`, `IMPLEMENTATION`, `VERIFICATION`, or `POST_MILESTONE`; its status is `OPEN` or `RESOLVED`.

Resolved records require both `resolved_by_ref` and `resolution_ref`. `resolved_by_ref` identifies the catalog record associated with the resolution; resolved `DECISION_REQUIRED` records must still resolve to `DEC-*`, while other unknown kinds are not forced to resolve to a decision record. `resolution_ref` points to dedicated resolution evidence in `DECISIONS`, with a fragment token exactly equal to the resolved `UNK-*` identity and structural content in that section. Open `AUTHORITY_CONFLICT` and `CONTRADICTION` records are blocking. An open `DECISION_REQUIRED` record with `resolution_phase: DESIGN` is also blocking. Every open blocking unknown has `resolution_phase: DESIGN`.

`UNK-*` records participate in reference and closure semantics but are not material graph roots and are not scored as orphan material entities. They therefore cannot appear in `milestone.root_refs`.

## 10. Build/buy semantics

A capability is either open or resolved. Open capabilities have `disposition: null` and an open blocking unknown. Resolved dispositions are `BUILD`, `BUY`, `HYBRID`, or `DEFER`.

- `BUILD` requires at least one `SYS-*` reference.
- `BUY` requires at least one `EXT-*` reference.
- `HYBRID` requires at least one system and at least one external dependency.
- `DEFER` requires `defer_ref` and may not be referenced by an in-scope feature.

Every resolved non-DEFER capability requires an architectural boundary and a `DEC-*` reference. Exit treatment is either an `ARCHITECTURE` reference or an explicit non-empty N/A rationale. A DEFER capability is not an active orphan-scored entity and cannot be a milestone root.

## 11. Closed-world milestone rule

A milestone is closed-world only when `scope_state` is `FROZEN`. `scope_ref` identifies the authoritative scope section in `PRODUCT`.

`milestone.root_refs` explicitly roots non-feature material entities that belong directly to the current milestone without requiring an artificial feature relation. Each root must resolve to an existing `ACT`, `ROL`, `ACC`, `SYS`, `DAT`, `IFC`, `FLW`, `EXT`, `CAP`, or `DEC` record. `FTR` is forbidden because features are already implicit roots; `UNK` is forbidden because unknowns are closure records, not material graph roots. Root references are unique, and a DEFER capability cannot be a root.

Reachability starts from every current `FTR-*` plus `milestone.root_refs`, then follows deterministic outgoing catalog ID references. An active material entity is orphaned when it is not reachable from those roots. A disconnected cluster remains orphaned merely referencing other members of the same disconnected cluster.

## 12. Coverage, resolution, and detail gaps

A **coverage gap** exists when an applicable concern has `actual_depth: NONE`, actual depth below required depth, missing required structural support, or a support section that has no real content.

A **resolution gap** exists when a decision-required design issue, contradiction, capability choice, or other blocking unknown remains unresolved under its V1 rule.

A **detail gap** exists when current evidence requires more depth than is actually documented; operationally this is represented by `actual_depth < required_depth`, not by an unbounded request for more prose.

A support reference is valid only when it resolves in the concern's canonical authority domain. Every logical reference resolves from its unique matching canonical heading until the next canonical heading of the same or higher level; headings inside fenced code blocks or HTML comments do not participate in resolution. Support references and the canonical scope/entity/specification/capability explanation references named in section 7 require at least one line that is not a heading, whitespace, or HTML-comment content. Heading-only, whitespace-only, and HTML-comment-only sections do not establish structural content.

## 13. Deterministic `DOCS_READY` predicate

`DOCS_READY` is derived; it is never stored in the catalog. It is `TRUE` exactly when all deterministic V1 checks succeed, including:

1. the model version and catalog/taxonomy structures are supported and exact;
2. all IDs and typed references are valid and globally unique;
3. every logical Markdown reference uses a legal root/shard path, stays within its authority domain, resolves exactly one canonical heading token, and ignores ATX-looking headings inside fenced code blocks and HTML comments;
4. every applicable concern has structurally valid `support_refs`, actual depth is not `NONE`, and actual depth meets required depth;
5. every resolved support reference, every canonical scope/entity/specification/capability explanation reference, and every resolved unknown `resolution_ref` points to a section containing structural content; resolved unknown resolution references stay in `DECISIONS` and bind their fragment token exactly to their own `UNK-*` identity;
6. feature traceability, relation-state, role/feature actor-intersection, and flow-subset invariants hold, and every role has at least one actor;
7. build/buy and unknown-resolution invariants hold, including the existing `DECISION_REQUIRED` attribution rule, blocking open design-phase `DECISION_REQUIRED` records, and no blocking unknown/conflict/contradiction remains open;
8. every active orphan-scored entity is reachable from a feature root or explicit milestone root;
9. structural N/A contradictions are absent and `product.objective` remains applicable; and
10. milestone scope is `FROZEN`.

Malformed/unsupported model or usage errors exit `2`. A valid model that has closure blockers exits `1`. A valid model with `DOCS_READY = TRUE` exits `0`.

## 14. Documentation closure and reopening

For documentation purposes, a milestone that is `FROZEN` and reaches `DOCS_READY = TRUE` is closed: the current V1 documentation requirements are satisfied, and this model requires no additional documentation depth for that milestone.

Documentation closure reopens whenever authoritative project facts change such that the deterministic V1 predicate becomes false, for example after a scope change, a newly represented blocking unknown or contradiction, invalidated support/reference evidence, or a changed external constraint. Closure is restored when the predicate is true again.

This section defines documentation closure only. It does not direct or authorize design, execution, review, promotion, release, or any other workflow. **DESIGN TO CLOSURE, NOT TO EXHAUSTION** is a documentation-scope principle, not a workflow-control rule.

## 15. Validator boundary

`tools/validate.py` uses only the Python standard library, reads the target repository, uses its own adjacent V1 model definitions, and performs no network access or target mutation. It checks deterministic structure, references, support presence/location, graph reachability, and closure invariants.

It does **not** judge whether prose is persuasive, complete in a literary sense, factually correct, secure, reliable, performant, mature, or otherwise high quality. In particular, the non-empty support-section check proves only that structural documentation content exists at the referenced location.

## 16. Target-repository structure

The default target shape remains:

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

When size requires physical scaling, any authority domain may additionally use its one-level lowercase shard directory, for example `docs/data/accounts.md` or `docs/behavior/onboarding.md`. Sharding is optional, creates no additional authority domain, and creates no extra catalog. One-file-per-concern and one-file-per-feature organization is neither required nor implied.

## 17. Non-goals

V1 is not an orchestration platform, documentation CMS, generator framework, database, API server, MCP server, workflow engine, maturity model, engineering standard, or agent-authority protocol. It does not define SEC/REL/etc. levels, project-specific truth, product examples tied to a specific application, automatic prose scoring, or natural-language contradiction detection.

## 18. Versioning and evolution rules

`model_version: 1` identifies this catalog/model contract. The 45 concern keys and eight authority domains are closed for V1. Physical shards are organization within an existing authority, not model extension.

Changes that add/remove/rename a concern, add a ninth authority domain, change identity classes, alter field authority, or otherwise break the V1 machine contract require explicit versioned evolution rather than silent reinterpretation. Validator/model/schema/template changes within a version must remain mutually consistent and deterministic.

This repository remains an unreleased candidate pending independent review; satisfying this model does not itself make V1 canonical or authorize release/promotion.
