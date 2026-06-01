#!/usr/bin/env python3
"""
Architecture tab v4 polish based on user review:
1. Vibration mm/s → Vibration (consistency — other sensors have no units)
2. Edge Bus → Message Bus
3. AlloyDB + pgvector → AlloyDB (in Pane 1 Context Store chip)
4. Pane 4: RAG Manuals / Stream 2 → Industry Corpus; add explicit ↓ arrow row between 3-box grid and AlloyDB
5. Pane 5: remove 'Outputs →' label; replace with ↓ arrow; AI-Informed RUL → AI-Based RUL; Action Recommendation → Actions
6. Stage 6 / Pane 6: Operator → Operations throughout
"""

FILE = 'gke/fault-trigger-ui/index.html'
with open(FILE, 'r') as f:
    html = f.read()

changes = []

def replace_once(old, new, label):
    global html
    assert old in html, f"PATTERN NOT FOUND: {label}"
    html = html.replace(old, new, 1)
    changes.append(label)

def replace_all(old, new, label):
    global html
    count = html.count(old)
    assert count > 0, f"PATTERN NOT FOUND: {label}"
    html = html.replace(old, new)
    changes.append(f"{label} ({count}x)")

# ── 1. Vibration mm/s → Vibration (in Pane 1 flow, Pane 2 info panel) ──
replace_all('<div class="arch-chip chip-orange"><span>Vibration mm/s</span></div>',
            '<div class="arch-chip chip-orange"><span>Vibration</span></div>',
            'Vibration chip in flow diagram')

# ── 2. Edge Bus → Message Bus (Pane 1 stage title) ──
replace_once('<div class="arch-stage-title">📨 2. Edge Bus</div>',
             '<div class="arch-stage-title">📨 2. Message Bus</div>',
             'Edge Bus → Message Bus in Pane 1')

# ── 3. AlloyDB + pgvector → AlloyDB (Pane 1 Context Store chip) ──
replace_once('<div class="arch-chip chip-blue"><span>AlloyDB + pgvector</span></div>',
             '<div class="arch-chip chip-blue"><span>AlloyDB</span></div>',
             'AlloyDB+pgvector → AlloyDB in Pane 1')

# ── 4a. Pane 4 Stream 2: OEM Manuals (RAG) → Industry Corpus ──
replace_once('<div class="arch-stage-title" style="font-size:0.65rem;color:#b388ff">📚 Stream 2 · OEM Manuals (RAG)</div>',
             '<div class="arch-stage-title" style="font-size:0.65rem;color:#b388ff">📚 Stream 2 · Industry Corpus</div>',
             'Stream 2 title → Industry Corpus')

# ── 4b. Pane 4: Replace converging arrow div with explicit 3-arrow row ──
replace_once(
    '            <!-- Converging arrow -->\n            <div class="arch-connector" style="text-align:center">↓ <span class="arch-connector-label">All three streams unified in AlloyDB · semantic query via pgvector (all-MiniLM-L6-v2)</span></div>',
    '''            <!-- Converging arrows from 3 streams -->
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:4px">
              <div style="text-align:center;font-size:1.2rem;color:rgba(255,109,0,0.5)">↓</div>
              <div style="text-align:center;font-size:1.2rem;color:rgba(179,136,255,0.5)">↓</div>
              <div style="text-align:center;font-size:1.2rem;color:rgba(30,144,255,0.5)">↓</div>
            </div>
            <div class="arch-connector" style="text-align:center;margin-bottom:8px"><span class="arch-connector-label">All three streams unified · semantic query via pgvector</span></div>''',
    'Pane 4: explicit 3-arrow row into AlloyDB')

# ── 4c. Pane 4 AlloyDB chip: AlloyDB + pgvector → AlloyDB Omni ──
replace_once('<div class="arch-stage-title">🗄 AlloyDB Omni — Unified Context (PostgreSQL + pgvector)</div>',
             '<div class="arch-stage-title">🗄 AlloyDB Omni — Unified Context Store</div>',
             'AlloyDB Omni title simplified')

# ── 4d. Pane 4 AlloyDB chip label for RAG: rag_documents → industry_corpus ──
replace_once('<div class="arch-chip chip-purple"><span class="arch-chip-label">Table</span><span class="arch-chip-val">rag_documents (18 rows)</span></div>',
             '<div class="arch-chip chip-purple"><span class="arch-chip-label">Table</span><span class="arch-chip-val">industry_corpus (18 rows)</span></div>',
             'Pane 4 AlloyDB rag_documents → industry_corpus')

