#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${AUTOSKILL_OPENCLAW_VERIFY_BASE_URL:-http://127.0.0.1:9100}"
BASE_URL="${BASE_URL%/}"
API_BASE="${BASE_URL}/v1"
AUTH_HEADER=()

if [[ -n "${AUTOSKILL_PROXY_API_KEY:-}" ]]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${AUTOSKILL_PROXY_API_KEY}")
fi

echo "[verify-sidecar] base_url=${BASE_URL}"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

curl -sS "${BASE_URL}/health" "${AUTH_HEADER[@]}" >"${tmp_dir}/health.json"
python3 - "${tmp_dir}/health.json" <<'PY'
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
if str(obj.get("status", "")).lower() != "ok":
    raise SystemExit("health check failed")
print("[verify-sidecar] health=ok")
PY

curl -sS "${API_BASE}/autoskill/capabilities" "${AUTH_HEADER[@]}" >"${tmp_dir}/capabilities.json"
python3 - "${tmp_dir}/capabilities.json" <<'PY'
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
data = obj.get("data", {}) if isinstance(obj, dict) else {}
openclaw = data.get("openclaw", {}) if isinstance(data, dict) else {}
if not openclaw:
    raise SystemExit("missing openclaw capability")
print("[verify-sidecar] capabilities=openclaw-ok")
PY

uid="verify_user_$$"
sid_a="verify_session_a_$$"
sid_b="verify_session_b_$$"

cat >"${tmp_dir}/before_payload.json" <<JSON
{
  "user": "${uid}",
  "session_id": "${sid_a}",
  "scope": "user",
  "messages": [
    {"role": "user", "content": "Need a concise deployment checklist."}
  ]
}
JSON

curl -sS "${API_BASE}/autoskill/openclaw/hooks/before_agent_start" \
  "${AUTH_HEADER[@]}" \
  -H "Content-Type: application/json" \
  -d @"${tmp_dir}/before_payload.json" >"${tmp_dir}/before.json"

python3 - "${tmp_dir}/before.json" <<'PY'
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
if str(obj.get("object", "")) != "openclaw_hook_before_agent_start":
    raise SystemExit("before_agent_start response shape mismatch")
print("[verify-sidecar] before_agent_start=ok")
PY

cat >"${tmp_dir}/agent_end_a.json" <<JSON
{
  "user": "${uid}",
  "session_id": "${sid_a}",
  "turn_type": "main",
  "success": true,
  "messages": [
    {"role": "user", "content": "Need a concise deployment checklist."},
    {"role": "assistant", "content": "1) Run smoke test; 2) check rollback path."}
  ]
}
JSON

cat >"${tmp_dir}/agent_end_b.json" <<JSON
{
  "user": "${uid}",
  "session_id": "${sid_b}",
  "turn_type": "main",
  "success": true,
  "messages": [
    {"role": "user", "content": "Start another task."},
    {"role": "assistant", "content": "Acknowledged."}
  ]
}
JSON

curl -sS "${API_BASE}/autoskill/openclaw/hooks/agent_end" \
  "${AUTH_HEADER[@]}" \
  -H "Content-Type: application/json" \
  -d @"${tmp_dir}/agent_end_a.json" >"${tmp_dir}/agent_end_a.out.json"

curl -sS "${API_BASE}/autoskill/openclaw/hooks/agent_end" \
  "${AUTH_HEADER[@]}" \
  -H "Content-Type: application/json" \
  -d @"${tmp_dir}/agent_end_b.json" >"${tmp_dir}/agent_end_b.out.json"

python3 - "${tmp_dir}/agent_end_b.out.json" <<'PY'
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
extract = obj.get("extraction", {}) if isinstance(obj, dict) else {}
status = str(extract.get("status", "")).lower()
if status not in {"scheduled", "skipped"}:
    raise SystemExit(f"unexpected extraction status: {status}")
print(f"[verify-sidecar] agent_end extraction status={status}")
PY

curl -sS "${API_BASE}/autoskill/extractions/latest?user=${uid}" "${AUTH_HEADER[@]}" >"${tmp_dir}/latest_event.json"
python3 - "${tmp_dir}/latest_event.json" <<'PY'
import json, sys
obj = json.load(open(sys.argv[1], "r", encoding="utf-8"))
data = obj.get("data") if isinstance(obj, dict) else None
if not isinstance(data, dict):
    raise SystemExit("latest extraction event missing")
print("[verify-sidecar] latest extraction trigger=", data.get("trigger"))
print("[verify-sidecar] done")
PY
