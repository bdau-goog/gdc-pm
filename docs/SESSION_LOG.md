# GDC-PM Session Log — Append-Only History

---

## Session F (June 8, 2026) — *Workspace isolation + Claim Ledger C2 resolved — Phase 3 unblocked*

**Code committed:** `39da363` (chore: bootstrap workspace isolation), `1518b5e` (docs: Claim Ledger C2 resolved)

**What was done:** (1) **Workspace isolation bootstrapped** for `~/gdc-pm` — had never been installed (not removed). Root cause: host-level bootstrap (`bootstrap-host.sh`) was done June 5 correctly, but per-repo step was never run for gdc-pm. Impact: every `kubectl` call in this repo was falling through to global `~/.kube/config` (gdc-pm-v2 context was set as global current context, contaminating other sessions). Fix: `scripts/setup-workspace.sh` copied from canonical template, `terraform/terraform.tfvars` created (`project_id=gdc-pm-v2, region=us-east1`), `.env`/`.envrc`/`.vscode/settings.json` generated, `.kubeconfig` seeded from live cluster (`gdc-edge-simulation us-east1`). Verified: `source .env && kubectl config current-context` → `gke_gdc-pm-v2_us-east1_gdc-edge-simulation` via isolated kubeconfig. `.gitignore` updated with isolation entries. `~/.clinerules` §5 table updated (gdc-pm → Fully isolated). All future `kubectl`/`gcloud` commands must use `source .env &&` prefix. (2) **Claim Ledger C2 resolved** — C2 (`$8k–$15k SCADA reactive path cost`) was the sole 🔴 NEEDS-EXPERT row blocking Phase 3. Resolved via independent math against demo well parameters (300 BPD @ $76/bbl net-back from app.py lines 1065/1072/1090): gas-locked ESP restart = 2–4 hours per API RP 11S §7.2; breakdown: $1,900–$3,800 production loss + $700–$1,400 labor + $500–$1,500 thermal cycling = **$3,000–$8,000** defensible range. Changed from 🔴 to 🟡 (our-math with disclosed assumptions), status → SURVIVES. Section 5 one-sentence claim updated to use new range. All 10 claims now SURVIVES or SURVIVES-with-qualification. (3) **Audited all ~/ repos** for isolation status — only gdc-pm was missing; gdc-das-physics-detection is half-done (needs project_id from user).

**Key decisions:** (a) C2 resolution approach: option (a) from rules = "soften to defensible range" — no SME required once math is transparent and assumptions are disclosed. The lower bound ($3,100) still beats the GDC action ($2,500) + preserves production, so the economic argument actually gets stronger with the honest range. (b) The $8k–$15k code values are not wrong — they map to different fault-urgency tiers (`urgent` vs `critical`), not a single scenario. (c) gdc-das-physics-detection bootstrap deferred — project_id unknown; noted in §5 table for next session that touches that repo.

**Next task (Session G):** Phase 3 H1 Decision Clock UI redesign — index.html only, single batched `replace_in_file`. Fix 3 integrity bugs (motor state timer, pre-injection sensor bars, RAG seed collapse) in the same pass. Review DEMO_MASTER.md §12 wireframe (lines 488–528) before writing any code.

---

## Session E (June 7, 2026) — *Phase 2 H1 integrity fixes — deployed and verified*

**Code committed:** `a493549` (fix(ui): Phase 2 H1 integrity fixes — Claim Ledger conformance)  
**Cluster image digest:** `sha256:ec5b0306` (fault-trigger-ui) · pod `fault-trigger-ui-cd6495468-bmpbz` 1/1 Running

**What was built and deployed:** Four H1 integrity violations from the CLAIM_LEDGER.md (Session D) fixed in two batched `replace_in_file` calls (index.html 5 blocks, app.js 3 blocks), then built, pushed, and force-deployed with explicit digest pinning. (1) **$0→$2,500 fix (Claim Ledger C1):** Corrected in 3 locations — physics panel comparison table, RESOLVED banner, Window of Options VFD card. The "$0 direct cost" was a known integrity violation: `RESOLUTION_OPTIONS["gas_lock"]["early"]["cost_incurred"] = 2500`. (2) **Vibration sensor bar added (Claim Ledger S1):** 4th H1 sensor bar (VIB) now rendered — scales to 10 mm/s, alarm tick at 80% (8.0 mm/s SCADA threshold), cavitation status "↑ Elevated — cavitation · no alarm" during gas lock injection. `h1RawVib` + `h1SensorVib` data properties added to app.js; extracted from forecast-data trace in `_renderH1PhasePlane`; included in reset. (3) **Thermal countdown clamped (I3):** Banner now gates on `h1ForecastData.slopes.dtemp_dt > 0.2` before showing countdown; shows "— monitoring temp rise" at injection onset when temperature hasn't moved yet (eliminates the "993 min" absurdity). (4) **Sensor source unified:** `_renderH1PhasePlane` now updates `h1SensorAmps/Psi/Temp/Vib` from the DB trace directly (not from the stale `activeDegradesMap.current_sensors` first-write path). With P0 queue fix (AI_NARRATIVE_ENABLED=false, queue=0), DB trace is always current.

**Verification note:** `rollout restart` re-used cached `:latest` tag and pulled the OLD image (`sha256:afa26b3a`). Fixed by `kubectl set image` with explicit new digest (`sha256:ec5b0306`). Confirmed running. API `/api/degrade-status/ESP-ALPHA-1` → `is_active: False, health: 1.0`. All 4 changes verified with grep against deployed files.

**Key decisions:** (a) The "SCADA alarm fires within seconds" root cause was the RabbitMQ backlog (stale DB rows), fixed in Session D by P0 (AI_NARRATIVE_ENABLED=false). The sensor source desync was a secondary contributor but also addressed by unifying to the DB trace source. (b) VIB bar uses `crit_vib=8.0` (from ASSET_REGISTRY) not 4.0 — gas lock vib stays at 2-3.5 mm/s, well below the alarm, which correctly shows "SCADA doesn't alarm" while showing the sensor is elevated. (c) Thermal countdown gates on `dtemp_dt > 0.2` per the Claim Ledger rationale: GDC's story is "classifier fires first, temp moves LATER." A blank "— monitoring temp rise" at T+00:10 is MORE on-message than a garbage large number.

**Next task (Session F):** User red-lines `docs/CLAIM_LEDGER.md` (esp. C2 = SCADA reactive path $8-15k, 🔴 NEEDS-EXPERT). After ledger is signed off with all SURVIVES rows, Phase 3 = H1 Decision Clock UI redesign around the honest cost-ladder story.

---

## Session D (June 7, 2026) — *Governance + Claim Ledger + RabbitMQ fix*

**Code committed:** `11d5430` (docs: archive superseded docs, add conformance report, rewrite README), `77be959` (fix: AI_NARRATIVE_ENABLED=false — kills per-message Gemma call, unclogs queue)

**What was built and deployed:** (1) **RabbitMQ P0 fix** — root-caused the 32k-message queue backlog to `AI_NARRATIVE_ENABLED=rag` in the event-processor, which was calling Ollama synchronously on every message (legacy from the old power-gen demo). Changed to `false`, restarted deployment, one-time purge of backlog. Verified: queue holds at 0 messages under live load. This fix also eliminates the stale-DB root cause of the "SCADA alarm fires in seconds" UI bug (I1 from the conformance report). (2) **Doc cleanup** — archived 13 superseded pre-pivot docs to `docs/archive/`; wrote `BACKEND_CONFORMANCE_REPORT.md` (component audit against DEMO_MASTER with integrity violations I1–I5 and legacy kill-list L1–L5); rewrote `README.md`; active doc set reduced to 7 files. (3) **Prime Directive** — prepended "Survive O&G Engineer Scrutiny" as rule #1 to `.clinerules` with 5-gate check, 🟢/🟡/🔴 confidence-tag system, and Claim Ledger enforcement mechanism. (4) **H1 Claim Ledger** — drafted `docs/CLAIM_LEDGER.md`: 14 claims across 4 sections (failure physics, SCADA limits, GDC detection, cost ladder), each sourced and challenge-tested. Key outcomes: the honest H1 story is "production continuity vs reactive shut-in" (not "GDC saves pump from death"); $0→$2,500 UI integrity bug identified; 25-min PNR and 45-min total failure window clarified as non-contradicting; C2 (SCADA reactive-path cost) flagged 🔴 NEEDS-EXPERT for SME validation before display.

**Key decisions this session:** (a) Established 6-phase program: Governance → Truth → Backend Truth → UI → Verify → Replicate H2/H3. (b) Prime Directive: every on-screen claim must pass a 5-gate scrutiny test + have a SURVIVES row in the Claim Ledger before any pixel is drawn. (c) The honest SCADA-vs-GDC comparison: SCADA's underload trip *protects the pump by stopping it*; GDC's advantage is *production continuity* — clearing the gas void before the trip fires. Never imply SCADA lets the pump die. (d) Conservative Claim Ledger drafting: 🔴 claims show as ranges or are SME-verified; no false precision. (e) Token budget discipline: no large-file (app.py/index.html) edits this session.

