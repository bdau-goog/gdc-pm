# LLM / RAG Architecture Assessment — GPU, Gemma, and the L3 Differentiator
**Created:** Session BK (June 12, 2026)
**Trigger:** User question after GPU node pool was scaled to 0 for cost reasons — "How are the LLM assessments in H1/H2 handled if there is no GPU, and how was the L3 capability slowly removed?"
**Status:** Assessment only — no code changed. Impact exploration deferred to next session.

---

## Executive Summary

The demo narrative has been conflating **two different systems** under the single word "the LLM." They have completely different GPU dependencies, and separating them resolves the confusion:

- **System A — Retrieval (the real L3 differentiator):** SentenceTransformer embeddings + AlloyDB pgvector semantic search. Runs **CPU-only**. Never removed. Unaffected by the GPU shutdown.
- **System B — Generation (Gemma via Ollama):** Generates dynamic demo documents and writes natural-language operator advisories. Requires **GPU**. This is what is dormant when the GPU pool is at 0.

The differentiator vs. Threshold SCADA and Advanced APM is **System A** — semantic retrieval of unstructured documents fused with live telemetry. Gemma (System B) was the *content factory* that manufactured realistic demo documents and worded advisories. In a real deployment the dynamic documents come from the operator's own systems (SAP, OSIsoft PI, work-order DBs); Gemma was standing in for those sources in the demo.

---

## Code-Verified Facts

| Claim | Evidence |
|---|---|
| Embedding model runs CPU-only in fault-trigger-ui | `sentence-transformers==2.7.0` in `fault-trigger-ui/requirements.txt`; loaded via `SentenceTransformer('all-MiniLM-L6-v2')` (app.py ~line 158) |
| Only ollama requests the GPU | `nvidia.com/gpu: 1` appears **only** in `gke/ollama/k8s/ollama.yaml`; fault-trigger-ui manifest has no GPU request |
| pgvector semantic search is real | `ORDER BY embedding <-> %s::vector` queries in app.py (lines ~5162, 5171, 5985, 5991) |
| Multivariate detector is XGBoost, not Gemma | `esp_health.ubj` loaded via `xgb.Booster()`, 8 sensor features, CPU in-process (app.py ~line 6618) |
| H1 discrimination is Bayesian math, not Gemma | `_bayes_discriminate()` naive-Bayes log-odds over document-derived findings |

---

## The Two Systems in Detail

### System A — Retrieval Engine (CPU · real · the differentiator)
- **SentenceTransformer `all-MiniLM-L6-v2`** embeds queries + documents to 384-dim vectors. Ships in the CPU pod; does **not** touch the GPU.
- **AlloyDB pgvector** stores embeddings and performs live cosine/L2 similarity search.
- This is the technical core of "fuse unstructured documents with live telemetry." Disabling the GPU had **zero** effect on it.

### System B — Generative LLM (Gemma via Ollama · GPU · two sub-roles)
- **B1 — Document generation:** Gemma synthesizes dynamic documents (well reports, shift handoffs, sample analyses) to populate the corpus during a live fault. (app.py `_intelligence_feed_loop`, lines 509–644.)
- **B2 — Recommendation prose:** Gemma writes natural-language operator advisory text layered on top of the deterministic rule-based recommendation. (app.py ~lines 3733–3757, and the SSE stream endpoint ~3780–3943.)
- Both fail **gracefully** when Ollama is unreachable — the loop skips the cycle (B1) or the rule-based text is returned with `enhanced_by_llm: false` (B2).

---

## Two Operating Modes — and the Migration Between Them

The demo has two modes. The project migrated its **primary** demo path from the first to the second over many sessions:

| | LIVE INJECT mode (original) | SCENARIO REPLAY mode (current primary) |
|---|---|---|
| Telemetry | Real-time degrade thread | Pre-computed deterministic trajectory |
| Documents | Gemma generates live (GPU) + pgvector retrieves (CPU) | **Scripted reveals** — hardcoded HTML (H1) / static Python templates (H2) |
| Retrieval | Real pgvector search executes | Illustrated, not live-executed (H1/H2) |
| Reliability | Variable (GPU cold-start + non-deterministic output) | Deterministic, demo-safe |

The migration happened because a scripted, deterministic flow survives a live demo better than one depending on a ~15-minute GPU cold-start and non-deterministic model output. **Session BJ's H2 change (static templates replacing Gemma generation) was the final step of that migration** — but the migration had been underway for many sessions. That incremental shift is the "slow removal" the user sensed.

---

