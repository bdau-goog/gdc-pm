#!/usr/bin/env python3
"""
Session 10 — Grafana Stat Panel Injector
=========================================
Adds 14 per-asset stat panels (PSI health cards) to the GDC-PM dashboard,
one card per asset grouped under each site-zone row header.

Each stat panel:
  - Shows the last-5-min average PSI for that specific asset
  - Color-codes green/orange/red by asset-class thresholds
  - Has a panel link to /d/gdc-pm-main?var-asset=<ID>&kiosk=tv
    so clicking the card filters all charts to that single asset

Layout changes (Y shifts):
  +4 rows after Pad Alpha row  (6 ESP stats in one row, h=4)
  +4 rows after Pad Bravo row  (4 GLIFT stats in one row, h=4)
  +4 rows after Rig 42 row     (4 Rig stats in one row, h=4)
  Total: +12 to Edge AI section and below
"""

import json, re, pathlib, sys

CONFIGMAP_PATH = pathlib.Path("/home/brian/gdc-pm/gke/grafana/k8s/grafana-configmap.yaml")

# ── Asset definitions ─────────────────────────────────────────────────────────
PAD_ALPHA_ASSETS = [
    ("ESP-ALPHA-1", "ESP-A1"),
    ("ESP-ALPHA-2", "ESP-A2"),
    ("ESP-ALPHA-3", "ESP-A3"),
    ("ESP-ALPHA-4", "ESP-A4"),
    ("ESP-ALPHA-5", "ESP-A5"),
    ("ESP-ALPHA-6", "ESP-A6"),
]
PAD_BRAVO_ASSETS = [
    ("GLIFT-BRAVO-1", "GL-B1"),
    ("GLIFT-BRAVO-2", "GL-B2"),
    ("GLIFT-BRAVO-3", "GL-B3"),
    ("GLIFT-BRAVO-4", "GL-B4"),
]
RIG42_ASSETS = [
    ("MUD-RIG42-1",     "MUD-1",   "mud_pump"),
    ("MUD-RIG42-2",     "MUD-2",   "mud_pump"),
    ("MUD-RIG42-3",     "MUD-3",   "mud_pump"),
    ("TOPDRIVE-RIG42-1","TDRIVE",  "top_drive"),
]

# ── Thresholds per asset class ────────────────────────────────────────────────
THRESHOLDS = {
    "esp": {
        "unit": "pressurepsi",
        "steps": [
            {"color": "red",    "value": None},
            {"color": "orange", "value": 800},
            {"color": "green",  "value": 1100},
            {"color": "yellow", "value": 1700},
            {"color": "red",    "value": 1850},
        ],
        "sql": "SELECT AVG(psi) AS value FROM telemetry_events WHERE asset_id = '{asset_id}' AND event_time > NOW() - INTERVAL '5 minutes'",
    },
    "gas_lift": {
        "unit": "pressurepsi",
        "steps": [
            {"color": "red",    "value": None},
            {"color": "orange", "value": 600},
            {"color": "green",  "value": 850},
            {"color": "yellow", "value": 1100},
            {"color": "red",    "value": 1200},
        ],
        "sql": "SELECT AVG(psi) AS value FROM telemetry_events WHERE asset_id = '{asset_id}' AND event_time > NOW() - INTERVAL '5 minutes'",
    },
    "mud_pump": {
        "unit": "pressurepsi",
        "steps": [
            {"color": "red",    "value": None},
            {"color": "orange", "value": 1800},
            {"color": "green",  "value": 2400},
            {"color": "yellow", "value": 3300},
            {"color": "red",    "value": 3800},
        ],
        "sql": "SELECT AVG(psi) AS value FROM telemetry_events WHERE asset_id = '{asset_id}' AND event_time > NOW() - INTERVAL '5 minutes'",
    },
    "top_drive": {
        "unit": "pressurepsi",
        "steps": [
            {"color": "red",    "value": None},
            {"color": "orange", "value": 2400},
            {"color": "green",  "value": 2700},
            {"color": "yellow", "value": 3200},
            {"color": "red",    "value": 3400},
        ],
        "sql": "SELECT AVG(psi) AS value FROM telemetry_events WHERE asset_id = '{asset_id}' AND event_time > NOW() - INTERVAL '5 minutes'",
    },
}

PANEL_SUBTITLES = {
    "esp":       "Intake PSI",
    "gas_lift":  "Discharge PSI",
    "mud_pump":  "Discharge PSI",
    "top_drive": "Hydraulic PSI",
}

def make_stat_panel(panel_id, asset_id, label, aclass, x, y, w=4, h=4):
    """Build a Grafana stat panel JSON dict for a single asset."""
    cfg = THRESHOLDS[aclass]
    subtitle = PANEL_SUBTITLES[aclass]
    dashboard_link = f"/d/gdc-pm-main?orgId=1&var-asset={asset_id}&kiosk=tv"
    return {
        "id": panel_id,
        "type": "stat",
        "title": label,
        "description": f"{asset_id} — current {subtitle}. Click to drill into single-asset view.",
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "options": {
            "colorMode": "background",
            "graphMode": "area",
            "textMode": "value_and_name",
            "justifyMode": "auto",
            "reduceOptions": {"calcs": ["lastNotNull"]},
        },
        "fieldConfig": {
            "defaults": {
                "unit": cfg["unit"],
                "decimals": 0,
                "thresholds": {
                    "mode": "absolute",
                    "steps": cfg["steps"],
                },
                "links": [
                    {
                        "title": f"Drill into {label}",
                        "url": dashboard_link,
                        "targetBlank": False,
                    }
                ],
            }
        },
        "targets": [
            {
                "datasource": "AlloyDB-Omni",
                "rawSql": cfg["sql"].format(asset_id=asset_id),
                "format": "table",
            }
        ],
    }


