# Next Session Prompt — ESP v2 Redesign (Sprint 5 v1 Complete: Begin Sprint 5 v2)

## Header
**Date:** May 21, 2026
**Live URL:** http://gdc-pm.bdau.io
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation
**Namespace:** gdc-pm
**Current Image Tag:** latest (Sprint 5 v1, commit c8c0b54)
✅ Working tree clean. Two commits this session: `c8c0b54` (UI) and `a29dfb7` (docs).

---

## What Was Done This Session

### Sprint 5 v1 — CSS Flexbox Digital Twin + Label Updates (committed `c8c0b54`)

#### 1. Digital Twin Diagram — Replaced SVG Overlay with CSS Flexbox

**Why changed:** The SVG + absolute-positioned `.pad-well-overlay` approach (Sprint 4) had lines running visually through the opaque well nodes, fragile percentage-based positioning that broke on resize, and labels that could be obscured.

**What replaced it:** A `.twin-diagram` container with a 5-tier CSS Flexbox layout. All relevant CSS uses the `.twin-*` prefix.

**Layout structure (top to bottom):**

```
[GENERATOR] [A/C]  |  [BROKER] [GDC AI] [SCADA]  |  [STARLINK]
                   |   ─────── NETWORK BAR ──────  |
                   ↓ (network lines, blue)           ↓
         [A-1] [A-2] [A-3] [A-4] [A-5] [A-6]    ← 72×72px opaque ESP nodes
                ↓ (gas lines, Google Blue #8ab4f8)
         ════════════ PRODUCTION HEADER ═══════→ SEPARATOR
         [Legend: Network/Data | Gas/Fluid | Nominal | Degrading | Critical]
```

**Key CSS classes (all in `index.html` `<style>` block):**
- `.twin-diagram` — outer container, dark bg, subtle border
- `.twin-top-row` — flex row aligning external assets + structure + starlink
- `.twin-external-left` — Generator + A/C column (outside structure)
- `.twin-external-right` — Starlink column (outside structure)
- `.twin-structure` — dashed `#5a6a7a` border; contains broker/GDC/SCADA + network bar
- `.twin-equip-row` — horizontal flex of equipment boxes inside structure
- `.twin-equip-box` + `.twin-equip-broker` / `.twin-equip-gdc` / `.twin-equip-scada` / `.twin-equip-ext` / `.twin-equip-ac` — styled equipment tiles
- `.twin-network-bar` — 6px horizontal blue bar at bottom of structure
- `.twin-network-label` — "SHARED EDGE NETWORK — Pub/Sub Data Bus" label
- `.twin-network-lines-row` — flex row with spacers + `.twin-net-lines` (6 vertical network line segments)
- `.twin-net-line` / `.twin-net-line-seg` / `.twin-net-junction` — individual vertical network lines
- `.twin-wells-row` — flex row of 6 `.twin-well-col` containers
- `.twin-well-col` — contains `.asset-node.esp-node` + `.twin-well-label` ("A-1" through "A-6")
- `.twin-wells-row .asset-node` — overrides size to 72×72px with `!important`
- `.twin-wells-row .health-green/amber/red` — opaque health colour fills (use `!important` to override global semi-transparent version)
- `.twin-gas-lines-row` — flex row of 6 `.twin-gas-line` with Google Blue gas junction dots + line segments
- `.twin-pipeline-row` — horizontal pipeline bar + arrow
- `.twin-pipeline-labels` — "PRODUCTION HEADER" and "→ SEPARATOR" labels
- `.twin-legend` — bottom legend strip
- `.gdc-led` / `.gdc-led2` — animated LED indicators on GDC AI box

**Vue interaction wiring (in `.twin-wells-row`):**
- `v-for="(assetId, idx) in SITES.pad_alpha.assets"` iterates 6 wells
- `@contextmenu.prevent="showAssetContextMenu($event, assetId)"` — right-click fault injection
- `@click="openDeepDive(assetId, activeDegradesMap[assetId]?.fault_type || null)"` — left-click deep dive
- `:class="[getAssetHealthClass(assetId), {selected: ddAssetId === assetId}]"` — live health + selection highlight
- `padWellStyle(idx)` method still exists in JS but is **not used** — can be cleaned up in a future session

**Network line spacers:** `twin-line-spacer-left` is `width:80px` and `twin-line-spacer-right` is `width:56px`. These are approximations — may need visual tuning after live testing to align lines with wells.

#### 2. Deep Dive Header — RUL Labels Updated

| Old Label | New Label | Data source |
|-----------|-----------|-------------|
| Base RUL | **Initial RUL** | `degStatus.time_to_scada_minutes` |
| Adjusted RUL (AI Fusion) | **AI Informed RUL** | `degStatus.adjusted_rul_minutes` |