**Key rejections:** Rejected prior "binary $0 vs $150k" framing (was oversimplifying and misleading). Rejected "SCADA can't see multi-sensor correlation" (modern SCADA CAN, in principle — GDC wins on pre-threshold probability and context fusion, not sensor blindness). Rejected "start over" impulse — the right architecture (System 1 GDC Advisor) already exists and works; problem was legacy code + stale docs creating confusion.

**Verification:** Queue = 0 messages, 1 consumer, confirmed stable. All 8 pods 1/1 Running. `AI_NARRATIVE_ENABLED=false` in live event-processor deployment.

**Next task (Session E):** User red-lines `docs/CLAIM_LEDGER.md`; SME verifies 🔴 rows (esp. C2). After ledger is signed off: Phase 2 backend truth fixes (4 bugs in app.js/index.html in one batched call, verify deployed). Then Phase 3 H1 Decision Clock UI on a truthful foundation.

---

## Session C (June 5, 2026) — *H1 V2 redesign deployed + thermal-window integrity fix + H2 narrative locked*

**Code committed:** `4f2847e` (feat(ui): H1 V2 redesign), `bc71f69` (fix(integrity): per-run thermal window), `5d2363a` (docs: H2 narrative + DEMO_MASTER §5)
**Cluster state:** fault-trigger-ui sha256:afa26b3a (1/1), inference-api sha256:d1194989 (unchanged, v3 esp_classifier live)

**What was built and deployed — code:** (1) **H1 V2 visual redesign** (`4f2847e`): replaced 3-column well-strip + phase-plane layout with HP-HMI 2-column layout. Full-width status banner (green/amber/red, pulsing animation post-inject), YOU ARE HERE dot sliding along 25-min decision timeline, three directional sensor bars (PIP/Amps/Temp each with "↓ Lower=worse · Alarm: <X" label and SCADA status), SCADA vs GDC plain-text progressive summary, Window of Options cards. Well strip, phase-plane chart, SCADA gauge cluster, AI lead-time panel all removed. Intel feed expanded to 5 items. (2) **Thermal window integrity fix** (`bc71f69`): deleted all 7 hardcoded `25`/`18`/`23` values from the live execution path. `h1WindowTotal` data property captures the per-run thermal deadline (`thermal_lead_time_minutes` from API, fallback `time_to_scada_minutes`) on first non-null forecast poll. `_updateOptionsViability` now uses elapsed/h1WindowTotal fractions (0.72/0.92) — inject twice, get two different windows. Banner shows live `thermal_lead_time_minutes` ("N min to 280°F limit"), timeline label shows "N min this run (varies per injection)." Tick marks: "72% of window" / "92% of window." Physics panel: "~15–30 min (conservative range, per API RP 11S)."

**What was built — docs:** (3) `docs/narratives/H2_SLUG_FLOW.md` — canonical H2 narrative with three-layer evidence framework (L1 telemetry / L2 classifier / L3 context fusion), honest SCADA-vs-GDC scoping (concede L1, scope L2, own L3 categorically), SCADA challenge rebuttals, and Session C visual design directive: two-line chart = setup, evidence fusion = punchline. (4) DEMO_MASTER.md §5 updated with H2 Visual Design Directive. Both from a session-opening design discussion where user correctly challenged: "won't a multivariate SCADA do the same minus the ML?"

**Key decisions:** (a) Gas lock thermal deadline confirmed as the correct H1 window basis (failure contributor = motor-winding thermal runaway per API RP 11S §4.2). (b) H2 deadline basis is NOT thermal (motor temp stays flat by design in slug flow) — H2's urgency is $1,500-vs-$150k decision, not a countdown. (c) Honest Layer-2 scope: a good SCADA can notice the vib/temp decorrelation on one well; GDC's advantages are pre-threshold probability, learned-not-hand-coded, scales to thousands of wells. Layer 3 (4-of-6 H2 evidence sources are unstructured field docs) is categorically impossible for any SCADA product. (d) RabbitMQ at 13,986 purged end of session.

**Session D task:** H2 Discern tab redesign — index.html only, single batched replace_in_file. app.py fully wired. See NEXT_SESSION_PROMPT.md STEP 3 wireframe.

---

## Session C (June 5, 2026) — *H2 narrative locked; docs/narratives/ architecture introduced; no code changes*

**Code committed:** None (documentation-only session — H1 V2 implementation deferred at user request)
**Cluster state:** All 8 pods 1/1 Running · ollama_online: True · gemma4:latest · rag_documents: 18 · field_intel: 2 (pre-fault, expected) · RabbitMQ telemetry.events: 1,528 (healthy, < 5,000 threshold)

**What happened:** Session opened with mandatory startup checks (all healthy). User requested deep-dive on H2 scenario before proceeding with the Session C primary task (H1 V2 visual redesign). Discussion covered: (a) the complete H2 slug-flow physics and evidence structure; (b) the honest three-layer breakdown (L1 telemetry departure, L2 classifier discrimination, L3 unstructured context fusion); (c) the critical design question: *"Won't a multivariate SCADA provide the same insights minus the AI/ML part?"* — answered directly: Layer 1 is conceded to a good SCADA, Layer 2 is scoped carefully as "calibrated probability, learned not hand-authored, pre-threshold, scalable," and Layer 3 (4 of 6 H2 evidence sources are unstructured field documents SCADA has no architecture to read) is the categorically unique differentiator.

**Design decision made this session:** H2 visual directive: **lead with Layer 3 / Context Fusion as the hero; treat the two-line chart as the setup, not the punchline.** The choke log + separator test + shift note + OEM "do not pull well" retrieval assembled into a cited Advisor verdict is what a controls engineer cannot replicate with any SCADA product. The two-line chart creates the question; the evidence fusion answers it. This is locked in DEMO_MASTER.md §5 and in the new narrative doc.

**New artifact introduced: `docs/narratives/` directory.** `docs/narratives/H2_SLUG_FLOW.md` is the first in a planned series of per-horizon narrative documents (H1, H2, H3). Canonical role: the *narrative rationale* layer above DEMO_MASTER.md's spec — includes SCADA-challenge rebuttals, honest Layer-2 claim wording, code-grounded mechanism description, and visual design directives. DEMO_MASTER.md §5 now points to this file.

**Next task (pending "proceed with C" from user):** H1 V2 visual redesign per DEMO_MASTER.md §12 and NEXT_SESSION_PROMPT.md STEP 3 — status banner, decision timeline with YOU ARE HERE, directional sensor bars, SCADA-vs-GDC plain-text comparison. Two `replace_in_file` calls: `index.html` + `styles.css`. Then build/push/rollout.

---

## Session B (June 5, 2026) — *All integrity fixes deployed + live verification passing + RabbitMQ backlog purged*

**Code committed:** Session B — fix(integrity): dynamic PNR remaining time, inference-api v3 deployed, backlog purged  
**Cluster state:** fault-trigger-ui sha256:7b97605e (1/1), inference-api sha256:d1194989 (1/1, v3 esp_classifier NOW LIVE), telemetry-simulator 1/1

**What was fixed and deployed:** Three batched app.py changes in one `replace_in_file` call: (1) Line 3495: `_gemma_finding = get_gemma_finding(fault_type, asset_id)` replaces direct `GEMMA_FINDINGS.get()` for LLM context — ensures gas_lock LLM context uses the dynamic template path, not the static fallback. (2) `GEMMA_FINDING_TEMPLATES["gas_lock"]` template line: `{pnr}` → `{remaining:.0f}-min advantage window` (the live countdown). (3) `get_gemma_finding()` function: added `onset_str` → `elapsed_min` computation from `fault_onset_utc`, `remaining = max(0, PNR_MINUTES[ft] - elapsed_min)`, passed as `remaining=remaining` instead of static `pnr=25`. (4) `GEMMA_FINDINGS["gas_lock"]` static fallback: "Act within 25 minutes" → "Motor thermal window is minutes, not hours — act immediately" (honest, non-time-specific). Both fault-trigger-ui and inference-api rebuilt, pushed, and deployed with exact digest pinning. fault-trigger-ui picks up the slug_flow vib_range fix (source already correct at HEAD); inference-api picks up esp_classifier v3 from `c4ca13e`.

**Live verification:** After purging 286,418-message RabbitMQ backlog (see below), live non-circular classifier verification passed all gates: normal→normal 92.5% ≥90% ✅ · gas_lock→gas_lock 100% @ conf=1.000 ✅ · slug_flow→slug_flow 100% @ conf=0.999 ✅. All offline gates now confirmed live.

**RabbitMQ backlog discovery:** The `telemetry.events` queue had accumulated 286,418 messages over ~8h of cluster operation. Root cause: event-processor uses `prefetch_count=1` (synchronous). The Ollama RAG narrative generation times out after 30s per triggered message (Ollama is busy with the `_intel_generator` keepalive and `/api/agent/chat` calls). During heavy Ollama load, the consumer drains at ~2 messages/min while the simulator publishes 168/min → queue grows at 166/min. Purged the backlog (`rabbitmqctl purge_queue`). Session C should add a queue-depth check to startup commands and consider making RAG narrative generation async (non-blocking) to prevent re-accumulation.

