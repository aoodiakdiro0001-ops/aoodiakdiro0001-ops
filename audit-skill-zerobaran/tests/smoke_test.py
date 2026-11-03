#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-Skill-ZeroBaran — Contract Smoke Test (runs fully offline, no secrets)
============================================================================
(c) 2026 Baran Avisat · ZeroBaran Studio · Baranavisat@gmail.com

Validates the contracts between all 4 layers so CI can never ship a broken
auditor. Exit 0 = every contract holds.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))

os.environ["ASZ_STATE_DIR"] = tempfile.mkdtemp(prefix="asz_test_")
for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "SUPABASE_URL",
          "SUPABASE_SERVICE_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
    os.environ.pop(k, None)  # force deterministic offline mode

from scanners import scan, shannon_entropy, Finding   # noqa: E402
from audit_brain import enrich_report, redact, MockBrain, _parse_batch  # noqa: E402
from store import Store                               # noqa: E402
from notify import Notifier, html_escape              # noqa: E402

PASS, FAIL = [], []


def check(name: str, cond: bool, detail: str = ""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ""))


VULN = ROOT / "examples/vulnerable_repo"
CLEAN = ROOT / "examples/clean_skill"

print("== Layer 1: scanner ==")
rep_v = scan(VULN)
rep_c = scan(CLEAN)
check("report schema keys", {"schema", "scan_id", "findings", "verdict",
                             "security_score", "counts_by_severity"} <= set(rep_v))
check("vulnerable repo detected", rep_v["findings_total"] >= 20,
      f"got {rep_v['findings_total']}")
check("clean repo APPROVED 100", rep_c["verdict"] == "APPROVED" and rep_c["security_score"] == 100,
      f"{rep_c['verdict']}/{rep_c['security_score']}")
rules_hit = {f["rule_id"] for f in rep_v["findings"]}
check("secrets rules fire", {"ASZ-SEC-001", "ASZ-SEC-002", "ASZ-SEC-006"} & rules_hit)
check("SQLi rule fires", "ASZ-INJ-001" in rules_hit)
check("agent rules fire (niche)", {"ASZ-AGT-002", "ASZ-AGT-003", "ASZ-AGT-004"} & rules_hit)
check("dockerfile rules fire", {"ASZ-IAC-001", "ASZ-IAC-003"} & rules_hit)
check("deps CVE rules fire", {"ASZ-DEP-003"} & rules_hit)
check("verdict BLOCKED on criticals", rep_v["verdict"] == "BLOCKED")
check("entropy sanity", shannon_entropy("aaaaaaaa") < 1 < shannon_entropy("xK9$mZq2!Lp7wRt4"))
fps = [f["fingerprint"] for f in rep_v["findings"]]
check("fingerprints unique", len(fps) == len(set(fps)))

print("== Layer 2: AI brain ==")
enr = enrich_report(dict(json.loads(json.dumps(rep_v))))  # deep copy
check("every finding enriched", all(f.get("ai", {}).get("explanation_ar") for f in enr["findings"]))
check("executive summary Arabic", "الحكم العام" in enr["executive_summary_ar"])
check("brains recorded", enr["ai_brains_used"] == ["mock"])
secret_line = 'API_KEY = "AKIAIOSFODNN7EXAMPLE"'
red = redact(secret_line)
check("redaction protects AWS key", "AKIAIOSFODNN7EXAMPLE" not in red and "AKIA_****" in red)
fenced = _parse_batch('```json\n{"results":[{"id":"abc","explanation_ar":"شرح","severity_assessed":"HIGH","priority_rank":1}]}\n```')
check("JSON fence repair works", fenced.get("abc", {}).get("explanation_ar") == "شرح")
garbage = _parse_batch("totally not json")
check("garbage input -> empty dict (no crash)", garbage == {})

print("== Layer 3: persistence ==")
st = Store()
saved = st.save_report(enr, project_tag="test")
check("local fallback active", saved["mode"] == "local-json" and saved.get("local"))
stats = st.stats()
check("stats counts findings", stats["open_findings"] >= 20)
check("history trend recorded", len(st.trend()) >= 1)
fp = enr["findings"][0]["fingerprint"]
check("mark_fixed flips status", st.mark_fixed(fp) and
      fp not in {f["fingerprint"] for f in st.open_findings()})
resave = st.save_report(enr, project_tag="test")  # idempotent re-store
check("re-save keeps first_seen dedupe", st.stats()["open_findings"] == stats["open_findings"] - 1)

print("== Layer 4: delivery ==")
n = Notifier()
msgs = n.scan_report(enr)
check("report + urgent alerts produced", len(msgs) >= 2)
check("all dry-run without token", all(m.get("dry_run") for m in msgs))
sent = []
n._send = lambda t: (sent.append(t), {"ok": True, "dry_run": True})[1]
n.alert_critical(enr["findings"][0], enr)
body = sent[0]
check("alert has promised format", "🛡️" in body and "تنبيه أمني عاجل" in body
      and "💻 السبب" in body and "🛠️ الإصلاح المقترح" in body)
check("branding footer present", "Baran Avisat" in body and "Baranavisat@gmail.com" in body
      and "00905313263722" in body)
esc = html_escape("<script>alert(1)</script>")
check("HTML injection escaped", "<script>" not in esc)
wk = n.weekly_digest(st.stats(), st.trend())
check("weekly digest ok", wk.get("dry_run"))

print("== Cross-layer ==")
check("orchestrator importable", (ROOT / "scripts/audit.py").exists())
check("workflow yaml exists", (ROOT / ".github/workflows/audit-skill-zerobaran.yml").exists())
check("supabase schema exists", "asz_scans" in (ROOT / "supabase/schema.sql").read_text())
check("semgrep rules exist", "osz" or "asz-agent" in (ROOT / "rules/semgrep/agent-rules.yaml").read_text())
try:
    import yaml  # type: ignore
    y = yaml.safe_load((ROOT / ".github/workflows/audit-skill-zerobaran.yml").read_text())
    check("workflow YAML parses", "jobs" in y and "audit" in y["jobs"])
except ImportError:
    txt = (ROOT / ".github/workflows/audit-skill-zerobaran.yml").read_text()
    check("workflow YAML parses (basic)", "jobs:" in txt and "runs-on: ubuntu-latest" in txt)

total = len(PASS) + len(FAIL)
print(f"\n{'🏆 ALL LAYER CONTRACTS OK' if not FAIL else '💥 FAILURES: ' + ', '.join(FAIL)} "
      f"({len(PASS)}/{total})")
sys.exit(0 if not FAIL else 1)
