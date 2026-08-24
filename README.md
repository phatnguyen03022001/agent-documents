# agent-documents

`agent-documents` defines what a project must be able to describe and when its documentation reaches closure. It is deliberately narrower than an orchestration or documentation platform.

This repository does **not** define engineering quality or maturity levels; those meanings belong to `agent-standards`. It does **not** define agent workflow authority or execution protocol; those belong to `agent-skills`. `agent-runtime` is optional bounded execution infrastructure and is not a dependency of this model. Actual product truth belongs visibly in the target repository where the product is built.

V1 is guided by two principles:

> **BROAD BY DEFAULT. DEEP BY EVIDENCE. CLOSED WHEN BLOCKERS REACH ZERO.**

> **DESIGN TO CLOSURE, NOT TO EXHAUSTION.**

This repository currently contains an **unreleased V1 candidate pending independent audit**. Nothing here claims that V1 is canonical, stable, or complete before the required reviews.

The normative human-readable model is [`DOCUMENT_MODEL.md`](DOCUMENT_MODEL.md). The finite concern taxonomy and machine-readable catalog shape are under `model/`.

A small target repository normally starts with eight root Markdown documents plus one catalog:

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
  catalog/project.json
```

Those eight names are authority domains, not a permanent eight-file ceiling. A large target may physically shard a domain one level under its lowercase directory while preserving the same authority ownership; `DOCUMENT_MODEL.md` defines the exact rule.

`docs/catalog/project.json` contains V1 inventory, stable identities, relationships, milestone roots, coverage state/support links, and the explicitly authorized compact state/outcome fields. Markdown contains project explanation and specification.

`tools/validate.py` is a small Python-standard-library validator. Conceptually, run it with a target repository root; it reads `<target>/docs/catalog/project.json`, resolves logical Markdown references within the eight authority domains, applies the adjacent V1 model definitions, and prints either `DOCS_READY = TRUE` or `DOCS_READY = FALSE` with deterministic blocker categories. It does not mutate or auto-fix target documentation and does not judge prose quality or factual correctness.