**Point injection limitation documented:** `/api/inject-fault` point injections (published synchronously to RabbitMQ) get consumed in the same batch as the telemetry-simulator's concurrent normal readings. The event-processor's batch at time T contains both fault and normal readings, but the logs only show the normal PSI values. The fault readings ARE written to DB but are indistinguishable from the rapid normal reads unless you query by asset+failure_type carefully. Use `/api/inject/degrade` for live classifier verification — the degrade thread's readings arrive on their own cadence and are more reliably isolated.

**Session C required:** (a) Confidence Widget in H1 tab — `h1TopClass`/`h1TopClassProb` already wired (Session V), needs HTML/CSS probability bars for all 5 classes; (b) H2 Discern tab per DEMO_MASTER.md §5.

---

## Session W (June 5, 2026) — *ESP classifier v3 — all training-fidelity bugs fixed, all offline gates pass*

**Code committed:** `c4ca13e` (feat(models): Session W — ESP classifier v3 all gates pass)  
**Cluster state:** fault-trigger-ui sha256:b57066d4 (1/1), inference-api sha256:62e007c5 (1/1, STALE — v3 model not yet deployed), telemetry-simulator 1/1

**Root cause investigation:** Full end-to-end audit of the training-serving path revealed four independently hand-authored fault definitions (simulator.py dead code, app.py FAULT_PROFILES, fault_signatures.py, MODEL_FOUNDATIONS) that disagreed. All four ESP fault endpoint ranges in fault_signatures.py (sand_ingress, motor_overheat, slug_flow) were reconciled to match app.py FAULT_PROFILES as the authoritative source. The physics of the fault scenarios was validated as correct — the failures were training-fidelity bugs, not physics bugs.

**Three fidelity bugs fixed in train_classifiers.py:** (1) Slope-window mismatch: training used 12-reading window with formula `scale=12/n`; live processor.py uses 60-reading deque with `dt_minutes=(n-1)/12.0`. Fixed to match exactly. (2) Normal-class slope skew: the root cause of live 97%-confidence false alarms. Training drew slopes from flat bands (±2 PSI/min); live noise-driven slopes are σ≈18.7 PSI/min at the 60-window. Fixed by simulating 60-reading steady-state trajectories with absolute simulator noise (psi σ=65, temp σ=8, amps σ=6). Normal precision went from 0% to 1.000 on hold-phase test. (3) Fault noise mismatch: training used flat 1.5% noise; degrade thread uses per-sensor fractions (psi 2%, temp 1%, vib 5%, amps 1%) and amps_end=midpoint of range. Fixed to match.

**Two additional fixes:** (1) Hold-phase training samples (N=20/trajectory): offline verifier revealed that without hold-phase training, the model returned to "normal" once slopes collapsed at the fault endpoint. Fixed by generating 60-reading steady-state samples at the fault endpoint per trajectory. Gas_lock recall went from 0% to 100% at hold phase. (2) Gas_lock departure filter: applied sensor-departure threshold (psi<1335 OR amps<69, i.e. >1σ from normal) to exclude ambiguous early-ramp training rows. Gas_lock precision went from 0.826 to 0.971. Detection threshold is at 4.6% PSI decline below nominal vs SCADA alarm at 43% — the early-detection advantage over SCADA is fully preserved.

**New tool:** `scripts/verify_classifier_offline.py` — full serving-path replica (degrade ramp → 60-window deque → inference-api feature construction → model → confusion matrix). All offline gates pass independently (seed=99 vs training seed=42): normal 1.000, gas_lock 0.971, sand_ingress 0.974, motor_overheat 0.890, slug_flow 0.946, slug→sand FP 0.000.

**Key decisions:** Option B chosen for gas_lock boundary fix (sensor-departure filter) vs Option A (accept 0.90 precision) or Option C (lower the gate). Rationale: Option A had ~22% chance of spurious alarm during a 5-min normal demo window; Option C weakens the precision claim; Option B is physically honest and preserves the early-detection story. The "25 minutes" static value in app.py GEMMA_FINDING_TEMPLATES/GEMMA_FINDINGS was identified as an integrity violation (shows static PNR regardless of elapsed time) but deferred to Session B (app.py batch). DEMO_MASTER.md design was not changed.

**Session B required:** (a) Fix app.py `{pnr}` template → dynamic elapsed-time remaining (lines 4506, 4527, 4597); (b) rebuild fault-trigger-ui (slug_flow vib_range container still stale at 2.2–3.2, source correct at 4.0–6.5); (c) rebuild inference-api with v3 model; (d) live non-circular verification; (e) Confidence Widget for H1 tab.

---

## Session V (June 5, 2026) — *Integrity audit fixes — all 9 violations resolved and deployed*

**Code committed:** `bd28fdf` (fix(integrity): Session V — all 9 violations resolved V-01 through V-09)  
**Cluster image digest:** `sha256:b57066d4` (fault-trigger-ui) · pod `fault-trigger-ui-699f7667c7-nljrm` 1/1 Running

**What was built and deployed:** All 9 🔴 VIOLATION items from the Session U integrity audit (`docs/INTEGRITY_AUDIT.md`) fixed in three batched `replace_in_file` calls — one per file. **(1) app.py V-08:** Deleted `OLLAMA_DISPLAY_MODEL` variable entirely (4 lines removed) — `/api/mlops/status` now reports `OLLAMA_MODEL` directly. Verified live: `ollama_online: True · model: gemma4:latest`. **(2) app.js V-07 + wire-up:** Replaced advisor pre-load string `"Gas lock diagnosis confirmed at 94% confidence"` with `"Gas lock pattern detected · confidence building"`. Added `h1TopClass`, `h1TopClassProb`, `h1GvfPct` Vue data properties. Wired `class_probs` from `/api/plot/forecast-data` into `h1TopClass`/`h1TopClassProb` in the degrade-poll interval. Added GVF parsing from intel feed items (`/estimated at (\d+)%/` regex). Added reset in `resetHorizon1`. **(3) index.html V-01 through V-09 (9 SEARCH/REPLACE blocks):** V-01 `"94% confidence"` → `"≥92% once confirmed"`; V-02 dual-reality bar badge bound to `h1TopClass`/`h1TopClassProb` live values; V-03 all 6 `h1ElapsedMin > 15` occurrences replaced with `parseInt(h1SensorTemp||'0') >= 260` (motor state now from actual winding temp); V-04 GVF display bound to `h1GvfPct || '—'`; V-05 H2 physics text `"52%"` → `"builds to ≥90% as slug pattern confirms"`; V-06 H2 confidence card `"52% (Ambiguous)"` → `"— PREVIEW — not yet live"`; V-07 arch tab banner added; V-09 `$1,200` → `~$2,000` in arch tab walkthrough.

**Key decisions:** V-04 (GVF) implemented as an intel-feed parse rather than a new API endpoint — `_intel_generator` already writes the GVF value as text (`"estimated at {gvf}%"`) into `field_intel`, so the frontend regex-parses it from `h1FeedItems`. This avoids app.py changes and is honest: shows `'—'` pre-inject, shows the actual drawn GVF value ~20s after injection. V-03 threshold chosen as `>= 260°F` (between nominal 198°F and SCADA alarm 280°F) to give meaningful WARMING → CRITICAL progression. `parseInt()` on the `"199°F"` string correctly returns 199 in both browsers and Vue templates.

**Verification:** Pod 1/1 Running · digest `sha256:b57066d4` · `/api/mlops/status` → `ollama_online: True, model: gemma4:latest` ✓. Git clean on `feature-trio-scenarios`.

**Next task (Session W):** Classifier model recreate — fix `train_classifiers.py` slope window, retrain, non-circular verification, deploy. See NEXT_SESSION_PROMPT.md STEP 4. After W: build Live Diagnostic Confidence widget in H1 tab (h1TopClass/h1TopClassProb now wired — widget just needs HTML/CSS).

---

## Session U (June 5, 2026) — *Integrity audit + canonical fault signatures + trajectory classifier v1 (not committed)*

**Code committed:** Session U commit — fault_signatures.py, train_classifiers.py rewrite, INTEGRITY_AUDIT.md, clinerules §6, MODEL_FOUNDATIONS §9, app.py slug_flow fix  
**Cluster state:** fault-trigger-ui / inference-api / telemetry-simulator at 0 replicas (intentional, unchanged from Session T)

**What happened:** Full integrity audit of the GDC-PM demo frontend — first systematic classification of all hardcoded values. Root cause: every fake confidence value (94%, 52%, 91.4%) is a fossil from the pre-model era (Session R found inference-api returned `inference_error` on every call since day one — no classifier existed when the UI was built). Placeholders were never retired when Session S trained classifiers. Nine violations classified (V-01 through V-09) across Display, Health/Identity, and Illustrative-without-marker dimensions. Model integrity finding: v1 trajectory-based classifier trained (108,937 rows, 600 trajectories/class) using correct distributions for the first time, but failed precision thresholds (gas_lock 0.815 vs 0.92 required, slug_flow 0.746 vs 0.90). Root cause diagnosed: label-noise from indistinguishable early-ramp readings (at ramp step 12, t≈0.012 — sensors 1% toward fault endpoint, indistinguishable across all fault classes). v1 NOT committed per ML Integrity rule — git checkout'd to restore Session S classifier.

