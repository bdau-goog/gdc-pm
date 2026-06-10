# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 10, 2026 (Session AE — RT-NEW-2/3/L2 integrity fixes deployed)
**git head:** `9d07ac2` (fix(integrity): Session AE)
**fault-trigger-ui image:** `sha256:2f5d3cab` (Session AE)
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

## STEP 3: Session AD COMPLETE — Next Task is Session AE

### Session AE COMPLETE ✅
All integrity fixes deployed and verified live (`sha256:2f5d3cab`):
- **RT-NEW-2 (Class H thermal label):** Reconciled all on-screen temp values to **280°F** (single consistent derated operating setpoint). Removed incorrect "Class H limit" label + unverifiable "per API RP 11S" citation. Now shows: "derated winding-temp operating limit (280°F; Class H insulation rated 356°F / 180°C per IEC 60085)". SCADA tile: `SP: 280°F TRIP`. Sensor glossary: `Derated operating setpoint: 280°F`. app.py motor_overheat methodology: dropped "ROI: 66:1" and softened "$200,000" to "~$150k–$200k" with 🔴 NEEDS-EXPERT tag.
- **RT-NEW-3 (SCADA ledger reword):** CLAIM_LEDGER.md §H1 row 2 reworded from "multivariate rate-of-change alarm, not a static threshold" to honest description of what fires (12/12 live runs = static rolling-average floor at 1,020 PSI). No UI change needed — `scada_rule_fired` already shows the true rule.
- **RT-L2-DRIFT (lead-time banner demoted):** Legacy injectionRunning banner demoted from red uppercase headline to muted weight. Text changed from "SCADA Alarm Zone — Lead Time Consumed" → "SCADA alarm zone — GDC already resolved the ambiguous fault signal". Empty-state: "see GDC lead time advantage" → "see GDC resolve ambiguous fault signals". Aligns with DEMO_MASTER §3(6) lead-time-as-footnote intent.
- **RED_TEAM_LEDGER.md + CLAIM_LEDGER.md** updated with all Session AE findings.
- Grep confirmed: `280°F TRIP`, `derated operating setpoint`, `IEC 60085`, `GDC already resolved`, `resolve ambiguous` — all live ✅. No 270/275/284/356 temp numbers on screen.

### Session AD history ✅
All UI changes deployed and verified live (`sha256:a74f5fbf`):
- **Surveillance tab removed** — nav div + full HTML block (344–508) deleted. `<!-- ══ end TAB: SURVEILLANCE ══ -->` comment kept as tombstone only.
- **Default opening tab** changed: `mainTab: 'surveillance'` → `mainTab: 'architecture'` (How It Works opens first)
- **Physics-impossibility premise** added to H1 Physics & Logic panel — blue callout box before the pp-cols grid, stating the physical measurement constraint cleanly
- **"8,412 field documents"** removed from Physics & Logic panel (L3 Context Fusion section) → replaced with "field-document corpus (shift notes, sonic logs, GOR reports)"
- **GDC disambiguation banner** (H1 post-RAG) reworded: "GDC resolved fault type from field documents — SCADA alarm remains ambiguous without document context"
- **Zone 2 Right synthesis payload** added after "RETRIEVED CONTEXT" label: "The answer was never in the sensors. GDC read these documents, cross-referenced them against live telemetry, and resolved the fault in under 2s." (appears only when h1RagRevealed=true)
- **How It Works Pane 1 GDC compare card** — bullets reordered L3-first: "Reads field documents (shift notes, sonic logs, GOR reports)" → "Resolves physically ambiguous faults sensors alone cannot" → "5s local stream — no WAN needed" → "Learned risk scoring — not fixed thresholds"
- **Tags vs. Tag-Patterns vs. Documents** — 3-column comparison centerpiece added after Pane 1 compare cards (Threshold SCADA / Advanced APM Platforms / GDC Edge AI)
- **Pane 3 ML Detection header** — paragraph replaced: "Learned risk scoring — not fixed thresholds. Against best-of-breed predictive platforms, detection converges; document fusion is GDC's categorical edge."
- **`model_drift_detected: False`** → `model_drift_detection: "not_implemented"` (integrity fix, app.py line 4975)

### NEXT TASK — Session AF: Presenter Script + 5-Minute Veo Video

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

**Note:** Session AD is complete. Session AE is the video script only — no code changes expected.

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
| Surveillance tab fabrications (8,412/14/156) | ✅ REMOVED Session AD | Surveillance tab HTML block deleted. Nav div deleted. No fabricated counts anywhere in UI. |
| DEMO_MASTER §3 L2 overclaims | ✅ FIXED Session AC | Rejected L2 claims table in DEMO_MASTER §3 — cannot be reintroduced. |
| `model_drift_detected: False` stub (app.py ~4975) | ✅ FIXED Session AD | Now `model_drift_detection: "not_implemented"` — no longer implies active detector. |
| "8,412 field documents" (index.html) | ✅ FIXED Session AD | Removed from Physics & Logic panel → "field-document corpus (shift notes, sonic logs, GOR reports)". |
| Surveillance nav tab | ✅ REMOVED Session AD | Nav div deleted; default tab changed to 'architecture' (How It Works). |
| Class H thermal label (270/275/284°F, unverifiable API RP 11S citation) | ✅ FIXED Session AE | All values reconciled to 280°F derated setpoint; IEC 60085 cited for insulation class; "Class H limit" label removed. |
| CLAIM_LEDGER H1 row 2 "multivariate rate-of-change" overclaim | ✅ FIXED Session AE | Reworded to match live behavior (static floor fires 12/12 runs). |
| Lead-time banner "SCADA Alarm Zone — Lead Time Consumed" (red uppercase) | ✅ FIXED Session AE | Demoted to muted footnote per DEMO_MASTER §3(6). |
| motor_overheat methodology "ROI: 66:1 / $200,000" false precision | ✅ SOFTENED Session AE | Dropped ROI ratio; softened to ~$150k–$200k range; 🔴 NEEDS-EXPERT tag added. |

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
