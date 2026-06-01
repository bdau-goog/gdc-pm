#!/usr/bin/env python3
"""
Replace the Pane 1 text comparison cards with a visual mirrored SCADA pipeline.
The SCADA pipeline runs below the GDC pipeline, same column structure, muted styling.
"""

FILE = 'gke/fault-trigger-ui/index.html'
with open(FILE) as f:
    html = f.read()

OLD = '''            <!-- Key differentiator comparison -->
            <div class="arch-compare-row">
              <div class="arch-compare-card acc-scada">
                <div class="acc-title acc-title-scada">🛢 Traditional SCADA Only</div>
                <ul class="acc-items">
                  <li class="no">Single-threshold alarm only</li>
                  <li class="no">15-min downsampled WAN poll</li>
                  <li class="no">No unstructured data fusion</li>
                  <li class="no">Reactive emergency dispatch</li>
                </ul>
              </div>
              <div class="arch-compare-card acc-gdc">
                <div class="acc-title acc-title-gdc">⚡ GDC Edge AI (E-House)</div>
                <ul class="acc-items">
                  <li class="yes">Multivariate ML detection</li>
                  <li class="yes">5s local stream — no WAN needed</li>
                  <li class="yes">OEM manuals + ops records fused</li>
                  <li class="yes">Scheduled proactive intervention</li>
                </ul>
              </div>
            </div>'''

NEW = '''            <!-- ── SCADA Legacy Path (parallel comparison) ── -->
            <div style="display:flex;align-items:center;gap:10px;margin:14px 0 10px;padding:6px 14px;background:rgba(120,80,80,0.08);border:1px solid rgba(200,100,100,0.25);border-radius:6px">
              <span style="font-size:0.65rem;font-weight:700;color:rgba(220,130,130,0.9);text-transform:uppercase;letter-spacing:0.09em">🛢 Traditional SCADA Path</span>
              <span style="font-size:0.6rem;color:var(--muted);font-style:italic">how this field would look without GDC</span>
            </div>

            <div style="display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap">

              <!-- S1: Same field sensors -->
              <div class="arch-stage" style="flex:1;min-width:110px;overflow:hidden;background:rgba(80,80,80,0.06);border:1px solid rgba(120,120,120,0.25)">
                <div class="arch-stage-title" style="color:var(--muted);font-size:0.62rem">📡 1. Field Sensors</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-muted"><span>Same sensors</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.6rem">Hardwired to RTU</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.12);font-size:1.2rem;padding-top:8px">→</div>

              <!-- S2: RTU WAN poll -->
              <div class="arch-stage" style="flex:1;min-width:110px;overflow:hidden;background:rgba(80,80,80,0.06);border:1px solid rgba(120,120,120,0.25)">
                <div class="arch-stage-title" style="color:var(--muted);font-size:0.62rem">🖥 2. RTU → WAN</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-muted"><span>15-min downsampled</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.6rem">Slow WAN to central SCADA</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.12);font-size:1.2rem;padding-top:8px">→</div>

              <!-- S3: Threshold check (no ML) -->
              <div class="arch-stage" style="flex:1;min-width:110px;overflow:hidden;background:rgba(100,40,40,0.07);border:1px solid rgba(200,100,100,0.25)">
                <div class="arch-stage-title" style="color:rgba(220,130,130,0.8);font-size:0.62rem">❌ 3. No ML</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-muted"><span>Single-sensor rules</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.6rem">Fixed thresholds only</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.12);font-size:1.2rem;padding-top:8px">→</div>

              <!-- S4: Basic historian (no context) -->
              <div class="arch-stage" style="flex:1;min-width:110px;overflow:hidden;background:rgba(100,40,40,0.07);border:1px solid rgba(200,100,100,0.25)">
                <div class="arch-stage-title" style="color:rgba(220,130,130,0.8);font-size:0.62rem">❌ 4. No Context</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-muted"><span>SCADA Historian</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.6rem">Raw values, no documents</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.12);font-size:1.2rem;padding-top:8px">→</div>

              <!-- S5: Alarm (no AI) -->
              <div class="arch-stage" style="flex:1;min-width:110px;overflow:hidden;background:rgba(100,40,40,0.07);border:1px solid rgba(200,100,100,0.25)">
                <div class="arch-stage-title" style="color:rgba(220,130,130,0.8);font-size:0.62rem">❌ 5. No AI</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-muted"><span>Threshold alarm only</span></div>
                  <div class="arch-chip chip-muted"><span style="font-size:0.6rem">Trips when damage is done</span></div>
                </div>
              </div>

              <div style="display:flex;align-items:center;color:rgba(255,255,255,0.12);font-size:1.2rem;padding-top:8px">→</div>

              <!-- S6: Control room HMI (reactive) -->
              <div class="arch-stage" style="flex:1;min-width:110px;overflow:hidden;background:rgba(140,30,30,0.1);border:1px solid rgba(220,80,80,0.35)">
                <div class="arch-stage-title" style="color:rgba(240,100,100,0.9);font-size:0.62rem">🚨 6. Control Room HMI</div>
                <div class="arch-stage-body" style="flex-direction:column;gap:4px">
                  <div class="arch-chip chip-muted" style="border-color:rgba(220,80,80,0.3)"><span style="color:rgba(240,100,100,0.85)">Emergency dispatch</span></div>
                  <div class="arch-chip chip-muted" style="border-color:rgba(220,80,80,0.3)"><span style="font-size:0.6rem;color:rgba(240,100,100,0.7)">After damage occurs</span></div>
                </div>
              </div>

            </div><!-- scada flow row -->'''

assert OLD in html, "Pattern not found!"
html = html.replace(OLD, NEW, 1)

with open(FILE, 'w') as f:
    f.write(html)

print("SUCCESS: SCADA pipeline row added to Pane 1")
# Verify
with open(FILE) as f: v = f.read()
print("  ✅ SCADA Path label present:", "Traditional SCADA Path" in v)
print("  ✅ RTU → WAN stage present:", "RTU → WAN" in v)
print("  ✅ Control Room HMI present:", "Control Room HMI" in v)
print("  ✅ Old compare cards removed:", "acc-title-scada" not in v.split("<!-- pane overview -->")[0].split("pane detection")[0])