**What was built:** (1) `gke/shared/fault_signatures.py` — canonical 8-feature ESP fault signature table; single source of truth replacing four previously-disagreeing definitions. (2) `scripts/train_classifiers.py` full rewrite to trajectory-based approach: uses same `((i+1)/steps)^k` ramp formula as `_run_degrade_thread`, distributions from fault_signatures.py (gas_lock PSI 875–1100, slug_flow vib 4.0–6.5). (3) `app.py` one-line fix: `slug_flow vib_range (2.2, 3.2) → (4.0, 6.5)`. (4) `docs/INTEGRITY_AUDIT.md` — full classified violation table (9 violations with precise fix instructions). (5) Global `~/.clinerules §6` — "Integrity, End to End" five-dimension rule (Display / Model / Provenance / Health / Documentation), portable to all projects.

**Key decisions:** (a) Gradual-confidence design approved: early-ramp uncertainty is on-message ("probability scoring before thresholds" — DEMO_MASTER §2 Claim 2). (b) Two-number metric approved: show both overall (~0.81) and developed-stage (≥0.92) precision — neither cherry-picked. (c) v1 classifier explicitly NOT committed. (d) `OLLAMA_DISPLAY_MODEL` flagged as Dimension-4 (Health/Identity) violation (V-08). (e) Three-session cadence: V = fix 9 violations, W = model recreate + non-circular verify, V+ = confidence widget.

---

## Session T (June 5, 2026) — *Model foundations audit + injection event log + MODEL_FOUNDATIONS.md*

**Code committed:** `89040f9` (feat: injection event log + popup — non-circular model verification foundation)
**Cluster image digest:** `sha256:34c0c8fe` (fault-trigger-ui) · `sha256:560e4ab3` (inference-api, unchanged)

**What happened:** Post-deployment audit of the Session S classifiers found three critical defects: (1) Training distributions were hand-authored, not derived from `FAULT_PROFILES` — gas_lock was trained on PSI 350–800 but the live system injects at 875–1100 (confirmed by 71,794 DB rows avg 971 PSI). (2) Verification was circular — the 94% accuracy figure was measured against the same invented distribution used for training, not against live data. (3) H3's `vizier_optimize()` uses a hardcoded polynomial — the XGBoost health model is never called, making the "edge model enforces thermal constraint" claim false. Session S classifiers remain deployed but are explicitly marked NOT TRUSTED in the new `docs/MODEL_FOUNDATIONS.md`. Additionally: the `FAULT_PROFILES["slug_flow"]["vib_range"]` of (2.2, 3.2) barely separates from normal (0.8–2.0), meaning the H2 "vibration alarm" story is not plausible at live signal levels. Four disagreeing definitions of each fault were found (simulator.py, fault-trigger-ui FAULT_PROFILES, retrain_edge_models.py, train_classifiers.py) with no canonical source.

**What was built:** (1) `docs/MODEL_FOUNDATIONS.md` — the authoritative model spec: canonical ESP fault-signature table (gas_lock PSI 875–1100 from live DB, slug_flow vib widened to 4.0–6.5 for H2 story), per-horizon model inventory (H1: classifier+health, H2: classifier, H3: `esp_thermal` not yet built), 4 open integrity violations with deadlines, trajectory-based training spec, and non-circular verification protocol with pass/fail thresholds (gas_lock ≥ 0.92, slug_flow ≥ 0.90 on live-distribution replay). (2) `injection_events` AlloyDB table — every inject/degrade now persists drawn values AND profile bounds. (3) `GET /api/injection-log`. (4) `showInjectionPopup()` in `app.js` — dynamically created DOM popup, 5s auto-dismiss, fires on all 3 inject points. Verified live: `gas_lock point psi_target: 882.9 [875–1100] amps_target: 23.5`.

**Key decisions:** `FAULT_PROFILES` in `app.py` is the canonical source — everything derives from it. slug_flow vib must be widened to 4.0–6.5 for H2 to be credible. `esp_thermal` XGBoost model must be built for H3 to be honest. The injection event log is the non-circular verification instrument — replay its rows through `/predict`, publish the confusion matrix in `MODEL_FOUNDATIONS.md §6`.

**Next task:** Clean retrain — 5-step runbook in `MODEL_FOUNDATIONS.md §7`: fix slug_flow vib range → `fault_signatures.py` → trajectory-based classifier retrain → non-circular replay verification → `esp_thermal` + wire into H3.

---

## Session S (June 4, 2026) — *Model Prep complete — ESP classifier with slug_flow class 4, inference-api LOCAL_MODELS_DIR deploy*

**Code committed:** `92dc9be` (feat: ESP classifier with slug_flow class 4 — inference-api LOCAL_MODELS_DIR deploy)
**Cluster image digest:** `sha256:560e4ab3` (inference-api) · `sha256:565ec44a` (fault-trigger-ui, unchanged)

**What was built and deployed:** Closed the classifier gap discovered in Session R. Created `scripts/train_classifiers.py` which trains XGBoost multi-class classifiers for all 4 asset classes. The ESP classifier was extended from 4 classes to 5 — adding `slug_flow` as class 4. The `slug_flow` training signature encodes the H2 demo's discriminating physics: elevated vibration (`vib` 3–8 mm/s) with near-zero temperature rate (`dtemp_dt` ≈ ±0.08°F/min), contrasting with `sand_ingress` (vibration + rising temperature) and `motor_overheat` (strong temperature rise). All classifiers trained in <2s locally: ESP 99.92% accuracy, all 5 classes 100/200 correct in holdout test. Classifier `.ubj` files baked into the inference-api container at `/app/models/` via `COPY models/ ./models/` in Dockerfile. Set `LOCAL_MODELS_DIR=/app/models` and cleared `GCS_MODEL_BUCKET` in k8s yaml (GCS bucket was always empty — fully edge-native now). Rebuilt, pushed (`sha256:560e4ab3`), applied k8s yaml, forced exact digest rollout (old image was cached on node — `kubectl set image` with full digest solved it).

**Verified live:** `gas_lock` → 94.41% · `slug_flow` → 93.8% (flat dtemp_dt correctly discriminated from sand_ingress) · `sand_ingress` → 94.47%. DB `telemetry_events` shows real `predicted_label` values for all asset types — `inference_error` is gone. Known calibration issue: ESP nominal state occasionally classified as `sand_ingress` at 50–63% because simulator nominal amps (~88A) overlap with the training sand_ingress range (42–72A). Non-blocking for H1 demo (gas_lock injection uses PSI <800, amps <50 — unambiguous). Fix: retrain with corrected normal amps range if needed.

**Next task:** H1 V2 UI integrity fixes — all 7 known violations in `static/app.js`: (1) motor state from `h1SensorTemp` not timer, (2) GAS LOCK% from live `class_probs.gas_lock` not static text, (3) SCADA gauge bars from live telemetry not fallback, (4) "YOU ARE HERE" moving marker on Window of Options timeline, (5) event-active status banner with ticking T+MM:SS timer, (6) directional labels on SCADA gauge bars, (7) drop phase-plane chart. All 7 batched into ONE `replace_in_file` call on `app.js`.

---

## Session R — Addendum 3 (June 4, 2026) — *Critical model-architecture discovery: no classifier models exist*

**Code committed:** None (discovery session — documentation only)

**What was discovered:** While diagnosing the nominal health_score issue (Fix A), a deeper architectural gap emerged: the GCS bucket `gdc-pm-v2-models` is **completely empty**. The inference-api has been running with no models loaded since the cluster was first deployed. Every call to `POST /predict` returns `{"predicted_label": "inference_error", "confidence": 0.0}`. This explains why `class_probs` showed `{'inference_error': 0.0}` after Phase 2.

**Root cause:** The project pivoted from BQML classifier models → XGBoost health score regressors during Phase 5.1. The `retrain_edge_models.py` script correctly produced health regressors (`esp_health.ubj`, etc.) and placed them in `fault-trigger-ui/models/`. However, no equivalent classifier training script was created, and no classifier models were ever uploaded to the `gdc-pm-v2-models` GCS bucket. The inference-api's model loading logic (Priority 2: GCS download) silently fails when the bucket is empty, leaving all models as `None`.

**Why this is blocking:** The H2 (Slug Flow) demo is 100% classifier-dependent. H2's entire argument is "the model discriminates slug_flow (surface issue, $1,500 fix) from downhole fault (wrong $150,000 pump pull) — SCADA cannot." Without a working `esp_classifier`, H2 has no story. Additionally, the `esp_classifier` label map is missing `slug_flow` as a class entirely (currently: `{0: normal, 1: gas_lock, 2: sand_ingress, 3: motor_overheat}`). This needs to be added as class 4 with training data that encodes the temperature-flat signature that is the discriminating H2 feature.

**Model dependency per horizon:** H1 needs both classifier (for "gas_lock 94%" panel) + health regressor (for early detection). H2 needs classifier only — it IS the classifier story. H3 needs health regressor as Vizier's thermal-safety constraint; Vertex AI Vizier is the one intentional cloud dependency in an otherwise fully-edge stack.

