# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session AT — strategy locked, build plan set, docs-only overnight session)
**git head:** `d80103f` (SESSION_LOG + NEXT_SESSION_PROMPT)
**fault-trigger-ui image:** `sha256:2fd95932...` (unchanged — no app code deployed)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected:** 8 pods 1/1 · ollama_online: True · gemma4:latest · field_intel: 5-6 · rag_docs: 18

---

## STEP 2: MCP Server (verify before use)

**Quick inline check:**
```bash
python3 -c "
from google import genai
from google.genai import types as gtypes
client = genai.Client(vertexai=True, project='gdc-pm-v2', location='us-central1')
r = client.models.generate_content(model='gemini-2.5-flash', contents='Reply: OK',
    config=gtypes.GenerateContentConfig(max_output_tokens=8192))
print(r.text)
"
```

**If "Reauthentication needed":**
```bash
gcloud auth application-default login --no-browser
gcloud auth application-default set-quota-project gdc-pm-v2
# Then: Ctrl+Shift+P → Developer: Reload Window
```

**Config:** `~/mcp/start.sh` → `~/mcp/second_opinion_server.py` · `gemini-2.5-flash` · `gdc-pm-v2` · `timeout: 120000` · results → `/tmp/mcp-results/`

---

## STEP 3: LOCKED STRATEGY — DO NOT RE-OPEN

**The strategy is decided. Do not re-litigate. Execute the build plan below.**

### The Locked Value Proposition

**Thesis:** The AI-powered diagnostic advisor — the capability the entire APM industry (GE, AVEVA, Aspen Mtell, Cognite, C3.ai) is building for cloud deployment in 2025–2026 — GDC delivers inside the operator's sovereign boundary, on open-weight Gemma, at the edge, where the data already lives.

**Three-gap frame:**
1. **The diagnostic gap**: SCADA says *that* something is wrong; APM says the *pattern* is anomalous; neither says *why*, because "why" lives in documents. GDC reads the documents.
2. **The scale gap**: A senior engineer can diagnose one well; they cannot diagnose 200 wells at 2am. GDC gives every operator senior-level differential diagnosis on every asset at once.
3. **The sovereignty gap**: Cloud APM requires data egress — precluded for NOCs, IEC 62443 OT-compliance, data-residency-law operators. GDC is the only complete path for those operators.

**Honest-footing rule (prevents "but a human could do this" attack):**
> *"Yes — a skilled engineer could reach this conclusion with the right documents and time, on a single well. What GDC does is make it automatic, fleet-scale, instant, cited, and inside your perimeter — turning a diagnosis that's possible in principle into one that happens every time in practice."*

**Competitive claim (neutral-checked by Gemini — do NOT say "no product does this"):**
> *"No native, production-ready commercial product combines real-time ML anomaly detection with LLM-based differential diagnosis over unstructured maintenance documents — as of 2025–2026, this is where all major APM platforms are heading. GDC delivers it now, inside the sovereign perimeter, on open weights."*

**Market validation (Gemini neutral search confirmed):**
- C3.ai 2026 roadmap: "virtual subject matter expert... full context — all sensor data, structured, unstructured, past work performed on the machine"
- GE Vernova, AVEVA, Aspen Mtell, Cognite: all have GenAI roadmap items for document-aware diagnosis
- The direction is industry-validated. GDC's differentiator is WHERE it runs (sovereign edge), not WHAT (the AI capability class).

---

## STEP 4: ORDERED BUILD PLAN — Execute top to bottom, max token budget

**Gemini MCP tools are autoApprove. Use `gemini_search` freely for fact-checking and citations. Use `gemini_second_opinion` only if a specific claim needs validation — do NOT run hostile red-team on locked strategy items.**

---

### PRIORITY 1: `docs/DEMO_STORY_AND_PATH.md` (NEW FILE — most important artifact)

**This is the stakeholder-ready document that tells the full story.** Six sections:

**Section A — The Journey (the diligence record)**

Write the honest narrative of how we got here, suitable for showing stakeholders. Key beats:

1. Started by overclaiming against SCADA (detection-race, "SCADA lets the pump die") → red-team killed it
2. Over-corrected: conceded detection speed, document access, safe-default shut-in → only "fleet doc-fusion efficiency" survived → felt thin
3. H2 slug-flow: dual-AI red-team (Gemini + Claude Opus) found 4 FAILs — deciding signal is telemetric (cyclic amps + PIP), APM reads it → invalidated
4. H2 frac-hit: failed Test 1 — experienced Permian operators recognize frac signatures → invalidated. Pre-alert reframe (RRC filing monitoring) rejected as too O&G-specific
5. The L2 over-concession: having conceded so much of L2, we tried to make L3 alone carry the moat → weak scenarios, each producing "a human could figure this out"
6. The resolution: neutral Gemini market check confirmed the entire APM industry is building this capability for cloud. GDC's differentiator is sovereign-edge deployment — not the AI, the WHERE. That claim is true and cannot be attacked.
7. Conclusion: we refused to ship a claim we couldn't defend. What survived is real, is needed, and is aligned with where the market is going.

