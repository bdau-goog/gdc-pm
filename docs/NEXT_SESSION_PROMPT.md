# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session K end)  
**Git Head:** `38326e4` — clean working tree  
**fault-trigger-ui image digest:** `sha256:c8dfa4c39282aef43011df1bef010e406653c7bb5700f77c88aa11bc2646a98b`  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Verified healthy at session end (June 4, 01:02 UTC):**
- All pods 1/1 Running · fault-trigger-ui-c6847cfc8-qqrsc (7 min old)
- ollama_online: True · model: gemma4:latest
- field_intel: 100 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read the **last 2 entries** in SESSION_LOG.md (Sessions K and J).

---

## STEP 3: What Was Built This Session (H1 Full Redesign)

**Live at:** `http://gdc-pm.bdau.io` → "Horizon 1: Gas Lock" tab

### H1 Tab Architecture (deployed `9951199`):

```
[BANNER: title · Inject Gas Lock · Reset · ⓘ Physics]
[STATUS BAR: SCADA ✓ All Nominal | GDC AI: monitoring/alert/recovering]
[h1-layout: flexbox]
  LEFT (55%):
    well-svg-wrap (SVG animated wellbore, :class="{gaslock, recovering}")
      - blue liquid circles: animateTransform upward, always visible
      - yellow gas circles: class="gas-p", opacity:0 → 0.75 on .gaslock CSS
      - motor rect: :fill/:stroke Vue-bound to h1Injected + h1ElapsedMin
      - GVF indicator: :width Vue-bound (3.5px → 13px on inject)
    sensor tabs (PIP / Motor Amps / Winding Temp) + div#h1-gdc-chart (230px)
    wopt-container (Window of Options)
      - 3 cards: h1OptA (wopt-viable/marginal/expired), h1OptB, last-resort
      - h1ElapsedTimer (5s interval): calls _updateOptionsViability()
      - ✔ Execute Now button: v-if h1Injected && !h1Resolved && h1OptA !== 'wopt-expired'
    h1RecoveryMsg div (v-if, from /api/recovery-status poll every 30s)
  RIGHT (45%):
    evidence-wall (5 rows)
      - h1EvidenceWall array, .active toggled by setTimeout chain on inject
      - activation delays: [200, 2000, 3800, 5500, 7200] ms
      - CSS: .evidence-row.active: opacity 1, glow animation
    scada-compare (always visible, no v-if)
    h1-copilot
      - auto-starts: setTimeout(_startCopilotStream, 3000) on inject
      - typewriter: 4 chars/28ms interval
      - citations: [¹][³][⁵] as <sup> HTML via v-html
      - chat input → /api/agent/chat → Gemma response
    h1-live-feed (h1FeedItems.slice(0,7), lbl_type ai/counterarg/neutral badge)
```

### Key Vue State Added (H1):
```javascript
h1EvidenceWall: [{icon,cat,placeholder,content,active}×5]
h1EvidenceActive: 0    // 0-5, controls ev-synthesis visibility
h1CopilotHtml: ''      // v-html bound, updated by _startCopilotStream
h1CopilotStreaming: bool  // controls .streaming-dot
h1CopilotTimer: null   // setInterval handle for typewriter
h1CopilotText: ''      // plain-text version for chat context
h1ChatInput: ''
h1ChatMessages: [{id,role,text}]
h1InjectedAt: null     // Date.now() on inject
h1ElapsedMin: 0        // (Date.now()-h1InjectedAt)/60000, updated every 5s
h1ElapsedTimer: null
h1OptA: 'wopt-viable'  // CSS class controlling card border/badge color
h1OptALabel: 'VIABLE'
h1OptB: 'wopt-viable'
h1OptBLabel: 'VIABLE'
h1RecoveryMsg: ''
h1RecoveryPollTimer: null
```

### Key Methods Added:
- `_startCopilotStream()` — typewriter effect on h1GemmaFinding or fallback text
- `_updateOptionsViability()` — updates h1OptA/B based on h1ElapsedMin
- `sendH1Chat()` — POST /api/agent/chat, updates h1ChatMessages
- `_activateEvidenceWall()` — setTimeout chain (not called directly; launchHorizon1 uses inline setTimeout loop)

### New API Endpoints (app.py):
- `GET /api/recovery-status/{asset_id}` — returns RECOVERY_STATUS dict (msg, state)
- `POST /api/agent/chat` — {asset_id, fault_type, message, context} → {response}
- `GET /api/plot/forecast-data/{asset_id}` — now includes `slopes: {dpsi_dt, dtemp_dt, dvib_dt, ds4_dt}`