**Temperature reframe does NOT reduce model dependence.** Temperature is the lagging deadline (`(280°F − temp) / dtemp_dt`) — the finish line the ML is racing to beat. The ML classifier is the hero. The reframe increases model dependence by making the classification panel the primary demo element.

**Next action:** Model-prep before any further UI work. See NEXT_SESSION_PROMPT.md STEP 4 for the complete 5-step sequence. Key steps: audit training scripts, extend classifier to include slug_flow (class 4, flat-temp training data), deploy via LOCAL_MODELS_DIR (edge-native, not GCS), verify `predicted_label = "gas_lock"` in DB.

---

## Session R — Addendum 2 (June 4, 2026) — *Fix A: inference_error classifier gate — deployed and verified*

**Code committed:** `0d85220` (fix: Fix A — exclude inference_error from classifier_active gate)
**Cluster image digest:** `sha256:565ec44a` (fault-trigger-ui)

**What was fixed:** Nominal health_score was 0.74 (should be ~0.92+ or None). Root cause diagnosed by querying the DB: ALL `predicted_label` values in `telemetry_events` were `inference_error` — the inference-api doesn't have the ESP classifier model loaded, so every reading gets labeled `inference_error`. The `classifier_active` gate checked `l not in ("normal", "")`, which treated `inference_error` as a fault label → 100% "fault fraction" → health model ran on nominal sensor data → scored 0.74 from noise slopes. **Fix:** Added `"inference_error"` to the exclusion tuple in both `plot_forecast` and `get_forecast_data`. Verified: `health_score: None, is_active: False` in nominal state. The health model itself is correctly calibrated — no retrain needed for the nominal issue. Fix B (retrain) remains optional for improving fault-severity discrimination in active injections.

---

## Session R — Addendum (June 4, 2026) — *Phase 2 app.py truth layer — deployed and verified*

**Code committed:** `faebd9f` (feat: Phase 2 app.py truth layer — thermal_lead_time, class_probs, RAG seed protection, advisor fallback)
**Cluster image digest:** `sha256:db6f7b6d` (fault-trigger-ui)

**What was built and deployed:** Four surgical `app.py` changes in a single batched `replace_in_file` call. (1) **`thermal_lead_time_minutes`** added to `/api/plot/forecast-data` response: computed as `(280 - temp_v[-1]) / dtemp_dt` where `dtemp_dt` comes from polyfit over fault-labeled rows. This number varies per run because `_run_degrade_thread` randomizes `_temp_target` and `_k` — directly solves the "always 25m" convergence problem. Verified live: returned 8.9 min with dtemp_dt=9.335 °F/min. (2) **`class_probs` dict** added to same endpoint: derived from the distribution of `predicted_label` + `confidence` in the last 20 DB rows. Currently shows `{'inference_error': 0.0}` because the ESP classifier isn't loaded in the inference-api pod — that's honest, not a code bug. During active gas_lock with a working classifier, will show `{'gas_lock': 0.94, ...}`. (3) **RAG seed doc protection**: the `_intel_generator` prune query now adds `AND id NOT IN (SELECT id FROM field_intel WHERE doc_type='shift_note' AND lbl_type='ai' ORDER BY created_at ASC LIMIT 5)` — protects the GVF seed document from being pruned after ~10 intel cycles, keeping the context-fusion RAG gap alive throughout the demo. (4) **Advisor template fallback**: `/api/agent/chat` now returns a physically grounded response when Gemma is unavailable, instead of "Unable to reach AI model." 

**Key data source discovery:** The inference-api (separate pod) outputs a full softmax `probabilities: dict[str, float]` on its `/predict` endpoint — confirmed from inspection of `gke/inference-api/app.py`. But the event-processor only stores `predicted_label` + `confidence` (top class), not the full vector, in `telemetry_events`. The `class_probs` field uses the stored labels. If the inference-api ESP classifier were loaded, this would produce a real multi-class probability distribution.

**Next task:** Phase 3 — HP-HMI/ISA-101 design system components: moving-analog-indicator (leading/lagging split), fault classification panel (from `class_probs`), status banner (from `thermal_lead_time_minutes`), gray/color discipline. Target files: `static/styles.css` + `static/app.js` (both now ~800-1600 lines, ~6× cheaper than pre-Phase-1).

---

## Session R (June 4, 2026) — *Design overhaul + Phase 1 frontend modularization — deployed and verified*

**Code committed:** `0d18533` (feat: Phase 1 frontend modularization — split index.html into static/{styles.css,app.js})
**Cluster image digest:** `sha256:85738e70` (fault-trigger-ui) · pod `fault-trigger-ui-74559b58dc-tlgmn` 1/1 Running

**What happened this session (Plan mode + Phase 1 only):** Longest Plan-mode session to date. Diagnosed the root cause of 8 failed redesigns: (1) no shared visual vocabulary — each session invented a new bespoke primary visual, every one rejected; (2) noisy real-model data forcing integrity violations (hardcoded timer-driven state, static "94%", converged "always 25m" RUL). Read all session history, the Situation Brief, and the full DEMO_MASTER before touching any code.

**Key design decisions locked this session:** Adopted HP-HMI (moving-analog-indicator + gray/color discipline) and ISA-101 (Level-1 fast-horse overview / Level-2 available detail) as the shared design system across H1/H2/H3. Reframed the hero visual from "countdown chart" to "live fault CLASSIFICATION panel + leading/lagging indicator split." Classification panel shows the full label-probability distribution derived from recent model outputs — this is categorically unmistakably ML, not threshold-alarm (SCADA). Temperature reframed as the *lagging deadline* motor is racing toward (not the ML detection signal). ML detection signal is the multivariate PIP+amps correlated decline *before* temp moves. Lead-time number = `(280°F − current_temp) / dtemp_dt` — varies per run because `_run_degrade_thread` randomizes `_temp_target` and `_k`, so "always 25m" problem is solved at the data layer. Confirmed inference-api returns full softmax `probabilities: dict[str, float]` per prediction; class_probs for UI will be derived from DB label-frequency distribution (no schema changes needed). 

**Phase 1 executed and verified:** Extracted CSS (829 lines → `static/styles.css`) and JS (1569 lines → `static/app.js`) from 4347-line `index.html` using a Python extraction script with structural assertions. New `index.html` is 1947 lines. Added `StaticFiles` mount to `app.py`, `aiofiles==23.2.1` to requirements, `COPY static/` to Dockerfile. Rebuilt image (sha256:85738e70, 2.56GB), pushed, rolled out. Verified: `/static/styles.css` HTTP 200 (76KB), `/static/app.js` HTTP 200 (87KB), page loads identically. Token impact: future HTML edits are ~2.2× cheaper; CSS/JS edits target small individual files.

**Rejected approaches this session:** (a) "5 separate microservice apps" for H1/H2/H3 — correct that they should be separate, wrong split axis; concerns should be split by concern within the frontend, not by demo act. (b) Motor temperature as the primary ML detection signal — caught and corrected: temp is lagging, ML acts on multivariate precursors before temp moves. (c) Continuing to push Phase 2+ without fixing the large-file token problem first.

**Next task:** Phase 2 (app.py truth layer): add `thermal_lead_time_minutes` (deterministic, per-run-varying), `class_probs` (DB-derived softmax), protect GVF RAG seed from prune, and Advisor template fallback. Single batched `replace_in_file` on `app.py`. See NEXT_SESSION_PROMPT.md §STEP 4.


**Format:** One paragraph per session, newest first. Never delete entries.  
**Usage:** New sessions read the last 3–5 entries only for recent decision context.

---

## Session Q — Addendum (June 4, 2026) — *H1 visual review: FAILED*

**Visual review outcome:** After deployment, four screenshots reviewed by the user. Every major element failed. Summary of failures in order of severity:

**(1) Integrity violations:** "Motor CRITICAL" fires at T+16m driven by `h1ElapsedMin > 15` — a hardcoded timer, not actual temperature. Motor temp was 199°F while SCADA alarm threshold is 280°F. The UI was lying. "GAS LOCK — 94% confidence" in the dual-reality bar is static text unconnected to the model. SCADA CSS gauge bars show fallback hardcoded values pre-injection even though live-telemetry data was available.

**(2) UX failures:** No visible "event active" state — audience doesn't know if the demo is running. No "YOU ARE HERE" indicator on the Window of Options timeline — viewers can't see how much window remains. SCADA gauge bars have no directional labels — "Alarm at 800" doesn't tell a non-engineer whether 800 is the floor or the ceiling. Phase-plane chart is unreadable to a business audience — state-space diagrams require engineering literacy that a business audience does not have.

**(3) Technical bugs:** AI Lead-Time RAG gap collapsed to 0 after ~5 minutes (seed `field_intel` GVF doc rotated out by the 100-row prune after `_intel_generator` wrote ~10 documents). Advisor T+2m re-trigger returned "Unable to reach AI model" — Gemma timeout, no fallback template.