# ── 4e. Pane 4 Context Assembled title: OEM Manual → Industry Corpus ──
replace_all('[OEM Manual]', '[Industry Corpus]', 'OEM Manual → Industry Corpus in assembled context')

# ── 5a. Pane 5 Gemma stage: remove 'Outputs →' label; replace with ↓ arrow ──
replace_once(
    '''                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-purple"><span>Gemma 27b (GPU)</span></div>
                </div>
                <div style="font-size:0.55rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:0.07em;margin:6px 0 3px">Outputs →</div>
                <div style="display:flex;flex-direction:column;gap:3px">
                  <div class="arch-chip chip-orange"><span>AI-Informed RUL</span></div>
                  <div class="arch-chip chip-green"><span>Action Recommendation</span></div>
                </div>''',
    '''                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-purple"><span>Gemma 27b (GPU)</span></div>
                </div>
                <div style="font-size:1.1rem;color:rgba(255,255,255,0.2);text-align:center;margin:4px 0">↓</div>
                <div style="display:flex;flex-direction:column;gap:3px">
                  <div class="arch-chip chip-orange"><span>AI-Based RUL</span></div>
                  <div class="arch-chip chip-green"><span>Actions</span></div>
                </div>''',
    'Pane 1 AI Fusion: Outputs→ to ↓ arrow; relabel RUL + Actions')

# ── 5b. Pane 5 AI Reasoning output cards: AI-Informed RUL → AI-Based RUL ──
replace_once(
    '<div style="font-size:0.6rem;font-weight:700;color:var(--orange);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px">📊 Output — AI-Informed RUL</div>',
    '<div style="font-size:0.6rem;font-weight:700;color:var(--orange);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px">📊 Output — AI-Based RUL</div>',
    'Pane 5 output card: AI-Informed → AI-Based RUL')

replace_once(
    '<div style="font-size:0.6rem;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px">✅ Output — Action Recommendation</div>',
    '<div style="font-size:0.6rem;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px">✅ Output — Actions</div>',
    'Pane 5 output card: Action Recommendation → Actions')

# ── 6a. Pane 1 stage 6 title: 👤 6. Operator → 👤 6. Operations ──
replace_once('<div class="arch-stage-title">👤 6. Operator</div>',
             '<div class="arch-stage-title">👤 6. Operations</div>',
             'Stage 6 title: Operator → Operations')

# ── 6b. Pane 6 header: Operator Interface → Operations Interface ──
replace_once('<h2>Operator Interface — Human-in-the-Loop & ROI</h2>',
             '<h2>Operations Interface — Human-in-the-Loop & ROI</h2>',
             'Pane 6 header: Operator → Operations')

# ── 6c. Pane 6 sub-tab label (if it still says 'Operator Value') ──
replace_once('<span class="ast-num">6</span> Operator Value',
             '<span class="ast-num">6</span> Operations',
             'Sub-tab 6 label: Operator Value → Operations')

# ── Also fix Pane 1 Context Store header description ──
replace_once('<h2>Context Fusion — Three Streams into AlloyDB</h2>',
             '<h2>Context Fusion — Three Streams into AlloyDB</h2>',
             'Pane 4 header (no change needed)')

# Write back
with open(FILE, 'w') as f:
    f.write(html)

print("SUCCESS — Changes applied:")
for c in changes:
    print(f"  ✅ {c}")

# Spot checks
spots = [
    ('Message Bus', 'Message Bus chip present'),
    ('AI-Based RUL', 'AI-Based RUL present'),
    ('Industry Corpus', 'Industry Corpus present'),
    ('"Vibration"', 'Vibration without units'),
    ('6. Operations', 'Stage 6 renamed'),
    ('Operations Interface', 'Pane 6 header renamed'),
    ('Operations</span>', 'Sub-tab 6 renamed'),
    ('Outputs \u2192', 'Outputs → REMOVED'),
]
with open(FILE, 'r') as f:
    v = f.read()
for term, label in spots:
    if term == 'Outputs \u2192':
        status = '✅ ABSENT' if term not in v else '❌ STILL PRESENT'
    else:
        status = '✅' if term in v else '❌ MISSING'
    print(f"  {status} {label}")