## Where Real Live Retrieval Executes Today (CPU, no GPU)

- **H3 Optimize tab:** the `?constraint=gas|thermal|rul` selector runs **genuine live pgvector retrieval** — `SentenceTransformer.encode()` + `ORDER BY embedding <-> vector LIMIT 1` against the 10-doc Pad Alpha corpus (Session BI). Real semantic search, CPU, working now.
- **Static industry/manual corpus:** `rag_documents` is seeded at startup with real embeddings and is genuinely retrievable.

## Where Documents Are Scripted (INTEGRITY FLAG)

- **H1 replay:** sonic log / shift note / GOR modals are hardcoded HTML. `/api/h1/scenario-replay` returns only sensor arrays + Bayesian math — no retrieval runs.
- **H2 replay:** the 3 documents come from static Python templates (Session BJ). No pgvector call in the replay path.
- In both, the on-screen labels **"cosine sim 0.94 · AlloyDB pgvector (< 2s)"** are decorative — retrieval is not actually executing during the replay.
- **This is a displayed-value-vs-actual-value consideration under the `.clinerules` "Integrity — No Silent Lies" rule.** It must be resolved by either:
  - **(a)** wiring the H1/H2 replay to perform a real retrieval against the seeded corpus (makes the differentiator actually execute during the demo), OR
  - **(b)** softening the labels so they don't assert a live search that isn't happening.

---

## Direct Answers

**"How was that capability slowly removed?"** — The *retrieval* capability (the real differentiator) was **not** removed; it runs on CPU and is live in H3. What was incrementally replaced was *Gemma generation* of demo documents, swapped for scripted/static documents to make the demo deterministic. Most recent step: Session BJ H2.

**"How does the demo work without it?"** — The Briefing → Scenario Replay path works because the documents are scripted reveals that *represent* the L3 concept. It demonstrates the argument (telemetry alone is ambiguous; documents resolve it) without executing live retrieval in H1/H2. H3 still executes genuine live pgvector retrieval on CPU.

**"I thought the multivariate detection model ran on GPU"** — It does not. The detector is **XGBoost** (`esp_health.ubj`), CPU-only, in-process. Gemma never did sensor inference — only text generation/wording.

---

## Open Questions for Next Session (Impact Exploration)

1. **Demo narrative decision:** Is the live-inject Gemma intelligence feed part of the demo story, or is Briefing + Replay the canonical path? (VIDEO_SCRIPT.md currently reflects Briefing + Replay.)
2. **Integrity resolution for H1/H2 replay labels:** wire real pgvector retrieval into the replay path, or soften the "cosine sim · pgvector" labels. (Decision + sprint.)
3. **Strategic framing in DEMO_MASTER §3:** make System A (retrieval, CPU, real) vs System B (Gemma generation, GPU, sovereign content) explicit, so the L3 claim is "semantic retrieval of unstructured documents fused with telemetry" — not "an LLM analyzes your sensors." The latter is not what happens and would fail engineer scrutiny.
4. **Cost posture:** confirm GPU stays at 0 by default; decide whether any demo segment requires it on-demand.

---

---

## Session BL — Architecture Decisions (June 12, 2026)

### The Weight-in-Code Problem (and the fix)

The `_BAYES_FINDINGS` dict in app.py assigns likelihood ratios (LRs) as hardcoded constants (3.0 / 2.0 / 1.6 / 1.4 → ~93% posterior). These are physics-cited expert weights grounded in API RP 11S §4.2/§7.2 — the methodology (Good 1950 / Fagan NEJM 1975 Bayesian log-odds) is legitimate. But the weights are in code: changing one requires a recompile + docker build + rollout.

**User architectural concern:** "It feels wrong that the weights are in the code because 'a person' decided what they should be."

**Resolution — expert-elicitation is correct; adaptability is the gap:**
- Expert-assigned LRs grounded in physics standards are the textbook method when historical failure-rate data is absent (clinical decision support, API RP 581 RBI, FMEA). The methodology survives the hostile engineer *if* each weight cites its standard.
- The real weakness is not "a person decided" — it is that the LR is static regardless of document content, and cannot be updated without a recompile.

**Approved fix (4-sprint re-elevation sequence, Session BL):**