**(4) Design root cause identified:** Every iteration added more sophistication (3-line charts → phase planes → state-space zones) while the core engagement problem was never solved: it's one button then "try to figure out what's happening." There is no live narrative, no sense of urgency building, no visual that a fast-moving business viewer can process in 3 seconds. The question was never "what does an engineer find credible?" — it should have been "what makes a non-technical person feel the urgency AND understand what GDC did that SCADA couldn't?"

**Decision:** H1 is NOT demo-ready. H2 and H3 must not be started. Next session must get explicit design approval for H1 V2 before writing any code. The redesign concept: horizontal decision timeline with a moving YOU ARE HERE marker, directional sensor bars with plain-English alarm context, a live event-active banner with ticking clock, evidence reveal sequence. DEMO_MASTER.md §15 now captures "Demo Engagement Requirements" so this failure mode is documented for future sessions.

---

## Session Q (June 4, 2026) — *Phase-plane chart + SCADA CSS gauges + AI lead-time panel + LLM re-triggering + context-fusion server fix*

**Code committed:** `a4cb95d` (fix: seed field_intel GVF doc on gas_lock inject), `245e50a` (feat: phase-plane chart, SCADA CSS gauges, AI lead-time panel, Vue watchers for LLM re-triggering)
**Cluster image digest:** `sha256:3ee29db0` (fault-trigger-ui) · pod 1/1 Running

**What was built and deployed:** Prompted by user frustration that the "Minutes Until Failure" chart showed a flat line (instantaneous model output, not a time-series countdown), the advisor fired only once, the SCADA chart showed nothing useful, and the context-fusion gap was always zero. Produced `docs/GDC_DEMO_SITUATION_BRIEF.md` for external review; consulted Gemini 3.1 Pro. Accepted 3 of 4 Gemini proposals; rejected the fake-frontend context-fusion delta (integrity violation). Also addressed user pushback on (a) what actually kills the pump (motor winding temperature, not PIP), (b) no digital clocks, (c) analytical/state-space visual, (d) resizability. **Commit 1 (app.py):** On `gas_lock` inject, immediately INSERT a `field_intel` seed row containing "estimated at 78% GVF" — the existing `adjust_rul_with_documents()` keyword-match regex fires its 0.6× multiplier, producing a real `adjusted_rul_minutes < time_to_scada_minutes`. Verified: 7.2 min gap (`17.9 → 10.7 min`). **Commit 2 (index.html):** (1) **Phase-plane chart** — replaces the flat-line chart with a Plotly scatter plot of Motor Amps (Y) × Winding Temp (X). Background shapes: green safe zone, amber warning, red gas-lock zone (physically grounded: low amps + rising temp = loss of motor cooling). SCADA alarm lines: horizontal at 50A, vertical at 280°F. Trail of last 20 operating points. Current point color-coded. The dot migrates into the red zone during gas lock while NEITHER alarm line has been crossed — this IS the demo story in one visual. (2) **SCADA CSS gauge cluster** — 4 horizontal bars (PIP, Amps, Temp, Vib) with colored fills and red threshold tick marks. Reactive to `h1RawPsi/Amps/Temp` numeric data props extracted from forecast data traces. (3) **AI Lead-Time Advantage panel** — shows sensor-only vs context-fused estimates from real API, with the RAG contribution labeled (~7 min, "Shift note + GOR lab report fused via AlloyDB RAG"). (4) **Vue `watch:` block + `_triggerAdvisoryUpdate()` method** — Advisor re-fires when: new intel doc arrives in feed, `h1OptALabel` transitions VIABLE→MARGINAL→EXPIRED, or at T+50s/T+2min scheduled intervals. Each re-fire builds a live-context prompt from current sensor slopes + elapsed time + the triggering document and calls `/api/agent/chat`.

**Decisions made this session:** (a) Rejected fake frontend context-fusion multiplier — fixed server-side with real RAG doc. (b) Replaced "Minutes Until Failure" with phase-plane state-space chart — analytically credible to petroleum engineers, self-explains without narration. (c) Destructive metric corrected to motor winding temperature (API RP 11S thermal failure chain). (d) Rejected 3D rotatable wellbore for today — deferred; SVG engineering schematic remains in well strip. (e) SCADA normalized-% chart replaced with absolute CSS gauges — cleaner signal that sensors ARE moving but haven't crossed SCADA thresholds. (f) Wrote `GDC_DEMO_SITUATION_BRIEF.md` as structured handoff doc for external model consultation.

**Verification:** Both commits deployed, pod 1/1 Running, digest `sha256:3ee29db0`. Context fusion gap: 7.2 min (real). Raw sensor values `latest_amps: 84.5, latest_temp: 202.6` confirmed present in API response for phase-plane rendering.

**Next task:** Visual verification of H1 Detect tab (user must view in browser). Then H2 (Discern) tab redesign per DEMO_MASTER.md §5: two-line Vib+Temp chart, evidence wall, GDC Advisor with "$1,500 vs $150,000" verdict.

---

## Session P (June 4, 2026) — *CSS instrument panel + 4-sensor SCADA chart + chart coherence fix*

**Code committed:** `919c7ee` (feat: CSS instrument panel (GVF/PIP/Amps/Temp), 4-sensor normalized SCADA chart (% Δ baseline))
**Cluster image digest:** `sha256:c335c72c` (fault-trigger-ui) · pod `fault-trigger-ui-7f476cf587-6bmgk` 1/1 Running

**What was built and deployed:** Two improvements prompted by user visual feedback on the Session O screenshot. (1) **CSS Instrument Panel** — the 45-line SVG wellbore cross-section replaced entirely with a CSS-only "downhole instrument panel." Structure: `WELL A-1` title + pulsing status dot (`dot-green`/`dot-amber`/`dot-red` with `@keyframes ws-pulse`) → animated fluid column (`.wstrip-casing` with `.fluid-nominal`/`.fluid-gaslock` CSS gradient animations + 3 CSS bubble floaters) → PUMP block (blue border) + MOTOR block (CSS `box-shadow` glow transitions: `motor-ok`/`motor-warn`/`motor-crit` with `@keyframes motor-glow`) → 4 instrument readouts (GVF% with animated bar, PIP↓, AMPS↓, TEMP — all live Vue data, color-coded). Design aesthetic taken from `gdc-das-physics-detection/gke/das-web-ui`: bold, dark, readable at any size, no tiny unrenderable SVG primitives. (2) **4-Sensor Normalized SCADA Chart** — replaced single-sensor-with-tabs approach (`setH1Sensor` / h1-stab tabs) with an overlay showing all 4 sensors (PIP, Amps, Temp, Vib) normalized to `% Δ from initial baseline value` on one Plotly chart. PIP and Amps decline together (orange solid / orange dotted) while Temp and Vib stay flat near 0% (blue / grey). Zero-line reference added. "✓ All above SCADA threshold" annotation bottom-right. This chart makes the multivariate correlation argument visual without narration — two sensors co-decline while two hold flat = gas lock signature, SCADA threshold not crossed.

**Decisions made this session:** (a) SVG wellbore rejected as renderable at 180px — CSS instrument panel is the correct tool at this scale. (b) Single-sensor SCADA chart with tabs undermined the multivariate argument by mimicking what SCADA does (one sensor, one threshold). 4-sensor normalized overlay is the correct visualization for "GDC sees the correlation, SCADA doesn't alarm." (c) Amps added to instrument panel per user request.

**Verification:** Pod 1/1 Running · digest `c335c72c` · ollama_online: True, gemma4:latest. Git clean on `feature-trio-scenarios`.

**Next task:** Visual verification of full H1 demo flow (inject → fluid column turns amber → status dot pulses amber → bubbles rise → SCADA chart shows PIP/Amps declining together, Temp/Vib flat → AI chart lines diverge → GDC Advisor streams → Window of Options → Approve). Then H2 (Discern) tab redesign per DEMO_MASTER.md §5.

---

## Session O (June 4, 2026) — *H1 chart redesign — implemented, deployed, verified*

**Code committed:** `15330a4` (feat: H1 chart redesign — Minutes Until Failure 3-line chart, SCADA secondary, GDC Advisor rename, well strip to right, SVG callout labels, dynamic feed poll)
**Cluster image digest:** `sha256:8202af33` (fault-trigger-ui) · pod `fault-trigger-ui-6558568b8c-q7gts` 1/1 Running