**Section B — Locked Value Proposition** (copy from §3 above, formatted for stakeholders)

**Section C — Full H1 Story**
- Asset: Permian ESP, moderate-sand, intake-only gauge string (≈90% of Permian ESPs — no discharge gauge)
- Event: PIP + motor amps decline together — genuinely ambiguous between gas lock and fluid drawdown on this sensor string
- Why ambiguous (source: API RP 11S §7.2): a downhole discharge gauge would resolve it but this well doesn't have one; acoustic fluid-level shot requires dispatching a crew (hours); PIP itself is only a proxy with gas breaking out
- Correct actions are opposite: Gas lock → VFD trim 52→44 Hz, stays online (~$2,500); Fluid drawdown in a moderate-sand well → emergency shut-in (trimming drops velocity below critical sand-transport threshold → solids compact around rotating impeller → seizure, ~$150k per SPE-170776)
- Without GDC: standard policy on ambiguous underload alarm = production-deferring shut-in (safe for both causes, but costs ~$3k–$8k in deferred production + restart)
- GDC resolution: XGBoost flags decline (L2) → Gemma reads shift note + sonic survey + GOR lab report → "casing annulus fully submerged, GVF elevated, stable sand history → gas lock → VFD trim safe" or "dynamic fluid level near intake, no gas indicators → drawdown → trim contraindicated, shut in"
- Cited verdict in seconds; operator reviews and approves (HITL)
- The win: at 2am across 200 wells, operators default to reflexive shut-in; GDC enables confident, cited, production-preserving action — every time, with an audit trail
- Vid spine: "One signature. Two causes. Opposite actions. The answer was never in the sensors."
- P&E example: Transformer DGA gas rise — normal load cycling or incipient fault? Deciding context: LTC maintenance log + loading plan + prior fault record
- Mfg example: Motor vibration rise — bearing wear or imbalance from a recent tooling change? Deciding context: maintenance log + production schedule

**Section D — Full H2 Story**
- Asset: Permian ESP producer, 8 weeks post-workover
- Event: Motor efficiency declining + vibration rising slowly over 3–4 weeks
- On standard 4-sensor string (PIP, motor amps, winding temp, single-axis vib accelerometer): pattern matches early **bearing wear** — the most common cause of this signature
- Hidden cause: workover crew used a **non-OEM-spec hydraulic fluid incompatible with the Buna-N elastomer shaft seals**. Documented only in the workover completion report (fluid type, vendor, date). No sensor recorded this.
- APM response: routes to "bearing degradation → workover investigation / pump pull" (~$80k WTX spot rate, 3-day rig)
- Why APM gets it wrong: Gemini confirmed (API RP 11S3/S5) — elastomer seal degradation and bearing wear produce genuinely ambiguous signatures on standard 4-sensor ESP strings without spectral analysis or dedicated bearing temps. APM routes to the *common* hypothesis. Cannot access the workover completion report.
- GDC resolution: L2 classifier flags "mechanical degradation — investigate" → Gemma reads workover report (fluid type) + OEM compatibility matrix (Buna-N incompatibility for that fluid class) + timing correlation (3-week onset matches expected elastomer swell timeline for that fluid) + historical pull data (last pull: normal bearing condition) → "Elastomer seal degradation from workover fluid fill — NOT bearing wear. Correct action: controlled flush + reseal (~$8k)"
- The win: GDC generates the non-obvious provenance hypothesis automatically. The fluid↔seal relationship is purely documentary — no sensor or APM can infer it. Fleet scale: the operator won't think to check the 8-week-old workover report when a vibration alarm fires at 2am for one of 200 wells.
- 51% of ESP failures attributed to human factors/operational problems (2014 SPE AI Conference survey; SPE 185275-MS, 194398-MS, 144562-MS). The maintenance-provenance class is common and material.
- Cost: verify via `gemini_search` before committing final numbers — target ~$8k reseal vs ~$80k pull
- Vid spine: "The pump isn't failing. The last workover is. And it's written down in a report no sensor can read."
- P&E example: Hot transformer — overload, or non-spec cooling fluid in last service (in the service record)?
- Mfg/MRO example: Pump cavitation or actuator degradation — wear, or a fluid/feedstock change documented in the batch/service record?

