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

## Related Files
- `gke/fault-trigger-ui/app.py` — all integration points (embedding ~158, intel loop 509–644, agent rec 3625–3774, SSE stream 3780–3943, get_gemma_finding 4957, pgvector retrieval 5145–5171 + 5945–5995)
- `gke/fault-trigger-ui/requirements.txt` — `sentence-transformers==2.7.0`
- `gke/ollama/k8s/ollama.yaml` — the only GPU-requesting workload
- `docs/DEMO_MASTER.md` §3 — L3 capability stack (needs System A/B distinction)
- `docs/H1_METHODOLOGY.md` — Bayesian discrimination methodology