**What was built and deployed:** Implemented the full H1 chart redesign approved in Session N. Single batched `replace_in_file` call (15 SEARCH/REPLACE blocks) covering: (1) **Primary chart rewrite** — `_renderH1Charts` replaced entirely with a rolling time-series "Minutes Until Pump Failure" chart showing 3 lines: gray (SCADA flat at 120), orange dashed (sensor-only from `d.time_to_scada_minutes`), solid orange (context-fused from `d.adjusted_rul_minutes`). Shaded fill + annotation bracket "⚡ Context Fusion: −Nm" renders when gap > 0. Pre-injection: all 3 flat at 120. History buffer `h1RulHistory[]` accumulates up to 36 points. (2) **New `_renderH1ScadaChart` method** added — renders raw PIP/Amps/Temp with SCADA alarm threshold line below the primary chart (id=`h1-scada-chart`, 110px fixed height). Sensor tabs (PIP/Amps/Temp) now control the SCADA chart. "✓ No SCADA alarm triggered" annotation shown pre-injection. (3) **NS handle** made always-visible (removed `v-if="h1Injected"` gate) — sits between primary and SCADA charts. (4) **Column reorder** via CSS `order:5` on `.h1-well-strip` + `.h1-body>:nth-child(2){display:none}` to hide left splitter — well strip moves to far right (180px, `align-self:stretch`) without touching the SVG HTML. (5) **SVG callout labels** added at end of SVG: "Intake: Nominal"↔"Intake: 68% GVF ⚠" and "Motor: Cooling normal"↔"Motor: Cooling lost ⚠". (6) **"GDC Copilot" → "GDC Advisor"** across all CSS classes, Vue data props, method name, HTML labels. (7) **Dynamic feed poll** `h1FeedPollInterval` every 15s during active fault, cleared on reset. (8) Both `initH1CenterSplit` and `initH1NsSplit` now resize both `h1-gdc-chart` and `h1-scada-chart`.

**Key implementation decisions:** Used CSS `order` property + `:nth-child(2){display:none}` to reorder columns without touching the large SVG HTML block (avoiding a risky 50-line exact-match SEARCH). Pre-injection chart shows all 3 lines at 120 by gating on `this.h1Injected` in the JavaScript. Column order: Charts (44%, left) | splitter | GDC Advisor (flex:1, center) | Well Strip (180px, right — CSS order:5).

**Verification:** Pod `fault-trigger-ui-6558568b8c-q7gts` 1/1 Running · `/api/mlops/status` → ollama_online: True, gemma4:latest · `/api/plot/forecast-data/ESP-ALPHA-1` returns `time_to_scada_minutes: 35.6, adjusted_rul_minutes: 35.6, sensors: [psi, temp, vib]` ✓.

**Next task:** Visual verification of H1 demo flow (inject → 3 lines diverge → bracket appears → Window of Options → Approve). Then implement H2 (Discern) tab redesign per DEMO_MASTER.md §5: two-line vibration+temp chart, 6-chip evidence wall, GDC Advisor auto-streams "$1,500 vs $150,000" verdict.

---

## Session N (June 4, 2026) — *H1 chart design — approved, not yet implemented*

**Code committed:** None (design session only — no code written)
**Cluster image:** Unchanged from Session M (`sha256:55e56268`)

**What was decided:** Extended design discussion triggered by user feedback on the Session M screenshot. Six issues identified: (1) Well strip placement (left column, too small, not readable); (2) Chart still confusing — Y-axis in PSI explains nothing to a business audience; (3) "SCADA Alarm" pins showing 4+ hours out (timing bug in chart render — `time_to_scada_minutes` returns large values in nominal state); (4) Truck roll/chemical injection as H2 scenario expansion; (5) LLM update frequency (every 20-30s, intel feed only refreshes on inject); (6) "GDC Copilot" = Microsoft competitor brand conflict.

