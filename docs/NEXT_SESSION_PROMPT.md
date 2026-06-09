# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session AC — L3-centered narrative locked, Surveillance removed, DEMO_MASTER §3/§3.5 rewritten)
**git head:** (pending final commit — docs only)
**fault-trigger-ui image:** `sha256:fa0d96b9` (Session AB — no code changes in Sessions AA or AC)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Five Commands First

```bash
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG"
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM telemetry_events;"
```

**Verification (Command 5 — inference model audit):**
```bash
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "import urllib.request, json; print(list(json.loads(urllib.request.urlopen('http://inference-api:8080/model-info').read().decode())['models'].keys()))"
```

**Expected when healthy:**
- Workspace: `PROJECT=gdc-pm-v2` · `KUBECONFIG=/home/brian/gdc-pm/.kubeconfig`
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ≥1 (hitl_action rows from Batch D) · rag_documents: 18 · telemetry_events: > 1,000,000
- inference-api models: `['esp_classifier', 'gas_lift_classifier', 'mud_pump_classifier', 'top_drive_classifier', ...]`

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read: `docs/RED_TEAM_LEDGER.md` — trigger phrase "**red team**" re-runs the hostile-engineer audit.

---

## STEP 3: Session Z completed Batch D + Batch E — Next Tasks

### Session Z Batch D COMPLETE ✅
- `/api/h1/remediation-record` endpoint live — writes `doc_type='remediation_record'`, `lbl_type='hitl_action'` to `field_intel`
- `get_rag_context_and_adjusted_rul()` excludes `hitl_action` rows (`AND lbl_type != 'hitl_action'`)
- `executeH1Shutdown()` and `approveH1VFD()` wired in `app.js` to POST remediation record

### Session Z Batch E COMPLETE ✅
- **SCADA pre-alarm sensor tiles:** Live PIP/Amps/Temp/Vib tiles (green nominal state) now shown on SCADA tab BEFORE alarm fires — same data as GDC tab. Symmetric presentation, ISA-101 compliant.
- **Taller wellbore SVG (Zone 3):** Container 12%→15%. viewBox 0 0 40 210 → 0 0 44 250. Added surface Christmas tree (X-MAS block at top), 4 perforation pairs, formation/reservoir block at bottom (~9,800 ft MD). Depth tick marks at 3k/6k ft.
- **SVG document icons:** Replaced plain 📄 emoji with distinct inline SVG badges: waveform acoustic trace (sonic log/shift note), bar chart GOR trend (separator lab report), open book (OEM guide). Each has distinct color (green/blue/purple) + label text.

### Session AA COMPLETE ✅
- `MODEL_FOUNDATIONS.md` precision conflict resolved — 0.815 is correct v1 historical record; v2 P=0.995 documented.

### Session AB COMPLETE ✅
- `esp_thermal.ubj` trained (50,200 rows, single feature `vfd_hz`, max delta ±0.33°F from physics polynomial)
- `load_health_models()` extended to load `esp_thermal.ubj` at startup — confirmed live in `HEALTH_MODELS` registry
- `evaluate_hz()` in `vizier_optimize()` now calls `HEALTH_MODELS["esp_thermal"].predict()` with honest polynomial fallback
- Deployed `sha256:fa0d96b9`, rollout successful, `api/model/status` confirms `esp_thermal` in models_loaded

### Session AC COMPLETE ✅ (docs only — narrative strategy locked)
- DEMO_MASTER.md §3/§3.5 rewritten: L3 = sole categorical moat; L1+L2 conceded; Surveillance removed with full rationale. Rejected L2 claims documented (cannot be re-introduced without SME source).
- SESSION_LOG + NEXT_SESSION_PROMPT updated with all decisions + H1/H2/H3 UI impact.

### NEXT TASKS — Session AD: UI Implementation

**1. index.html — Surveillance removal + How It Works + H1 re-emphasis (single batched call):**
- Remove Surveillance tab HTML block (lines ~345–508)
- Remove Surveillance nav `<div>` (line ~21)
- How It Works: reorder GDC column bullets — L3 ("Reads field documents") first; ML detection moves to one honest line conceding both tiers
- How It Works System Overview or Context Fusion: add "tags vs. tag-patterns vs. documents" 3-line comparison
- How It Works Pane 3 (ML Detection): replace "Multivariate ML detection" with: *"Learned risk scoring — not fixed thresholds. Against best-of-breed predictive platforms, detection converges; document fusion is GDC's categorical edge."*
- H1 banner or Physics & Logic panel: add physics-impossibility premise — *"Gas lock and fluid drawdown produce identical PIP/Amps/Temp/Vib. No sensor model can distinguish them. The answer exists only in field documents."*
- H1 GDC Advisor Zone 2 Right doc-reveal label: add synthesis payload — *"The answer was never in the sensors. GDC read these documents, cross-referenced them against live telemetry, and resolved the fault in under 2s."*
- H1 lead-time callout: demote from headline to compact annotation
- INTEGRITY: line ~572 "8,412 field documents" → "field-document corpus (shift notes, sonic logs, GOR reports)"

**2. app.js — Default tab (1 line):**
- `mainTab: 'surveillance'` → `mainTab: 'architecture'`

**3. app.py — Integrity fix (1 line):**
- Line ~4975: `"model_drift_detected": False` → remove the field or relabel as `"model_drift_detection": "not_implemented"`. Do NOT imply an active detector.

**After:** docker build → push → `kubectl set image` with explicit digest → verify grep (no "surveillance" nav, no "8,412", model_drift relabeled, mainTab default = 'architecture').

---

### FUTURE SESSION AE: Presenter Script + 5-Minute Veo Video

**Scope:** A full narrated demo script suitable for: (a) live presenter walkthrough and (b) Veo-generated 5-minute video.