**Section E — Full H3 Story**
- Setup: Oil price spikes; operator wants to run the ESP faster (50→58 Hz) to capture production upside
- Risk: Faster = hotter. Motor winding exceeds thermal limit → burnout. IEC 60085 Class H insulation limit = 356°F / 180°C. Field derated operating setpoint = 280°F (the limit enforced in the demo — not the insulation class limit).
- The collaboration: Vertex AI Vizier runs in cloud to search the optimization space (GP-based Bayesian search over Hz + well parameters) → local XGBoost thermal model (`esp_thermal.ubj`) evaluates each proposed point against the 280°F constraint → HITL approves the final setpoint
- **Honest sovereign framing (the fix):** NOT air-gap. "No cloud dependency for the *decision*. Vizier proposes candidate setpoints; the **edge model enforces the thermal safety limit and holds it even if the WAN drops mid-search**. Only parameter-level math goes to cloud — never raw operational telemetry."
- The novel piece: it's not the cloud optimization (common). It's the **edge safety constraint that holds when the link dies** — at precisely the wrong moment (process upset, storm, satellite outage).
- The win: operator captures the price window without risking a $150k motor burnout. The edge is the safety system.
- Vid spine: "Push for the price window. The edge holds the safety line — even if the cloud goes dark."
- P&E example: Dynamic transformer loading — push harder at peak demand; local model holds the hot-spot temperature limit
- Mfg example: Line-speed optimization — push throughput; local model holds the quality/thermal constraint

**Section F — Path to Vids (the morning checklist)**

```
MORNING SESSION — ordered checklist to reach recorded narrations:

1. [ ] Read DEMO_STORY_AND_PATH.md (confirm framing is right)
2. [ ] Walk H1 all 6 briefing panels (already built) — note any copy changes against locked framing
3. [ ] Walk H1 scenario replay — confirm cited verdict, document reveals, HITL
4. [ ] Walk H2 3-panel briefing (needs to be built overnight or this session)
5. [ ] Sign off H2 synthetic documents (workover report, OEM matrix, shift note) against G1–G6 gate
6. [ ] Walk H2 scenario replay (needs backend endpoint + replay UI)
7. [ ] Walk H3 Optimize tab — confirm Vizier hybrid framing in copy
8. [ ] Record H1 narration (~90–120s)
9. [ ] Record H2 narration (~90–120s)
10. [ ] Record H3 narration (~90–120s)
11. [ ] Record overview / value-prop narration (~60s)
```

---

### PRIORITY 2: DEMO_MASTER §3 Rewrite

Replace the current §3 (STATE vs CONTEXT) with the locked framing:
- **New thesis**: sovereign-edge of an industry-validated capability
- **Three gaps**: diagnostic / scale / sovereignty
- **Honest-footing rule**: "yes a human could, in theory, on one well..."
- **Competitive claim**: "no native commercial product combines all three tiers as of 2025–2026"
- **Market validation**: cite the neutral Gemini finding (C3.ai, GE Vernova, AVEVA, Cognite all heading here)
- **The winning frame**: where-not-what

Keep DEMO_MASTER §3.5 (Surveillance tab removed), §4 (H1 — do not change, already aligned), §4.5 (Briefing Pattern Spec — do not change).

---

### PRIORITY 3: DEMO_MASTER §5 Rewrite (H2)

Replace the invalidated slug-flow H2 with the maintenance-provenance scenario:
- Asset: ESP producer, 8 weeks post-workover
- Trigger: wrong-fluid fill (Buna-N incompatible) documented in workover completion report
- Sensor pattern: efficiency decline + vibration rise → bearing wear (misdiagnosed)
- GDC resolution: workover report + OEM compatibility matrix + timing → seal degradation → $8k reseal
- Synth docs needed (G1–G6 gate): workover completion report (measurements only, no diagnosis), OEM fluid compatibility matrix (factual table), shift note ("pumping rougher than usual, monitoring")
- Screen architecture: same H1 pattern (briefing → scenario replay). Replay endpoint: `GET /api/h2/scenario-replay?asset=ESP-ALPHA-3`. Two tabs: SCADA View (flags degradation, recommends investigation) / GDC Advisor (reads 3 documents, reclassifies, recommends flush+reseal)
- Cost claims: source via `gemini_search` — target $8k–$15k reseal vs $70k–$100k pump pull investigation (WTX rig rates)

Also update the "Visual & Narrative Drama" section to reflect new scenario architecture.

---

### PRIORITY 4: DEMO_MASTER §6 Rewrite (H3)