### New CSS Classes (reuse for H2/H3):
```
.h1-status-bar, .h1-sb-half, .h1-sb-scada, .h1-sb-alert, .h1-sb-recover, .h1-sb-label, .h1-sb-div
.h1-layout, .h1-left, .h1-right
.well-svg-wrap, .gas-p (opacity:0; .gaslock .gas-p: opacity:0.75)
.evidence-wall, .evidence-row, .evidence-row.active
.ev-icon, .ev-body, .ev-cat, .ev-content, .ev-check, .ev-synthesis
.scada-compare, .scada-box, .scada-ok, .scada-fault
.scada-box-hdr, .scada-line, .scada-verdict, .scada-verdict-ok, .scada-verdict-fault, .scada-arrow
.wopt-container, .wopt-timeline, .wopt-line, .wopt-now, .wopt-fail, .wopt-marker, .wopt-pnr-lbl
.wopt-cards, .wopt-card, .wopt-badge, .wopt-viable, .wopt-marginal, .wopt-expired, .wopt-last-resort, .wopt-postpnr
.wopt-action, .wopt-cost, .wopt-window, .wopt-approve-btn
.h1-copilot, .h1-copilot-hdr, .h1-copilot-body, .h1-copilot-input
.h1-chat-input-field, .h1-chat-send, .h1-chat-msg.user, .h1-chat-msg.assistant
.streaming-dot
.h1-live-feed, .ai-doc-badge
```

### Known Issues / Things to Check in Browser:
1. **SVG gas particles** — SMIL `animateTransform` runs continuously; `.gaslock .gas-p` CSS opacity should transition on inject. If particles don't appear, check that `h1Injected && !h1Recovering` is true and `.gaslock` class is applied to well-svg-wrap.
2. **Evidence wall reactivity** — `h1EvidenceWall[i].active = true` in Vue 2 is reactive because `active` is pre-declared in data(). If rows don't activate, check that `h1EvidenceWall` is not re-assigned (it's mutated in place).
3. **Copilot text** — Uses `h1GemmaFinding` from `/api/intelligence-feed`. If Gemma is slow and returns empty, the fallback hardcoded text in `_startCopilotStream` kicks in — always produces output.
4. **Window of Options timer** — `h1ElapsedTimer` starts on inject. Viability changes: OptA goes MARGINAL at 18m, EXPIRED at 23m; OptB goes EXPIRED at 23m. The demo runs in 5× compressed time so these will hit quickly if desired.
5. **Chat input** — Uses `/api/agent/chat` which calls Gemma. Expect 8-15s response time. The last message in h1ChatMessages will show `'…'` while waiting.
6. **Recovery message** — Only appears after `approveH1VFD()` is called AND the `_post_approval_monitor` backend thread has run ≥30s. First message: "↗ Recovery on track."

---

## STEP 4: Next Session Flow

### A. First: Accept UI feedback from user (they said "I'll offer feedback on the UI in the next session")
- Do NOT implement anything until feedback is heard
- Common things to check: layout proportions, font sizes, SVG visibility, copilot text quality

### B. After incorporating feedback: H2 Tab Redesign

H2 redesign per DEMO_MASTER.md §5:

**Primary visual:** Two-line superimposed chart — Vibration (rising, orange) + Motor Temperature (flat, blue). One chart. Two lines. The entire diagnostic is visible in 3 seconds.

**New H2 layout structure:**
```
[BANNER: title · Inject Slug Flow · Reset · ⓘ Physics]
[STATUS BAR: SCADA ⚠ Vibration Rising | GDC AI: surface slugging, pump healthy]
[h2-layout: 2-col]
  LEFT (55%):
    Well SVG (pump body GREEN/healthy, surface flowline shows orange slug pulses)
    Two-line chart: vib (orange, rising) + motor_temp (blue, flat)
    Dispatch button (existing dispatchTruckRoll logic)
    $1,500 truck roll vs $150,000 pump pull decision panel
  RIGHT (45%):
    Evidence Wall (6 rows — different from H1):
      📊 Vibration: 1.1→2.4 mm/s ↑ (ALARMING)
      📊 Motor Temp: 198°F → flat (EXONERATING)
      📋 Shift Note: "pumping rough but temp is normal"
      🧪 Separator Test: 1.8 bbl slug volumes, 14-min periodicity
      📋 Surface Choke Log: 3 manual adjustments this tour
      📖 OEM Guide: "Vibration without thermal elevation = surface flow regime"
    SCADA comparison (reuse CSS)
    LLM Copilot: "$1,500 truck roll, not $150,000 pump pull"
    No Window of Options (slug flow = dispatch, no PNR countdown)
```

**Implementation approach:**
- Reuse ALL `.evidence-wall`, `.scada-compare`, `.h1-copilot`, `.h1-status-bar` CSS
- Add `.h2-layout`, `.h2-left`, `.h2-right` (same pattern as h1-layout)
- H2 Vue state additions: `h2EvidenceWall`, `h2EvidenceActive`, `h2CopilotHtml`, `h2CopilotStreaming`, `h2CopilotText`, `h2ElapsedTimer` (for optional future use)
- Modify `launchHorizon2` to activate evidence wall + start copilot stream
- Keep existing `dispatchTruckRoll()` and truck roll countdown logic

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — no `browser_action` tool
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain
- Fleet Operations tab: do NOT re-add (removed)
- Financial case: LLM only, no static financial cards
- Token budget: batch all edits to same file in ONE replace_in_file call
