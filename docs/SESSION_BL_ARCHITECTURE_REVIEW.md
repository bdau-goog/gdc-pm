# Session BL — Architecture Review: GPU/Gemma Re-elevation
**Date:** June 12, 2026  
**Type:** Design discussion — no code written this session  
**Status:** Decisions locked. Implementation begins Session BM (Sprint L1).

---

## Context

Session BK reduced GPU costs by fixing the node-pool/deployment-scale bug (~$78/day idle → $0 off). The user then raised a strategic concern: the demo's value proposition ("AI-powered diagnostic advisor on open-weight Gemma") was no longer visibly demonstrated — the Gemma/GPU generative layer had been incrementally replaced by scripted/static content across many sessions to make the demo deterministic.

---

## The System A / System B Distinction (settled)

The root confusion was conflating two systems under the word "the LLM":

| System | What it is | Hardware | Status |
|---|---|---|---|
| **System A — Retrieval** | SentenceTransformer `all-MiniLM-L6-v2` + AlloyDB pgvector semantic search | CPU-only | Always live — unaffected by GPU shutdown |
| **System B — Generation** | Gemma 4 via Ollama | GPU (NVIDIA L4) | Dormant by default ($0 when off) |

System A (retrieval) was never removed and is the real L3 competitive moat. System B (generation) was incrementally swapped for scripted content. The migration was for demo-safety reasons that were real, but it left the "open-weight Gemma at the edge" claim invisible on screen.

---

## What Bayesian means in H1 — and where the weights come from

H1's "93% confidence drawdown" verdict is **not** an LLM output. It is CPU arithmetic:

```
Prior odds = 1.0  (50/50 — telemetry physically identical for both faults)
× F1: No free gas at intake   LR 3.0  (API RP 11S §4.2)
× F2: Casing pressure flat    LR 2.0  (API RP 11S §7.2)
× F3: Fluid column declining  LR 1.6
× F4: GOR nominal             LR 1.4
= 13.4 odds → 93.1% posterior
```

**Where the LR values came from:** A domain engineer assigned them once, at code-authoring time, grounded in API RP 11S physics. They live in `_BAYES_FINDINGS` dict in app.py — not in the database.

**Why this was the user's architectural concern:** "It feels wrong that the weights are in the code because 'a person' decided what they should be." The methodology (expert-elicitation, Good 1950 / Fagan 1975) is correct. The adaptability is the gap — changing a weight requires recompile + deploy.

**The trap to avoid:** Do NOT let Gemma assign LR values. An LLM picking safety-critical probability weights fails the hostile engineer: *"Show me its calibration."* The physics anchor stays human+citation; Gemma's role is extraction and bounded modulation.

---

## The Approved Architecture: Weights as Document Metadata

LR values move from code → `field_intel` database columns:

```sql
ALTER TABLE field_intel ADD COLUMN finding_code  TEXT;   -- 'F1'..'F4'
ALTER TABLE field_intel ADD COLUMN lr_base       REAL;   -- physics-anchored LR e.g. 3.0
ALTER TABLE field_intel ADD COLUMN lr_min        REAL;   -- floor of physics band e.g. 2.0
ALTER TABLE field_intel ADD COLUMN lr_max        REAL;   -- ceiling e.g. 4.5
ALTER TABLE field_intel ADD COLUMN lr_source     TEXT;   -- 'API RP 11S §4.2'
ALTER TABLE field_intel ADD COLUMN finding_dir   TEXT;   -- 'drawdown' | 'gas_lock'
```

Weights are now **adaptable without recompile** (SQL UPDATE, no docker build). The physics band (`lr_min`/`lr_max`) is the anchor; the citation (`lr_source`) is the legitimacy.

**Gemma's defensible role — Path A evidence-strength modulation:**
```
Document → Gemma extracts finding (GPU)
         → Gemma rates assertion strength: emphatic / qualified / absent (GPU)
         → effective_lr = clamp(lr_base × strength_factor, lr_min, lr_max) (CPU)
         → multiply posterior (CPU)
         → Gemma writes synthesis prose (GPU)
```
Gemma never invents a weight. It modulates within a physics-set band.

---

## H1 vs H2 Rigor Asymmetry

| | H1 Discern | H2 Classify |
|---|---|---|
| **Contested artifact** | The posterior % — "why 93%?" | The causal chain — "why paraffin not bearings?" |
| **Rigor type** | Numerical provenance — weight metadata, physics bands, auditable arithmetic | Causal/physical provenance — physics-cited discriminators, readable documents |
| **LR metadata needed** | Yes (Sprint L1) | No — H2 has no LRs |
| **Readable docs + provenance** | Yes (Sprint L2) | Yes (Sprint L2, different form: causal exclusion not LR bands) |
| **Gemma's role** | Extraction + evidence-strength modulation + conversational chat | Document summarization + causal synthesis |
| **Verdict mechanism** | **Stays Bayesian math** — never LLM. This is a feature: engineer can check the arithmetic. | Gemma-owned narrative synthesis |

