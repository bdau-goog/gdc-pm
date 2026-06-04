# GDC-PM Session Log — Append-Only History

**Format:** One paragraph per session, newest first. Never delete entries.  
**Usage:** New sessions read the last 3–5 entries only for recent decision context.

---

## Session L (June 4, 2026) — *H1 UI Redesign + Vue template bug fix*

**Code committed:** `e500c4d` (feat: H1 redesign — Detect/Discern/Optimize tabs, dual-reality bar, 3-col layout, copilot dominant, wopt v-if), `1915fe1` (fix: remove em-dash from Vue template expressions)  
**Cluster image digest:** `sha256:b0291a14...` (fault-trigger-ui)

**What was built and deployed:** Complete H1 ("Detect") UI restructure in response to 12-point user feedback. Tab nav renamed: Horizon 1/2/3 → Detect / Discern / Optimize (user's preferred "Detect, Discern, Optimize" progression). Fleet Financials tab removed. H1 banner collapsed to a single line with physics description moved behind ⓘ. "25-minute lead time" removed as a standalone callout. New **dual-reality bar** (hero comparison element): two-column compact strip showing SCADA (4 sensors, all nominal) vs GDC AI (same 4 sensors + 4 context chips activating on inject → different verdict). Old evidence wall and scada-compare boxes removed; their purpose absorbed into the dual-reality bar. New **3-column main body**: thin 82px SVG well strip (left), sensor chart + Window of Options (center 36%), dominant LLM copilot panel (right ~52%). Window of Options hidden with `v-if="h1Injected"` — only visible when fault is active. Charts now load and tick on tab open (before injection) via baseline `/api/plot/forecast-data` fetch in `setMainTab`. Live intel feed reduced to 3 compact rows. Stale `h1-scada-chart` DOM reference removed from `_renderH1Charts`.

**Key design decisions:** Dual-reality bar replaces the separate evidence-wall + scada-compare pattern — cleaner and immediately communicates the core "same sensors, different conclusion" argument. LLM copilot at ~52% width is now the visual anchor of the right half of the screen. Window of Options visible only post-injection reduces visual noise in the baseline monitoring state. "How It Works" tab pinned for future refactoring — not touched this session.

**Verification:** Pod `fault-trigger-ui-587fc8fb94-vqdst` 1/1 Running · `/api/live-telemetry/ESP-ALPHA-1` → 200 OK in logs · image digest `sha256:5c6d33ae`.

**Bug fixed (commit `1915fe1`):** Em dash character U+2014 (`—`) inside Vue 3 template `{{ }}` expression string literals (e.g., `{{ h1SensorPsi || '—' }}`) causes Vue 3 CDN runtime's template expression extractor to misparse the `}}` boundary. The extractor consumed a large portion of subsequent template as one broken expression, which caused ALL subsequent `{{ }}` expressions to fail silently — including the Financial Justification modal, which then rendered raw template text despite Vue being mounted. Fix: replaced all `'—'` fallback defaults in `{{ }}` expressions with `'--'`, and simplified the dr-verdict nested ternary to ASCII-only strings. The box-drawing character `─` in static text (outside `{{ }}`) is unaffected.

**Vue 3 CDN Runtime — confirmed limitation:** Multi-byte UTF-8 characters (em dash U+2014 = E2 80 94, emoji, etc.) inside single-quoted string literals within `{{ }}` template expressions can corrupt Vue 3's production CDN runtime template extractor. Safe workaround: use ASCII alternatives (`--`, `-`, `N/A`) as fallback values in `{{ }}` expressions. Emoji in static text (outside `{{ }}`) is unaffected.

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
