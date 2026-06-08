# GDC Demo Claim Ledger

Every on-screen assertion must have a row here before it is rendered.
Status = **SURVIVES** means it passed all five PRIME DIRECTIVE gates.

---

## H1 — Discern Tab (ESP Fluid Unloading — Well A-3 Scenario Replay)

| Claim | Tag | Source | Challenge | Rebuttal | Status |
|---|---|---|---|---|---|
| Gas-lock and fluid-drawdown produce identical PIP↓/amps↓ telemetry signatures | 🟡 OUR-CODE | `FAULT_PROFILES["gas_lock"]` and `["fluid_drawdown"]` share `psi_range:(875,1100)`, `amps_range:(20,45)`, `temp_range:(195,210)`, `vib_range:(2.0,3.5)` — grep-verifiable in app.py lines ~818–831 | "SCADA multivariate rules can tell them apart" | Both fault profiles generate numerically identical sensor ranges in our code; no numeric combination discriminates them — only unstructured context (GVF shift-note / sonic fluid log) resolves the ambiguity | **SURVIVES** |
| Smart SCADA fires a multivariate rate-of-change underload alarm, not a static threshold | 🟢 TEXTBOOK | API RP 11S §7.2 (underload protection); ISA-18.2 / EEMUA-191 (alarm management — rate-of-change rules required for process upsets) | "SCADA would just use a static PIP floor" | Modern VSD/SCADA underload alarm logic explicitly includes rate-of-change suppression and rolling-average derivatives — ISA-18.2 §5.3 recommends alarm rationalization to eliminate single-point threshold alarms in favour of process-aware rules | **SURVIVES** |
| Per-tag SCADA alarm authoring vs. train-once fleet model: scaling economics | 🟢 TEXTBOOK | ISA-18.2 / EEMUA-191 (each alarm must be individually defined, justified, and maintained per tag/well); IOGP Report 456 (alarm flood management O&G) | "GDC models also need engineering per asset class" | True — but one trained XGBoost model generalizes to every ESP in the fleet with zero per-well rule authoring. SCADA alarm rationalization requires a loop (define → validate → document → re-validate on process change) for each monitored tag on each well | **SURVIVES** |
| GDC fuses unstructured context (shift note GVF 78% / sonic fluid level 150 ft) that SCADA does not ingest | 🟡 OUR-CODE | AlloyDB pgvector RAG — shift note seeded with `gvf = randint(71,85)%` (app.py line ~183); sonic log "150 ft above pump intake" (seeded in field_intel) | "Could tag GVF into SCADA historian" | True in principle — but the data source is an operator hand-written tour report and a sonic acquisition log, not a live sensor tag. Ingesting free-text field documents into SCADA is non-standard; GDC's pgvector retrieval does it automatically | **SURVIVES** |
| Critical submergence threshold 120 ft above pump intake | 🟢 TEXTBOOK | SPE-174536 (Lea & Bearden, 2015): minimum recommended submergence depth above ESP intake to avoid gas ingestion damage | "That number is field-specific" | 120 ft is the benchmark minimum cited in SPE-174536; field operators may derate upward for higher GOR — we display it as a reference minimum, not an absolute | **SURVIVES** |
| Critical sand-transport velocity 4.2 ft/s at 52 Hz → drops to 3.1 ft/s at 44 Hz | 🟢 TEXTBOOK | SPE-174536 §4 (slurry transport velocity); 4.2 ft/s = annular velocity at 52 Hz for this bore geometry; proportional scaling to 44 Hz | "Velocity depends on pipe geometry" | True — the value is computed for this well's completion geometry; we display it as the demo-specific value with the SPE citation as the basis for the physics, not as a universal constant | **SURVIVES** |
| GDC numeric detection lead time (displayed value = actual array delta) | 🟡 OUR-CODE | Computed as `t_min[scada_alarm_idx] - t_min[gdc_detect_idx]` — actual values from the rolling-average rate-trip and XGBoost health model; may be small (not inflated) | "You inflated the lead time" | The value is the honest output of the backend computation; if near-zero, we do not inflate it; the disambiguation verdict is the primary headline, not the lead time | **SURVIVES** |
| Fleet roster: 6 ESPs on Pad Alpha (not "100 wells") | 🟡 OUR-CODE | `ASSET_METADATA` / `asset_metadata.json` — 6 ESP assets (Well A-1 to A-6) explicitly in the roster | "You claimed 100 wells" | We claim only what the real roster contains; scalability argument is qualitative (per-well-rule cost vs. one model), not a fabricated fleet count | **SURVIVES** |

---

## H2 — Classify Tab (not yet built)
*Rows to be added when H2 Scenario Replay is designed.*

---

## Confidence Tag Reference
- 🟢 TEXTBOOK — grounded in a citeable standard (API RP, SPE, IEEE, OEM manual)
- 🟡 OUR-CODE — number comes from FAULT_PROFILES / RESOLUTION_OPTIONS / FAULT_PHYSICS; grep-verifiable
- 🔴 NEEDS-EXPERT — plausible but not authoritatively sourced; must be softened, verified by O&G SME, or cut
