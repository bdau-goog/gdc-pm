# GDC-PM — Predictive Maintenance Edge AI Demo

## What This Is

A fully deployed demo system running on GKE that proves GDC Edge AI gives production operators more time before a failure becomes irreversible — across three distinct scenarios:

| Scenario | Asset | Story |
|---|---|---|
| **H1 Detect** | ESP gas lock | GDC detects ~21 min before SCADA alarms. $0 VFD fix vs $150,000 pump pull. |
| **H2 Discern** | ESP slug flow | Prevents a $150,000 false-alarm pump pull. Vibration alarm ≠ downhole failure. |
| **H3 Optimize** | ESP VFD optimization | Vertex AI Vizier finds optimal Hz. $1.2M additional revenue over 90 days. |

The technology stack is 100% real and production-grade. The fault injection button replaces what would be a live sensor connection in a customer deployment.

## Live System

```
https://gdc-pm.bdau.io
```

## Active Documentation

| Document | Purpose |
|---|---|
| [`DEMO_MASTER.md`](DEMO_MASTER.md) | **THE SPEC** — H1/H2/H3 requirements, physics, UI design, implementation order. Read first. |
| [`MODEL_FOUNDATIONS.md`](MODEL_FOUNDATIONS.md) | Canonical model spec, training parameters, integrity status, retrain runbook. |
| [`BACKEND_CONFORMANCE_REPORT.md`](BACKEND_CONFORMANCE_REPORT.md) | Code audit vs target architecture. Integrity violations and kill-list. |
| [`NEXT_SESSION_PROMPT.md`](NEXT_SESSION_PROMPT.md) | Current cluster state, git head, next tasks. Rewritten every session. |
| [`SESSION_LOG.md`](SESSION_LOG.md) | Append-only decision history. Read last 3 entries for context. |
| [`INTEGRITY_AUDIT.md`](INTEGRITY_AUDIT.md) | Known display-vs-reality mismatches. Any violation not in here is undocumented. |
| [`narratives/H2_SLUG_FLOW.md`](narratives/H2_SLUG_FLOW.md) | H2 slug flow narrative detail, SCADA rebuttal wording. |
| [`runbooks/deploy-from-scratch.md`](runbooks/deploy-from-scratch.md) | Zero-to-cluster deployment runbook. |
| `rag_source/` | Source documents ingested into AlloyDB pgvector. These are data, not docs. |

## Archived (Superseded)

Historical documents that predate the current H1/H2/H3 architecture are in [`docs/archive/`](archive/). They are preserved for reference but **do not describe the current system**.

## Stack

```
Telemetry Simulator → RabbitMQ → Event Processor → AlloyDB Omni (pgvector)
                                                           ↕
Fault-Trigger-UI (FastAPI + Vue.js) ← ← ← ← ← ← ← ← ← ← ←
  ├─ XGBoost health regressors (on-cluster, ubj files)
  ├─ Ollama Gemma 4 (on-cluster NVIDIA L4 GPU)
  ├─ RAG pipeline (AlloyDB pgvector, 18 OEM manual sections)
  └─ Vertex AI Vizier (Google Cloud, H3 only)

Inference API (FastAPI) ← XGBoost classifiers (esp, gas_lift, mud_pump, top_drive)
```

## Rules

- `terraform/gke.tf` must NOT be applied — it would destroy the live cluster.
- All demo changes go into `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`.
- After changes: docker build → docker push → kubectl rollout restart.
- DEMO_MASTER.md takes precedence over all other docs including this one.