**H2 is not lower rigor — it has different rigor.** Both get readable docs + discoverable provenance. Only H1 gets LR weight metadata (because only H1 has a posterior % to defend).

---

## UI Requirements (from discussion)

1. **Weights in metadata, not code** — adaptable without recompile ✅ (addressed by Sprint L1 schema)
2. **More documents** — corpus should feel realistic; retrieval should visibly discriminate (Sprint L3)
3. **Documents readable in UI** — click any evidence card → see full retrieved document text (Sprint L2)
4. **Weights discoverable** — provenance panel shows `lr_base` + physics band + citation + effective LR (Sprint L2)

**Example provenance panel (target design):**
```
┌─ Acoustic Survey — ESP-ALPHA-3 ──────────────────────┐
│ "Free gas at intake: NONE DETECTED. Fluid level       │
│  declining, 142 ft above pump intake..."              │
│                                                        │
│ ── How this evidence is weighted ──────────────────── │
│ Finding F1: No free gas at intake                      │
│ Physics band: LR 2.0–4.5  ·  anchor 3.0               │
│ Source: API RP 11S §4.2 (gas lock requires free gas)  │
│ Document assertion: EMPHATIC → effective LR 3.6        │
│ ⓘ Weight stored in field_intel metadata, not code     │
└────────────────────────────────────────────────────────┘
```

---

## GPU Cost Reality

- **$78/day idle (bug):** GPU node pool (3 × g2-standard-8 L4) billed 24/7 even with Ollama deployment scaled to 0. Root cause: standard GKE requires explicit node-pool resize; deployment-scale doesn't touch VMs.
- **After Session BK fix:** `gpu-start.sh`/`gpu-stop.sh` now resize the node pool. **Off = $0.**
- **Recommendation:** Trim `gpu-start.sh` to `--num-nodes 1` total (~$1.09/hr) vs 3 nodes (~$3.27/hr) for showcase. Single L4 is sufficient for Gemma 4.
- **Why not Autopilot:** Standard GKE gives explicit on/off node-pool control. Autopilot has limited GPU SKU support and no equivalent manual scale-to-zero. The Session BK fix only works because this is standard GKE.
- **Dev cost = $0** (all L1–L3 sprints are CPU-only). GPU only on for L4 showcase/record session.

---

## The Honest Demo Claim (locked)

> *"GDC turns a pile of unstructured field documents into structured findings (Gemma, GPU), fuses them with auditable probability math (CPU), and lets the operator interrogate the result in plain language (Gemma, GPU) — all inside the sovereign perimeter on open weights."*

**Replaces:** "the LLM diagnoses your pump" (never true — XGBoost does detection, Bayesian math does discrimination).

---

## 4-Sprint Re-elevation Sequence

| Sprint | Deliverable | GPU? | Cost |
|---|---|---|---|
| **L1** | `field_intel` schema migration + `_bayes_discriminate()` reads DB not dict. Pure refactor — posterior unchanged. | No | $0 |
| **L2** | Readable-doc modal + discoverable weight provenance panel (H1 + H2). Closes "cosine sim · pgvector" integrity-label violation. | No | $0 |
| **L3** | Corpus expansion — more H1/H2 `field_intel` docs (some noise). Makes retrieval visibly discriminating. | No | $0 |
| **L4** | Gemma extraction + Path A evidence-strength modulation. GPU on for showcase/record only; CPU fallback for dev. | Single L4 ~$1.09/hr (showcase only) | ~$2–3/session |

**Atomic-fix discipline:** Deploy and verify each sprint before starting the next.

---

## Active Integrity Exposures (going into Sprint L1)

| Exposure | Sprint that closes it |
|---|---|
| H1/H2 replay shows "cosine sim · pgvector (< 2s)" labels but retrieval is not executing | L1 + L2 |
| `_BAYES_FINDINGS` LRs hardcoded in app.py — not adaptable without recompile | L1 |
| `H1_METHODOLOGY.md` says LRs 8/5/3/2 → 99.6%; deployed code uses 3.0/2.0/1.6/1.4 → ~93% | Fix after L1 (doc cleanup) |

---

## Documents Updated This Session

| Document | What changed |
|---|---|
| `docs/DEMO_MASTER.md` §3 | Added "The Two-System Architecture" section — System A/B table, Gemma's defensible roles, H1/H2 asymmetry, honest demo claim |
| `docs/LLM_RAG_ARCHITECTURE_ASSESSMENT.md` | Appended §Session BL — weight-in-code problem, approved fix, H1/H2 rigor asymmetry, GPU cost reality, integrity exposures |
| `docs/NEXT_SESSION_PROMPT.md` | Updated STEP 3 — Session BL complete, Sprint L1 task spec with schema DDL |
| `docs/SESSION_BL_ARCHITECTURE_REVIEW.md` | **This file** — standalone discussion record |