Both appear as pill badges in the `.dd-header` when a fault is active.

#### 3. Evidence Panel — Label Updated

| Old | New |
|-----|-----|
| "Live Intelligence Feed" | "📄 RAG Context Documents" |

The section header in Column 1 of the Deep Dive now reads "📄 RAG Context Documents". The section shows the dynamically generated enterprise documents (lab reports, shift notes, PM records, VFD logs) that `generate_dynamic_documents()` in `app.py` creates and pushes to ChromaDB. These documents directly feed the Gemma4 LLM prompt AND the `adjust_rul_with_documents()` regex-based multiplier that produces the "AI Informed RUL".

**Not yet updated** (open item for Sprint 5 v2):
- The "All ▾" drill-down modal title still reads "All Intelligence Feed Items" → should be "All RAG Context Documents"
- The loading placeholder reads "Ingesting unstructured data sources…" → can stay as-is

---

## Current Cluster State

| Pod | Status |
|-----|--------|
| `alloydb-omni` | ✅ 1/1 Running |
| `event-processor` | ✅ 1/1 Running |
| `fault-trigger-ui` | ✅ 1/1 Running (Sprint 5 v1, HTTP 200) |
| `inference-api` | ✅ 1/1 Running |
| `grafana` | ✅ 1/1 Running |
| `telemetry-simulator` | ✅ 1/1 Running |
| `ollama` | ⏳ 0/1 Pending (awaiting L4 GPU node from GKE Autopilot) |

---

## Immutable Design Decisions (Do Not Reverse)

1. **No Activity Stream on the landing page.** The right-side activity stream was removed from scope. Do not add it back.
2. **CSS Flexbox only for the Digital Twin.** SVG + HTML overlay must never return. If the diagram needs changes, edit the `.twin-*` CSS classes and the HTML tiers in `.twin-diagram`.
3. **Terminology:** "Initial RUL" / "AI Informed RUL" / "RAG Context Documents" — these are agreed labels.
4. **GDC data flow:** GDC Edge AI and SCADA RTU both independently subscribe to the Edge Broker Pub/Sub. GDC is NOT downstream of SCADA. This is a critical demo talking point encoded in the diagram.

---

## Outstanding Development Items — Sprint 5 v2

### Must-Do (visual quality)
1. **Live visual test of the Flexbox diagram** — load http://gdc-pm.bdau.io and verify:
   - Network lines (Tier 2) align approximately above the wells (Tier 3)
   - Wells are opaque and labels (A-1 through A-6) are clearly visible
   - Gas lines (Google Blue) drop cleanly from wells to pipeline
   - No labels are obscured
   - Right-click context menu on wells still works
   - Left-click opens Deep Dive
   - Fault injection changes well node colour (amber → red)
   - Active fault shows pulse ring on the well

2. **Fix spacer widths if alignment is off** — edit `.twin-network-lines-row` spacer `style="width:80px"` and `style="width:56px"` values to tune alignment with wells.

3. **Update drill-down modal title** — change "All Intelligence Feed Items" → "All RAG Context Documents" in the `#feed-modal` template.

### Nice-to-Have
4. **Equipment→Network subscription lines** — currently the link between each equipment box and the network bar is implied by the shared bar. Could add a subtle dashed `border-left` stub from each equipment box down to the network bar for visual clarity.

5. **Ollama GPU node** — pending GKE Autopilot L4 provisioning. No action needed, monitor with `kubectl get pod ollama-0 -n gdc-pm -w`.

---

## Constraints
- `terraform/gke.tf` must NOT be applied.
- All demo UI changes go into `gke/fault-trigger-ui/index.html` and logic into `gke/fault-trigger-ui/app.py`.
- Preserve XGBoost health score models (`*.ubj` files).
- `/api/*` endpoints must remain backward-compatible.
- Do NOT commit to `main`.
- O&G scenarios and physics must remain authentic.
- **No browser on the SSH remote** — `browser_action` tool must NOT be used.

---

## Rebuild & Deploy Commands
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```

---

## Key Lessons Learned This Session
- SVG + absolute-positioned HTML overlay fails at resize — CSS Flexbox is the right approach.
- `.health-green/amber/red` global rules are semi-transparent. The `.twin-wells-row` scoped overrides use `!important` to force opaque fills on well nodes.
- The `padWellStyle(idx)` method in Vue JS is now dead code (kept for safety but no longer called). Can be removed in a future cleanup commit.
- Rigorous `NEXT_SESSION_PROMPT.md` documentation prevents context loss between sessions — include CSS class names, Vue wiring details, and exact data field names alongside design intent.