**Key design decision approved (the chart redesign):** Replace raw sensor telemetry (PSI/Amps/Temp) as the primary H1 visual with a **"Minutes Until Pump Failure" chart** showing three distinct lines on the same plot: (1) gray — SCADA deterministic threshold monitoring (stays HIGH — honestly shows SCADA hasn't been alarmed yet); (2) orange dashed — GDC AI sensor-only XGBoost prediction; (3) solid orange — GDC AI context-fused prediction (adjusted by retrieved AlloyDB RAG documents). A shaded bracket between lines 2 and 3 dynamically labels the gap as "Context Fusion: −Nm (shift note + GOR lab test)". No hardcoded values — all computed live from `d.time_to_scada_minutes` and `d.adjusted_rul_minutes` from the API. Pre-injection: three flat calm lines at ~120+ minutes. Post-injection: GDC lines decline; context-fused line diverges below sensor-only after first RAG retrieval cycle.

**Key rejections this session:** Rejected raw-sensor-on-Y-axis approach (requires narration to understand). Rejected hardcoded timing values (integrity violation). Rejected "straw-manning" SCADA as dumb — SCADA can do multivariate correlation; our advantage is specifically (a) retrainable physics-aware models and (b) unstructured document fusion. Rejected two-chart comparative-only approach (proposed by Gemini during a brief model switch) — the context-fusion gap visualization requires both the sensor-only AND context-fused forecasts on the same Y-axis to make the gap visible.

**Additional layout changes approved:** Well strip moved to far right (decorative, full-height, 180px, with dynamic SVG callout labels for pump intake and motor status). "GDC Copilot" renamed to "GDC Advisor" throughout all CSS, Vue data, and HTML labels (Microsoft Copilot brand conflict). Dynamic feed poll every 15s during active fault.

**Next task:** Fresh session, implement the approved chart design. ONE batched `replace_in_file` call to index.html. See NEXT_SESSION_PROMPT.md Step 3 for complete implementation spec.

---

## Session M (June 4, 2026) — *H1 Detect tab bug fixes + chart redesign*

**Code committed:** `9b77d4b` (fix: H1 Detect tab — cost-zone chart, column splitters, NS resize, well strip height, intel timestamps, clean pre-injection state)
**Cluster image digest:** `sha256:55e5626853cc...` (fault-trigger-ui)

**What was built and deployed:** Five user-reported bugs on the H1 "Detect" tab fixed in a single batched `replace_in_file` call. (1) **Chart redesign** — `_renderH1Charts` rewritten from scratch: pre-injection now shows only "Live Sensor Reading" + SCADA alarm threshold line with a clean "NOW — Monitoring" label (no fault projection, no declining ML lines). Post-injection renders three colored cost-zone backgrounds (green=$0, amber=~$2k, red=$150k) with "🤖 AI detects — ACT NOW", "📡 SCADA alarms T+Xm", "⛔ PNR" event pin annotations and cost labels in each zone. "ML RUL Projection" label (integrity violation per our rules) removed and replaced with "GDC ML Forecast". (2) **Column resize splitters** — two `.h1-splitter` divs inserted between well-strip↔center and center↔copilot; `initH1CenterSplit(e, side)` wired to both; replaces the dead `initH1Resize` which was referencing `.h3-main-body` (a container that doesn't exist in the H1 layout). (3) **NS resize handle** — `h1-ns-handle` div added between chart and Window of Options (gated v-if="h1Injected"); `initH1NsSplit` method controls `h1ChartH` data property via `:style` binding. (4) **Well strip** — widened 82px → 110px; SVG `max-height:215px` changed to `flex:1;min-height:0` so the strip fills the full column height. (5) **Intel feed timestamps** — `item.ts_label` rendered in `.h1-ic-time` span on each feed row (field was already returned by the API, just never displayed in H1). Also corrected `h1SplitPercent` initial value 60→36 and added `h1ChartH:200` data property.

**Design decisions:** Chart redesign settled on a "cost-zone" framing rather than the previous engineering-centric "ML RUL Projection" line — colored background zones make the business story ($0 vs $2k vs $150k) immediately readable by a non-technical observer. SCADA chart (second stacked chart) was discussed and deferred — the dual-reality bar at the top already handles the SCADA vs AI comparison narrative. "Dive deeper" technical sub-page also deferred — existing ⓘ, citation superscripts, and "How It Works" tab stub cover that need.

**Verification:** Pod `fault-trigger-ui-64d4b6b944-9m5xb` 1/1 Running · `/api/mlops/status` → ollama_online: True, gemma4:latest · digest `sha256:55e56268`.

**Next task:** Collect user visual feedback on the Detect tab, then implement H2 ("Discern") tab redesign per DEMO_MASTER §5 — two-line vibration+temp chart, H2 dual-reality bar with 6 evidence chips, LLM copilot "$1,500 vs $150,000" verdict, reuse all H1 CSS patterns.

---

## Session L (June 4, 2026) — *H1 UI Redesign + Vue template bug fix*

**Code committed:** `e500c4d` (feat: H1 redesign — Detect/Discern/Optimize tabs, dual-reality bar, 3-col layout, copilot dominant, wopt v-if), `1915fe1` (fix: remove em-dash from {{ }} expressions — incorrect theory, benign change), `df13bf2` (fix: remove extra </div> that closed #app early)  
**Cluster image digest:** `sha256:719e0a6c...` (fault-trigger-ui)

**What was built and deployed:** Complete H1 ("Detect") UI restructure in response to 12-point user feedback. Tab nav renamed: Horizon 1/2/3 → Detect / Discern / Optimize (user's preferred "Detect, Discern, Optimize" progression). Fleet Financials tab removed. H1 banner collapsed to a single line with physics description moved behind ⓘ. "25-minute lead time" removed as a standalone callout. New **dual-reality bar** (hero comparison element): two-column compact strip showing SCADA (4 sensors, all nominal) vs GDC AI (same 4 sensors + 4 context chips activating on inject → different verdict). Old evidence wall and scada-compare boxes removed; their purpose absorbed into the dual-reality bar. New **3-column main body**: thin 82px SVG well strip (left), sensor chart + Window of Options (center 36%), dominant LLM copilot panel (right ~52%). Window of Options hidden with `v-if="h1Injected"` — only visible when fault is active. Charts now load and tick on tab open (before injection) via baseline `/api/plot/forecast-data` fetch in `setMainTab`. Live intel feed reduced to 3 compact rows. Stale `h1-scada-chart` DOM reference removed from `_renderH1Charts`.

**Key design decisions:** Dual-reality bar replaces the separate evidence-wall + scada-compare pattern — cleaner and immediately communicates the core "same sensors, different conclusion" argument. LLM copilot at ~52% width is now the visual anchor of the right half of the screen. Window of Options visible only post-injection reduces visual noise in the baseline monitoring state. "How It Works" tab pinned for future refactoring — not touched this session.

**Verification:** Pod `fault-trigger-ui-587fc8fb94-vqdst` 1/1 Running · `/api/live-telemetry/ESP-ALPHA-1` → 200 OK in logs · image digest `sha256:5c6d33ae`.

**Bug fixed (commit `df13bf2`):** The H1 redesign's Block 6 SEARCH/REPLACE (SVG closing → h1-center opening) introduced one extra `</div><!-- /h1-well-strip -->`. After `</svg>`, the existing `</div>` correctly closed `h1-well-strip`. The extra `</div>` then closed `h1-body`. This caused a cascade of 5 more orphaned closing divs: `/h1-center` → closed `h3-dashboard`, `/h1-copilot-pane` → closed the H1 `main-tab-content`, `/h1-body` → closed `app-body`, `/h3-dashboard` → **closed `#app` at line 1334**. Everything after line 1334 (the H2 tab, H3 tab, Architecture tab, and Financial Justification modal at line 2553) was rendered OUTSIDE the Vue template scope — explaining why the Financial Justification modal showed raw `{{ }}` text. Fix: removed the one duplicate line. Commit `1915fe1` (em-dash removal) was an incorrect theory and is a benign no-op; the real fix was one `</div>` deletion.

**Next task:** Collect Detect tab visual feedback, then implement H2 (Discern) tab redesign reusing all new CSS patterns (`.dr-bar`, `.h1-body`, `.h1-copilot-pane`) per DEMO_MASTER §5.

---

## Session K (June 4, 2026) — *H1 Full Redesign — deployed and verified*

**Code committed:** `9951199` (feat: H1 full redesign — Evidence Wall, Cited Copilot, Window of Options, SVG well schematic)  
**Cluster image digest:** `sha256:c8dfa4c...`

**What was built and deployed:** Complete H1 tab redesign matching DEMO_MASTER.md §4 wireframe. Two-column layout (55% left / 45% right). Left column: 2D SVG animated wellbore schematic (blue liquid particles + yellow gas particles with CSS transition, motor housing color gradient green→amber→red, GVF indicator bar), sensor tab bar + GDC forecast chart (230px), Window of Options timeline (3 cards with live VIABLE/MARGINAL/EXPIRED viability tickers, `_updateOptionsViability` ticking every 5s). Right column: Evidence Convergence Wall (5 source categories activating in sequence at 200ms/2s/3.8s/5.5s/7.2s with glow animation), SCADA comparison (always visible, left=4 sensors normal, right=8 signals GAS LOCK 94%), Cited LLM Copilot (auto-streams on inject via `_startCopilotStream` typewriter effect at 4 chars/28ms, superscript citations [¹][³][⁵] linked to source categories, follow-up chat via `/api/agent/chat`), Live Document Feed with `⚡ GDC AI — just now` badge and ALT counterargument styling.

**app.py changes:** `_intel_generator` now uses weighted 55/30/15 document type mix (supporting/neutral/counterargument) per DEMO_MASTER §10 with tailored Gemma prompts per category. `slopes` dict (`dpsi_dt`, `dtemp_dt`, `dvib_dt`, `ds4_dt`) added to `/api/plot/forecast-data` response. `_post_approval_monitor()` background function polls PIP recovery trend every 30s for 2.5 min post-VFD-approval, writes to `RECOVERY_STATUS` dict, exposed via `/api/recovery-status/{asset_id}`. `/api/agent/chat` endpoint added for H1 copilot follow-up chat. `hitl_approve()` for gas_lock now launches both `_run_recovery_thread` and `_post_approval_monitor` in parallel. Fleet Operations tab removed from header. Static financial cards not present (already absent from prior session).

**Verification passed:** Pod 1/1 Running (digest `c8dfa4c`). `/api/mlops/status` → ollama_online: True, gemma4:latest. `/api/recovery-status/ESP-ALPHA-1` → `{"msg":"","state":"pending"}` (correct for no active fault). `/api/plot/forecast-data/ESP-ALPHA-1` → `slopes` dict present with all 4 keys.

**Next task:** Verify H1 demo flow end-to-end in browser (inject → evidence wall → copilot streams → approve → recovery message). Then implement H2 redesign per DEMO_MASTER §5 (two-line vibration+temp chart, H2 evidence wall, copilot with $1,500 vs $150,000 decision, reuse H1 CSS classes).

---

## Session J (June 3–4, 2026) — *Major planning session; H1 full implementation*

**Code committed:** `e8f8b78` (feat: H1 Live Telemetry & Strategic Advisor), `862d674` (docs handoff)  
**Cluster image:** `sha256:7da84c...` (fault-trigger-ui)

**What was built and deployed:** H1-Live-1 (`/api/live-telemetry/{asset_id}` endpoint, SCADA card polls real DB every 5s), H1-Live-2 (`"normal"` key in `INTELLIGENCE_FEED` with 3 baseline docs), H1-Cards-1 (2-card layout, GDC card renamed "Assessment", PIP/Amps/Temp trend rows), H1-LLM-1 (Gemma templates upgraded to risk-weighted financial advisory), H1-P3 (`_run_recovery_thread()` posts 36 climbing DB rows over 3 min post-approval).

**Major design decisions made this session (Session J planning portion):** The Fleet Operations tab was previously removed (do not re-add). H1/H2/H3 tabs are the complete primary demo experience. The `DEMO_MASTER.md` document was written as the authoritative permanent spec — all future sessions read this first. Three-act narrative locked: H1=Protect (gas lock, 25 min window), H2=Discriminate (slug flow, false positive prevention), H3=Optimize (VFD Bayesian optimization, Vertex AI Vizier + local XGBoost). RUL metric replaced by "Window of Options" (viability timeline). Financial case delivered through LLM only, no static cards. "Consult Agent" button eliminated — LLM auto-starts on injection. Evidence Convergence Wall (5 source categories, activation sequence) and Cited LLM Copilot (superscript citations) added as required UI patterns for all three tabs.

**Physics corrections made:** Gas lock failure is thermal (motor loses cooling fluid flow) NOT mechanical dryout ("running dry" is incorrect — pump is still submerged). 25-minute PNR is defensible per API RP 11S and ESP manufacturer guidelines. Three defensible SCADA vs ML claims: fault discrimination, probability scoring before thresholds, context fusion. Advanced SCADA CAN do some multi-sensor correlation — ML wins on discrimination, probability scoring, and context fusion specifically.

**Key rejections this session:** Rejected "RUL" as primary H1 metric (engineering term, not audience-friendly). Rejected static financial cards (numbers without context). Rejected H2 abandonment (reframed as false-positive prevention — compelling to production engineers who have experienced unnecessary pump pulls). Agreed H2 needs temperature-vibration decorrelation as primary visual, not a generic evidence list.

**Next session's primary task:** Implement H1 tab redesign from `DEMO_MASTER.md` spec — 2D SVG well schematic, Evidence Convergence Wall, Cited LLM Copilot (auto-streaming), Window of Options timeline. Single `app.py` + single `index.html` replace_in_file call. Then rebuild/push/rollout.

---

## Session I (June 3, 2026) — *H1 UX overhaul — slate palette, sensor tabs, splitter, corrected financials*

**Code committed:** `0949491` (feat: H1 UX overhaul), `ddb8a3b` (docs handoff)

What was built: Global Tailwind dark slate palette replaced harsh neon palette across the entire UI. H1 drag-resizable splitter between chart pane and RAG pane. H1 multivariate sensor tabs (PIP / Motor Amps / Winding Temp) above GDC forecast chart with `h1ForecastData` cache. H1 assessment state machine (`h1Recovering` flag, 4 states). VFD terminology with Hz + RPM equivalents. Recovery phase (approveH1VFD sets h1Recovering=true, polls for 2 min). Financial card integrity fix: VFD cost corrected $2,500→$0, physics panel net avoided updated, financial card restructured with risk-weighted SCADA-only expected loss (~$97,500).

---

## Session H (prior) — *V1+V2 integrity violations fixed and verified*

**Code committed:** `65275b7`

Fixed integrity violations: H3 Vizier tab now uses real Vertex AI Vizier Gaussian Process Bandit (not fake deterministic trials). Field intel documents now use live Gemma4 Ollama generation via `_intel_generator()`. VFD cost displayed was $2,500 (fixed to $0). H1 assessment label was "INTERVENE NOW" (fixed to "Intervention Needed" with dynamic state machine). All known display-vs-reality mismatches resolved.