Single focused change: add the honest Vizier hybrid framing:
> "Vertex AI Vizier searches the optimization space (cloud GP math — only parameter-level data, never raw telemetry). The local XGBoost thermal model (`esp_thermal.ubj`) enforces the 280°F derated safety constraint at every proposed setpoint and holds it even if the WAN link drops. The decision and the safety constraint both remain on-premise."

Remove any language that implies full air-gap or "no cloud dependency" without qualification.

---

### PRIORITY 5: `docs/VIDEO_SCRIPT.md` (NEW FILE)

**Format for each scenario:** Open (the situation) → Tension (the problem) → Reveal (GDC) → Resolution (the outcome) → Bridge to next horizon. ~90–120 seconds each.

**H1 Narration — DISCERN:**
Open: "In a Permian Basin RTOC, an unloading alarm just fired on Well A-3. PIP down, amps down. Standard response: shut it in to be safe."
Tension: "But this well has two possible causes. Gas lock — trim the VFD, stay online. Fluid drawdown — trim in a sandy well, and you seize the pump. Same sensors. Same alarm. Opposite actions."
Reveal: "GDC has already retrieved the 06:15 shift note, the GOR lab report, and the sonic survey. Casing annulus is fully submerged. GOR is rising. Stable sand history. That's gas lock."
Resolution: "The operator approves the VFD trim. The well stays online. The differential diagnosis took 8 seconds. The audit trail cites three documents."
Bridge: "That's the ambiguity problem. H2 shows the provenance problem."

**H2 Narration — CLASSIFY:**
Open: "Well A-3 has been declining for three weeks. Efficiency down. Vibration up. Textbook early bearing wear."
Tension: "Every APM platform on the market would route this to a pump-pull investigation. That's $80,000 and three days offline. Except the pump bearings are fine."
Reveal: "Eight weeks ago, a workover crew used a non-OEM hydraulic fluid. Incompatible with the Buna-N seals. That's in the workover completion report. GDC read it. Cross-referenced the OEM compatibility matrix. The timing matches elastomer swell — three weeks, exactly as expected."
Resolution: "The recommendation: flush and reseal. Eight thousand dollars. The pump stays in the ground. The cause was never in any sensor — it was in a document from 8 weeks ago."
Bridge: "Now: what if you could also optimize production within that safety envelope?"

**H3 Narration — OPTIMIZE:**
Open: "Oil price just spiked. The operator wants to run Well A-3 faster — 50 to 58 Hz — to capture the window."
Tension: "Faster means hotter. Exceed the motor winding temperature and the pump burns out. That's a $150,000 failure."
Reveal: "Vertex AI Vizier searches the optimization space. Every candidate setpoint is evaluated by the local XGBoost thermal model — running inside the RTOC, inside the perimeter. The edge holds the 280°F safety line."
Resolution: "The operator runs at 54 Hz — within limits, capturing the upside. If the satellite link drops mid-search, the edge model holds the constraint. The AI goes as far as it safely can. No further."
Bridge: "Diagnose the cause. Prevent the wrong fix. Optimize within limits. Three problems. One sovereign AI stack."

**Overview / Value Prop Narration (~60s):**
"Industrial operations generate two kinds of intelligence: sensor data, which every SCADA and APM platform reads, and operational documents — shift notes, workover reports, OEM manuals, lab results — which no sensor-based system can read in real time. GDC changes that. A local LLM reads your documents. Local ML models read your sensors. Together they generate a cited differential diagnosis — not just an anomaly score, but a ranked explanation of what's happening and what to do — inside your sovereign boundary, on open weights, in seconds. The whole APM industry is building this for the cloud. GDC delivers it where your data already lives."

---

### PRIORITY 6: H2 Briefing Panels (3-panel spec)

**Panel 1 — The Equipment:**
- Scope: Permian ESP producer well, moderate-sand, post-workover context
- Key callout: "This well had a workover 8 weeks ago — recorded in the completion report. What was used matters."
- Visual: wellbore schematic (nominal state, green pump/motor indicators)
- Blue callout: sensor string (PIP, amps, winding temp, single-axis vib) — note: no bearing temp sensor, no vibration spectrum

**Panel 2 — The Provenance Hook:**
- Title: "The Sensor Can't Remember What Happened"
- Visual: Timeline — Workover (T-8wk) → Symptom onset (T-5wk) → Alarm today
- Left column: 4 sensor tiles showing the degradation pattern (efficiency ↓, vib ↑) — the "bearing wear signature"
- Right column: Document stack — Workover completion report (fluid type: [X]), OEM compatibility matrix (shows [X] fluid class → Buna-N: INCOMPATIBLE), timing correlation (3-week onset = expected elastomer swell)
- Key quote: "Bearing wear and seal degradation look the same on these four sensors. The difference is in a document."