def build_stat_row(assets, aclass, start_y, start_id, total_width=24):
    """Build a row of stat panels for a list of (asset_id, label) tuples."""
    n = len(assets)
    w = total_width // n
    panels = []
    for i, entry in enumerate(assets):
        if len(entry) == 2:
            asset_id, label = entry
            cls = aclass
        else:
            asset_id, label, cls = entry
        panels.append(
            make_stat_panel(
                panel_id=start_id + i,
                asset_id=asset_id,
                label=label,
                aclass=cls,
                x=i * w,
                y=start_y,
                w=w,
                h=4,
            )
        )
    return panels


def shift_panels_y(panels, min_y, shift):
    """Shift gridPos.y by `shift` for all panels whose current y >= min_y."""
    for p in panels:
        if p.get("gridPos", {}).get("y", 0) >= min_y:
            p["gridPos"]["y"] += shift


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    raw = CONFIGMAP_PATH.read_text()

    # Extract the JSON block embedded in the YAML (everything after "gdc-pm-dashboard.json: |")
    # Strategy: split on the key, extract indented block, parse as JSON
    match = re.search(r'gdc-pm-dashboard\.json: \|\n([\s\S]+?)(?=\n---|\Z)', raw)
    if not match:
        print("ERROR: Could not locate gdc-pm-dashboard.json block in ConfigMap", file=sys.stderr)
        sys.exit(1)

    indented_json = match.group(1)
    # Find minimum indentation level
    lines = indented_json.split('\n')
    nonempty = [l for l in lines if l.strip()]
    if not nonempty:
        print("ERROR: Empty JSON block", file=sys.stderr)
        sys.exit(1)
    indent = len(nonempty[0]) - len(nonempty[0].lstrip())
    # Dedent by stripping `indent` spaces from each line
    dedented = '\n'.join(l[indent:] if len(l) >= indent else l for l in lines)

    dashboard = json.loads(dedented)
    panels = dashboard["panels"]

    # ── Print current Y coordinates for verification ──────────────────────────
    print("=== Before patch ===")
    for p in panels:
        print(f"  id={p['id']:3d}  y={p.get('gridPos',{}).get('y','?'):3}  title={p.get('title','')[:50]}")

    # ── Step 1: Shift existing panels to make room ────────────────────────────
    # Pad Alpha stat row goes at y=6 (right after the Pad Alpha row header at y=5)
    # Shift all panels at y>=6 by +4
    shift_panels_y(panels, min_y=6, shift=4)
    # After shift, Pad Bravo row is now at y=24+4=28
    # Pad Bravo stat row goes at y=29; shift all panels at y>=29 by +4
    shift_panels_y(panels, min_y=29, shift=4)
    # After shift, Rig 42 row is now at y=34+8=42
    # Rig 42 stat row goes at y=43; shift all panels at y>=43 by +4
    shift_panels_y(panels, min_y=43, shift=4)

    # ── Step 2: Build the three stat rows ─────────────────────────────────────
    # IDs: use 100–105 for Pad Alpha, 110–113 for Pad Bravo, 120–123 for Rig 42
    esp_stats   = build_stat_row(PAD_ALPHA_ASSETS, "esp",      start_y=6,  start_id=100)
    glift_stats = build_stat_row(PAD_BRAVO_ASSETS, "gas_lift", start_y=29, start_id=110)
    rig_stats   = build_stat_row(RIG42_ASSETS,     None,       start_y=43, start_id=120)

    # ── Step 3: Insert new panels into panel list ─────────────────────────────
    # Insert after the Pad Alpha row panel (id=2)
    # Insert after the Pad Bravo row panel (id=3)
    # Insert after the Rig 42 row panel (id=4)
    # Simplest: just append and sort by y then x
    panels.extend(esp_stats)
    panels.extend(glift_stats)
    panels.extend(rig_stats)
    # Sort by y asc, then x asc, row panels first
    panels.sort(key=lambda p: (p.get("gridPos", {}).get("y", 0),
                                p.get("type") != "row",
                                p.get("gridPos", {}).get("x", 0)))

    print("\n=== After patch ===")
    for p in panels:
        print(f"  id={p['id']:3d}  y={p.get('gridPos',{}).get('y','?'):3}  title={p.get('title','')[:50]}")

    dashboard["panels"] = panels
    # Re-indent at 4 spaces (the YAML indents the JSON by 4 spaces inside the ConfigMap)
    new_json = json.dumps(dashboard, indent=2)
    # Indent every line by `indent` spaces for YAML embedding
    re_indented = '\n'.join(' ' * indent + line if line.strip() else line
                            for line in new_json.split('\n'))

    # Rebuild the YAML: replace the old JSON block with the new one
    old_block = match.group(0)  # includes the key line
    # Rebuild: key line + indented JSON
    new_block = 'gdc-pm-dashboard.json: |\n' + re_indented
    new_raw = raw[:match.start()] + new_block + raw[match.end():]

    CONFIGMAP_PATH.write_text(new_raw)
    print(f"\n✅ Wrote patched ConfigMap → {CONFIGMAP_PATH}")
    print(f"   Added {len(esp_stats)} ESP stat panels (IDs 100-105)")
    print(f"   Added {len(glift_stats)} GLIFT stat panels (IDs 110-113)")
    print(f"   Added {len(rig_stats)} Rig stat panels (IDs 120-123)")
    print(f"   Total panels: {len(panels)}")


if __name__ == "__main__":
    main()
