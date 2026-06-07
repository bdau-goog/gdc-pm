# Architecture Tab — Native HTML/CSS Implementation Plan

**Status:** Ready for implementation  
**Target:** Add a "How It Works" tab to `gke/fault-trigger-ui/index.html`  
**Approach:** Native HTML/CSS Flexbox (Responsive, Theme-compliant, No external dependencies)

---

## Design Philosophy

The diagram must look like a native part of the UI, not an embedded image. It will use:
- The app's existing CSS variables (`--bg`, `--surf`, `--surf2`, `--border`, `--border2`, `--text`, `--text2`, `--muted`, `--blue`, `--green`, `--orange`, `--purple`)
- Flexbox for responsive scaling
- CSS pseudo-elements (`::after` and `::before`) to draw clean, subtle flow arrows without SVG complexity
- Flex layouts to group logical tiers (Input → Edge → Output)

---

## The HTML Structure

We will insert a new `<style>` block scoped to the new tab, followed by the HTML structure. 

### Insertion Point
Insert this entirely new block into `gke/fault-trigger-ui/index.html` around line 1256 (after the `</div>` that closes `#tab-telemetry`, and before the `</div><!-- app-body -->`).

### The Code Block (Copy & Paste)

```html
    <!-- ══ TAB: ARCHITECTURE ══ -->
    <style>
      .arch-container { padding: 32px 48px; background: var(--bg); overflow-y: auto; height: 100%; display: flex; flex-direction: column; align-items: center; }
      .arch-header { width: 100%; max-width: 1200px; margin-bottom: 32px; }
      .arch-title { font-size: 1.2rem; font-weight: 700; color: var(--text2); margin-bottom: 8px; }
      .arch-subtitle { font-size: 0.85rem; color: var(--muted); }
      
      .arch-diagram { display: flex; gap: 40px; width: 100%; max-width: 1200px; justify-content: space-between; align-items: stretch; }
      .arch-tier { display: flex; flex-direction: column; gap: 16px; flex: 1; }
      .arch-tier-title { font-size: 0.75rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 8px; }
      
      .arch-node { background: var(--surf); border: 1px solid var(--border); border-radius: 8px; padding: 16px; position: relative; transition: border-color 0.2s, transform 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
      .arch-node:hover { border-color: var(--border2); transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.2); }
      .arch-node-title { font-size: 0.9rem; font-weight: 600; color: var(--text2); margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
      .arch-node-desc { font-size: 0.75rem; color: var(--muted); line-height: 1.4; }
      
      .arch-box { background: rgba(255,255,255,0.02); border: 1px dashed var(--border); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 16px; }
      .arch-box-title { font-size: 0.7rem; font-weight: 600; color: var(--muted); letter-spacing: 1px; text-align: center; }

      /* Highlighted Nodes */
      .node-db { border-color: rgba(30,144,255,0.3); background: linear-gradient(145deg, var(--surf) 0%, rgba(30,144,255,0.05) 100%); }
      .node-db .arch-node-title { color: var(--blue); }
      
      .node-ml { border-color: rgba(255,140,0,0.3); background: linear-gradient(145deg, var(--surf) 0%, rgba(255,140,0,0.05) 100%); }
      .node-ml .arch-node-title { color: var(--orange); }
      
      .node-llm { border-color: rgba(179,136,255,0.3); background: linear-gradient(145deg, var(--surf) 0%, rgba(179,136,255,0.05) 100%); }
      .node-llm .arch-node-title { color: var(--purple); }
      
      .node-demo { border-style: dashed; opacity: 0.6; }

      /* Flow Arrows */
      .arrow-right::after {
        content: '→'; position: absolute; right: -28px; top: 50%; transform: translateY(-50%);
        color: var(--border2); font-size: 1.2rem; font-weight: bold;
      }
      .arrow-down::after {
        content: '↓'; position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%);
        color: var(--border2); font-size: 1.2rem; font-weight: bold;
      }
      
      /* Subtle path indicators */
      .path-label { display: inline-block; font-size: 0.65rem; background: var(--bg); border: 1px solid var(--border); border-radius: 4px; padding: 2px 6px; color: var(--muted); margin-top: 8px; }
      .path-blue { color: var(--blue); border-color: rgba(30,144,255,0.2); background: rgba(30,144,255,0.05); }
      .path-orange { color: var(--orange); border-color: rgba(255,140,0,0.2); background: rgba(255,140,0,0.05); }
      .path-purple { color: var(--purple); border-color: rgba(179,136,255,0.2); background: rgba(179,136,255,0.05); }
      .path-green { color: var(--green); border-color: rgba(0,230,118,0.2); background: rgba(0,230,118,0.05); }
    </style>

    <div id="tab-architecture" class="main-tab-content" :class="{active: mainTab==='architecture'}">
      <div class="arch-container">
        <div class="arch-header">
          <div class="arch-title">GDC Predictive Maintenance — How It Works</div>
          <div class="arch-subtitle">Production deployment architecture · Fully localized on-premises edge AI</div>
        </div>
        
        <div class="arch-diagram">
          
          <!-- TIER 1: INPUT -->
          <div class="arch-tier">
            <div class="arch-tier-title">1. Data Sources</div>
            
            <div class="arch-node arrow-right">
              <div class="arch-node-title">📡 Field Sensors</div>
              <div class="arch-node-desc">ESP, Compressor, Turbine, Transformer</div>
              <div class="path-label path-blue">Live Telemetry</div>
            </div>
            
            <div class="arch-node arrow-right">
              <div class="arch-node-title">📄 Operations Records</div>
              <div class="arch-node-desc">Shift Notes, Work Orders, Lab Reports</div>
              <div class="path-label path-purple">Context Vectorized</div>
            </div>
            
            <div class="arch-node arrow-right">
              <div class="arch-node-title">📚 Industry Corpus</div>
              <div class="arch-node-desc">ISO Standards, OEM Manuals</div>
              <div class="path-label path-purple">RAG Knowledge Base</div>
            </div>
            
            <div class="arch-node node-demo arrow-right" style="margin-top:24px">
              <div class="arch-node-title">⚙️ Fault Injector</div>
              <div class="arch-node-desc">(Demo Only)</div>
            </div>
          </div>
          
          <!-- TIER 2: LEGACY OT & EDGE BUS -->
          <div class="arch-tier">
            <div class="arch-tier-title">2. Legacy OT & Edge Bus</div>
            
            <div class="arch-node arrow-right">
              <div class="arch-node-title">SCADA</div>
              <div class="arch-node-desc">Legacy Threshold Monitoring</div>
              <div class="path-label">Static Alarm Trigger</div>
            </div>
            
            <div class="arch-box" style="margin-top:16px; flex:1">
              <div class="arch-box-title">GDC EDGE CLUSTER</div>
              
              <div class="arch-node arrow-down">
                <div class="arch-node-title">RabbitMQ</div>
                <div class="arch-node-desc">Real-Time Telemetry Bus</div>
              </div>
              
              <div class="arch-node node-db arrow-right">
                <div class="arch-node-title">AlloyDB Omni</div>
                <div class="arch-node-desc">PostgreSQL + pgvector<br/>Unified Asset Data Store</div>
                <div style="display:flex; gap:4px; flex-wrap:wrap; margin-top:8px">
                  <div class="path-label path-blue">telemetry_events</div>
                  <div class="path-label path-purple">rag_documents</div>
                  <div class="path-label path-purple">field_intel</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- TIER 3: AI ENGINE -->
          <div class="arch-tier">
            <div class="arch-tier-title">3. AI Engine (GDC)</div>
            
            <div class="arch-box" style="flex:1">
              <div class="arch-box-title">NVIDIA L4 GPU ACCELERATED</div>
              
              <div class="arch-node node-ml arrow-right" style="margin-top:auto">
                <div class="arch-node-title">XGBoost ML</div>
                <div class="arch-node-desc">Multivariate Health Score & Fault Probability</div>
                <div class="path-label path-orange">Initial RUL</div>
              </div>
              
              <div class="arch-node node-llm arrow-right" style="margin-top:16px; margin-bottom:auto">
                <div class="arch-node-title">Gemma 27b</div>
                <div class="arch-node-desc">Edge LLM + RAG Synthesis</div>
                <div style="display:flex; gap:4px; flex-wrap:wrap; margin-top:8px">
                  <div class="path-label path-purple">Reads Ops Records</div>
                  <div class="path-label path-orange">Ingests ML Score</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- TIER 4: OUTPUT -->
          <div class="arch-tier">
            <div class="arch-tier-title">4. Operator Interface</div>
            
            <div class="arch-node">
              <div class="arch-node-title">AI-Informed RUL</div>
              <div class="arch-node-desc">vs. Legacy SCADA Estimate</div>
              <div class="path-label path-orange">Context-Aware</div>
            </div>
            
            <div class="arch-node">
              <div class="arch-node-title">Recommended Action</div>
              <div class="arch-node-desc">Human-in-the-Loop (HITL) Approval</div>
              <div class="path-label path-green">Actionable Insight</div>
            </div>
            
            <div class="arch-node">
              <div class="arch-node-title">Financial Ledger</div>
              <div class="arch-node-desc">ROI Tracking & Cost Avoided</div>
              <div class="path-label path-green">Business Value</div>
            </div>
            
            <div class="arch-node" style="margin-top:16px">
              <div class="arch-node-title">Asset Chatbot</div>
              <div class="arch-node-desc">Operator Q&A & Investigations</div>
              <div class="path-label path-purple">RAG Empowered</div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
```

---

## Tab Button Insertion Point

Insert this around line 491 (after the Fleet Telemetry `hdr-tab`):

```html
<div class="hdr-tab" :class="{active: mainTab==='architecture'}" @click="mainTab='architecture'">How It Works</div>
```

---

## Verification

1. Insert the two HTML blocks above into `gke/fault-trigger-ui/index.html`.
2. Build and deploy the UI container.
3. Reload the UI. The "How It Works" tab will show a beautiful, responsive, dark-themed HTML/CSS diagram that uses the exact same visual language as the rest of the application.