**Panel 3 — The Decision:**
- GDC verdict: "Elastomer seal degradation from workover fluid incompatibility — NOT bearing wear"
- Action cards: ✅ Controlled flush + reseal (~$8k) vs ⚠ Unnecessary pump pull (~$80k)
- Document citations shown
- Universal pattern close: same structure = wrong-lube (mfg) / wrong-coolant (P&E) / wrong-fluid (MRO)

---

### PRIORITY 7: H2 Claim Ledger Rows

Add to CLAIM_LEDGER.md, sourced via `gemini_search`:

| ID | Claim | Tag | Source | Challenge | Rebuttal | Status |
|---|---|---|---|---|---|---|
| H2-P1 | Bearing wear and elastomer seal degradation produce ambiguous signatures on standard 4-sensor ESP string (PIP, amps, winding temp, single-axis vib) — cannot be distinguished without vibration spectrum or bearing temps | 🟢 TEXTBOOK | API RP 11S3/11S5; Gemini search confirmed | "Good APM would distinguish them" | Only on full spectral analysis. Standard 4-sensor string: genuinely ambiguous. | SURVIVES |
| H2-P2 | Wrong-fluid fill during workover is documented only in the workover completion report — no online sensor on the running ESP carries this information | 🟢 TEXTBOOK | Physical impossibility; no sensor measures historical fill provenance | "Oil analysis can detect it" | Oil analysis requires scheduled sample + lab + days. Not a real-time online sensor. | SURVIVES |
| H2-P3 | Human factors / maintenance-provenance errors are common ESP failure contributors | 🟡 OUR-CODE | 51% of ESP failures = human factors (2014 SPE AI Conference; SPE 185275-MS, 194398-MS) | "How often does a crew use the wrong fluid?" | The class (wrong fluid, non-spec parts, improper procedures) is the common case; not just wrong-fluid specifically. | SURVIVES-SCOPED |
| H2-C1 | Cost of controlled flush + reseal: ~$8k | 🔴 NEEDS-EXPERT | Estimate — verify via gemini_search before shipping | "What's the actual cost?" | Source realistic figure with range before display | PENDING |
| H2-C2 | Cost of unnecessary pump pull investigation: ~$80k | 🟡 OUR-CODE | WTX spot rig rate ~$14k/day × 3 days + motor + deferred production — similar to H1 C3 | "Operators don't pull on early vibration alone" | Correct — they investigate, which can still cost $20k–$80k. Use defensible range. | SURVIVES-SCOPED |

---

### PRIORITY 8: Commit + Final Handoff Docs

After completing priorities 1–7:
1. `git add -A docs/` → `git commit -m "docs(session-at): DEMO_STORY_AND_PATH + DEMO_MASTER §3/§5/§6 rewrite + VIDEO_SCRIPT + H2 spec"`
2. Update SESSION_LOG with one-paragraph Session AT entry
3. Update NEXT_SESSION_PROMPT with: git head, completed items, next task = H2 backend endpoint + UI implementation

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ COMPLETE Session AQ | Deployed |
| H1 Scenario replay | ✅ WORKING | Deployed |
| H2 Briefing panels | ❌ NOT BUILT | Slug-flow H2 invalidated. Maintenance-provenance spec in this prompt. Build per Priority 6. |
| H2 Scenario replay | ❌ NOT BUILT | Backend endpoint + UI needed after spec approval |
| H3 copy — Vizier framing | ⚠️ NEEDS COPY FIX | H3 tab says "no cloud dependency" — fix per Priority 4 |
| MCP gdc-second-opinion | ✅ WORKING | ~/mcp/, gemini-2.5-flash, gdc-pm-v2, timeout=120000 |
| DEMO_MASTER §3 | ⚠️ STALE | Still says STATE-vs-CONTEXT as sole thesis. Needs rewrite per Priority 2. |
| DEMO_MASTER §5 | ❌ INVALIDATED | Slug-flow text still present. Replace per Priority 3. |
| docs/VIDEO_SCRIPT.md | ❌ DOES NOT EXIST | Create per Priority 5. |
| docs/DEMO_STORY_AND_PATH.md | ❌ DOES NOT EXIST | Create per Priority 1. |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — do NOT use `browser_action`
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,400 lines · `index.html` ~3,200 lines · `app.js` ~2,300 lines — grep first, read targeted sections only
- **Wireframes → sign-off → HTML** (never write HTML without sign-off)
- **No H2 HTML until H2 spec and synthetic documents are approved**
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking; do NOT re-open locked strategy decisions
