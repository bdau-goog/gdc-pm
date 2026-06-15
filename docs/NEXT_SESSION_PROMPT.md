# Next Session Prompt — GDC Edge AI Demo (Operational State)
Session BS+1 wrap — June 15, 2026 / git head: `4db6223` / image: `sha256:bb501fded1f125db7708e976e29e4dacc11cd6c4fd3cd526ef53bca3b9043ed8` / branch: `feature-trio-clean`

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'))" 2>/dev/null || echo "API offline"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

## STEP 3: CRITICAL — Blank Page Bug NOT YET RESOLVED

### What is known:
- The self-hosting commit (3a74460) broke the app
- **HTML div balance is confirmed 0** (server-side verified) — `<script src="/static/app.js">` IS outside `#app`
- **Vue 3.5.38** is now being served (was 3.4.38)
- **Server-side is correct** — all files serve 200, div balance good
- **Page still shows dark blue** (v-cloak still active = Vue not mounting)

### What was NOT tried yet:
1. **Verify app.js actually loads in browser** — Network tab in last attempt did NOT show app.js loading. With div fix deployed, does it now appear? This is the first check in next session.
2. **Check if v-cloak is still on #app** in Elements panel after hard refresh
3. **Add a non-Vue visible element** outside #app (like `<p style="color:white">LOADED</p>`) to confirm HTML is rendering
4. **Roll back to pre-self-hosting (commit 757916f)** using CDN URLs as a known-good baseline to confirm infrastructure is working
5. **Check if the issue is specific to Chrome** — try a different browser

### Fastest unblock path for next session:
```bash
# Roll back to last known working commit for a quick confirm:
git show 757916f:gke/fault-trigger-ui/index.html | grep "cdn.plot.ly\|unpkg.com"
# If CDN version works: the issue is with static file serving, not HTML structure
# If CDN version also blank: the issue is infrastructure (pod, ingress, etc.)
```

### Known integrity issues:
| Item | Issue | Status |
|------|-------|--------|
| blank page | Vue not mounting despite correct HTML div balance | OPEN |

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied (would destroy live cluster)
- No `browser_action` (SSH remote, no browser)
- Batch all edits to same file in ONE `replace_in_file` call
- `feature-trio-clean` branch — do NOT merge to main
- No GPU start without announcing cost (~$0.35/hr T4) and getting confirmation
- Deploy sequence: `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- Artifact Registry only — NOT gcr.io
- All Ollama API calls MUST include `"think": False` — do not omit this