| Sprint | Deliverable | GPU? | Cost |
|---|---|---|---|
| **L1 — Weight metadata migration** | Add columns to `field_intel`: `finding_code`, `lr_base`, `lr_min`, `lr_max`, `lr_source` (citation), `finding_dir`. Refactor `_bayes_discriminate()` to read LRs from DB not dict. Weights become adaptable without recompile. Posterior is unchanged. | No | $0 |
| **L2 — Readable docs + discoverable weights** | Document modal: click any evidence card → see full retrieved document text. Weight provenance panel shows `lr_base` + physics band + citation + Gemma-rated strength → effective LR. Closes the hardcoded-label integrity violation. | No | $0 |
| **L3 — Corpus expansion** | More `field_intel` docs for H1/H2 — some relevant, some noise. Makes retrieval visibly discriminating, reduces "obviously seeded" appearance. | No | $0 |
| **L4 — Gemma extraction + Path A modulation** | Gemma reads retrieved docs → extracts structured findings (replaces hardcoded finding list). Gemma rates assertion strength → `effective_lr = clamp(lr_base × strength_factor, lr_min, lr_max)`. Gemma writes advisory summarization. GPU on for showcase/record only; CPU fallback for dev. | GPU (single L4 node, ~$1.09/hr, showcase only) | ~$2–3/session |

**The trap — never do this:** Do not let Gemma assign LR values. An LLM picking safety-critical probability weights fails the hostile engineer: *"Show me its calibration."* The physics-cited constants are the anchor; Gemma's role is extraction + bounded modulation within those constants.

### H1 vs H2 Rigor Asymmetry

| | H1 Discern | H2 Classify |
|---|---|---|
| Contested artifact | **The posterior %** — "why 93%?" | **The causal chain** — "why paraffin not bearings?" |
| Rigor type needed | Numerical provenance — weight metadata, physics bands, auditable arithmetic | Causal/physical provenance — physics-cited discriminators, readable documents |
| LR metadata needed | **Yes** (L1 sprint) | **No** (no LRs in H2) |
| Readable docs + provenance | **Yes** (L2 sprint) | **Yes** (L2 sprint, different provenance: causal exclusion not LR bands) |
| Gemma's role | Extraction + evidence-strength modulation + chat | Document summarization + causal synthesis |
| Verdict mechanism | **Stays Bayesian math** (never LLM) | Gemma-owned synthesis (no CPU classifier backup; the synthesis IS the verdict) |

### Honest Demo Claim (replaces "the LLM diagnoses your pump")

> *"GDC turns a pile of unstructured field documents into structured findings (Gemma, GPU), fuses them with auditable probability math (CPU), and lets the operator interrogate the result in plain language (Gemma, GPU) — all inside the sovereign perimeter on open weights."*

### GPU Cost Reality

- **Before Session BK:** GPU node pool (3 × g2-standard-8 L4) billed 24/7 even when Ollama deployment was scaled to 0, because node-pool resize and deployment-scale are separate GKE layers. **Cost: ~$78/day idle.**
- **After Session BK fix:** `gpu-start.sh` / `gpu-stop.sh` now resize the node pool (0 ↔ 3), not just the deployment. **Cost when off: $0.**
- **Recommended for L4 showcase:** resize to `--num-nodes 1` per zone → 1 total node (~$1.09/hr) instead of 3 (~$3.27/hr). Single L4 is sufficient for Gemma 4 demo generation. Change `gpu-start.sh` line 43 accordingly.

### Current integrity exposures (as of Session BL)

| Exposure | Status | Sprint |
|---|---|---|
| H1/H2 "cosine sim · pgvector (< 2s)" labels — retrieval not actually executing in replay path | ⚠️ ACTIVE — displayed value ≠ actual value | Closed by L1+L2 |
| H1 `_BAYES_FINDINGS` LR values in code, not DB | ⚠️ ACTIVE — not adaptable without recompile | Closed by L1 |
| H1_METHODOLOGY.md says LRs 8/5/3/2 → 99.6%; deployed code uses 3.0/2.0/1.6/1.4 → ~93% | ⚠️ STALE DOC — code is the more honest/correct version | Fix docs after L1 |

## Related Files
- `gke/fault-trigger-ui/app.py` — all integration points (embedding ~158, intel loop 509–644, agent rec 3625–3774, SSE stream 3780–3943, get_gemma_finding 4957, pgvector retrieval 5145–5171 + 5945–5995)
- `gke/fault-trigger-ui/requirements.txt` — `sentence-transformers==2.7.0`
- `gke/ollama/k8s/ollama.yaml` — the only GPU-requesting workload
- `docs/DEMO_MASTER.md` §3 — L3 capability stack (needs System A/B distinction)
- `docs/H1_METHODOLOGY.md` — Bayesian discrimination methodology
