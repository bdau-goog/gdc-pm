# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Consolidation Complete)  
**git head:** `feature-trio-clean` (new branch, all cruft purged)  
**fault-trigger-ui image:** `sha256:df7f9433` (1/1 Running — Session G)  
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)  
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

Also check RabbitMQ:
```bash
source .env && kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Task

**Build the H1 V2 red-line UI components (Split SCADA/GDC Advisor Card + Surveillance Strip)**
1. **The Split SCADA vs GDC Card:** Replace the old bottom cards in `index.html` with the split layout detailing the SCADA Ambiguity (Gas Lock vs. Pump-Off risk) vs. the GDC L3 Certainty. Implement the `[APPROVE VFD TRIM]` HITL action button.
2. **The surveillance strip:** Add the horizontal multi-well surveillance strip below the main cards to show the scale factor (monitoring 14 assets simultaneously).

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
