// terms.js — GDC briefing deck content dictionary
// Lever E (DEMO_MASTER §7.5): volatile terms resolved at load time.
// data-term="key" elements are filled by slide.js injectTerms() after DOMContentLoaded.
//
// CONTENT POLICY: No authored hard dollar figures in narrative/briefing copy.
// Use comparative language only. Live model outputs (health score, lead-time,
// H3 +77.9 bbl/d) are exempt — they are labeled model outputs, not authored claims.

window.TERMS = {
  // ── Terminology ───────────────────────────────────────────────────────────
  pip:              'Pump Inlet Pressure',
  pip_abbr:         'Pump Inlet Pressure',

  // ── H1 comparative cost phrases ──────────────────────────────────────────
  // Replaces authored ~$2,500 / ~$150k in briefing copy (DEMO_MASTER §7.5).
  cost_trim:        'a low-cost control-room adjustment',
  cost_trim_short:  'low-cost — a VFD command',
  cost_pull:        'a six-figure workover',
  cost_pull_risk:   'workover-level risk',
  cost_shutdown:    'trip and restart costs',

  // ── H2 comparative cost phrases ───────────────────────────────────────────
  // Replaces authored ~$3k–$6k / ~$70k–$100k in briefing copy.
  cost_hotoi:       'a low-cost surface truck job',
  cost_hotoi_scope: 'surface-only · no rig · no wireline',
  cost_no_pull:     'far less than pulling the pump',
  cost_pull_h2:     'pulling the pump on a wrong diagnosis',
};