**Structure of the 5-minute video (draft outline):**

| Segment | Duration | Content |
|---|---|---|
| 1 — The Problem | ~45s | Physics-impossibility frame: gas lock and drawdown produce identical telemetry. Wrong action = $150k seized pump. SCADA cannot distinguish them. |
| 2 — How It Works | ~60s | Tags vs. tag-patterns vs. documents. GDC reads the field documents the operator already has. The answer is always in the documents. |
| 3 — H1 Discern (live demo) | ~90s | Scenario replay: sensors decline → SCADA alarm fires → GDC already retrieved 3 docs → Bayesian discrimination → correct action prescribed. Lead-time shown but not featured. |
| 4 — H2 Classify (live demo) | ~45s | Slug flow: vibration rises, temp flat → classifier + choke log + separator test → do NOT pull well → $1,500 truck roll vs $150k false alarm. |
| 5 — H3 Optimize (live demo) | ~30s | VFD optimization: Vizier drives Hz search, edge model enforces thermal constraint. Vertex AI collaboration without cloud dependency for the decision. |
| 6 — Close | ~30s | All-edge, no cloud dependency, sovereign, on-prem. The decision stays at the pad. |

**Deliverable:** A `docs/VIDEO_SCRIPT.md` file containing:
- Scene-by-scene narration text (Veo voiceover)
- On-screen UI state descriptions at each beat (what the presenter clicks)
- On-screen text overlays at each beat
- Timing targets per segment

**Note:** This is a separate session from Session AD (UI code). Do NOT mix them. Session AD first, then Session AE.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Scenario Replay physics | ✅ FIXED Session S | psi_final 400–600 PSI, temp 245–265°F, vib 4.5–6.5, lead ~5–15 min |
| Smart SCADA alarm logic | ✅ FIXED Session S | 3-rule ISA-18.2/API RP 11S — fires step 79/120 (~T=20min) |
| `esp_health.ubj` / `esp_classifier.ubj` | ✅ FIXED Session S | RMSE=0.00179, gas_lock P=0.995, all gates pass |
| CLAIM_LEDGER.md H1 ranges | ✅ FIXED Session V | Was wrong (875-1100 PSI) — reconciled to actual FAULT_PROFILES (400-600 PSI) |
| H2 physics mechanism | ✅ FIXED Session V | Cut 'surface shock transmission'; corrected to in-string multiphase slug loading |
| H2 Classify tab | ✅ NEW Session V | Full Scenario Replay layout: dual chart, scrubber, ISA-101 SCADA, GDC 3-zone, shared SVG wellbore |
| `92%/94% confidence` literals | ✅ FIXED Session X Batch B | Replaced with live `_bayes_discriminate()` posterior — 99.6% on fluid_drawdown |
| Bayesian discrimination confidence not wired | ✅ FIXED Session X Batch B | `_bayes_discriminate()` live; evidence table shows F1–F4 LR chain |
| Scrub-reactive GDC verdict reset | ✅ FIXED Session Y Batch C | Back-scrub before gdc_detect_idx resets all revealed state |
| Transport controls locked after remediation | ✅ FIXED Session Y Batch C | Buttons + scrubber disabled on h1Resolved/h1Seized/h2Resolved/h2PullOutcome |
| H2 classifier_ok verified live | ✅ VERIFIED Session Y | curl confirms classifier_ok:true — inference-api running real esp_classifier.ubj |
| Remediation writes to field_intel | ✅ FIXED Session Z Batch D | `/api/h1/remediation-record` live; lbl_type='hitl_action' excluded from discrimination RAG |
| SCADA pre-alarm sensor tiles | ✅ NEW Session Z Batch E | Live PIP/Amps/Temp/Vib tiles (green) on SCADA tab before alarm fires |
| Wellbore SVG taller + X-MAS tree + formation | ✅ NEW Session Z Batch E | Zone 3: 15% wide, viewBox 250 tall, surface tree, depth ticks, formation block |
| SVG document icons | ✅ NEW Session Z Batch E | Distinct inline SVG badges (sonic waveform, GOR bar chart, OEM book) replace 📄 emoji |
| MODEL_FOUNDATIONS vs SESSION_LOG precision conflict | ✅ FIXED Session AA | MODEL_FOUNDATIONS.md updated — v2 results (P=0.995, all gates pass) documented in §6/§8/§9 addendum. 0.815 retained in §9 as correct v1 historical record. |
| `vizier_optimize()` hardcoded polynomial (H3 integrity) | ✅ FIXED Session AB | `esp_thermal.ubj` trained + deployed; `evaluate_hz()` now calls `HEALTH_MODELS["esp_thermal"].predict()`. Confirmed in HEALTH_MODELS registry. |
| Surveillance tab fabrications (8,412/14/156) | ✅ SPEC REMOVED Session AC | DEMO_MASTER §3.5 documents all 4 reasons. UI removal = Session AD. |
| DEMO_MASTER §3 L2 overclaims | ✅ FIXED Session AC | Rejected L2 claims table in DEMO_MASTER §3 — cannot be reintroduced. |
| `model_drift_detected: False` stub (app.py ~4975) | ⏳ OPEN Session AD | Remove or relabel — implies an active detector that always returns OK. |
| "8,412 field documents" (index.html ~572) | ⏳ OPEN Session AD | Remove count; rephrase as "field-document corpus." |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- Gas Lock and Fluid Drawdown have IDENTICAL sensor trajectories — this is the H1 premise
- Physics panel `<` chars in text content: safe only as `< ` (space after) — never `<digit`
- `app.py` ~6,400 lines, `index.html` ~2,760 lines, `app.js` ~2,300 lines — always grep for line numbers first
- H2 uses inference-api (not local esp_classifier.bst) — local .bst is 4-class without slug_flow
