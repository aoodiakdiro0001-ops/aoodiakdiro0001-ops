#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-Skill-ZeroBaran — Orchestrator (CI/CD security gate + CLI)
================================================================
Project #35 | Baran Avisat | ZeroBaran Studio
Baranavisat@gmail.com | WhatsApp 00905313263722 | MIT (c) 2026

Pipeline: scan -> AI enrich -> persist -> notify. Exit codes make it a real
deploy gate for GitHub Actions / any CI:
   0 = APPROVED / APPROVED_WITH_WARNINGS
   2 = REJECTED
   3 = BLOCKED (critical vulnerability found -> stop the deploy)

Commands:
  audit.py scan <path> [--tag NAME] [--no-notify] [--fail-on critical|high|never]
  audit.py demo            # audits bundled vulnerable examples, end-to-end
  audit.py stats           # posture summary from local/Supabase archive
  audit.py fix <fingerprint>  # mark finding fixed after developer patches it
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from scanners import scan                      # noqa: E402
from audit_brain import enrich_report          # noqa: E402
from store import Store                        # noqa: E402
from notify import Notifier                    # noqa: E402

__author__ = "Baran Avisat"

EXIT_BY_VERDICT = {"APPROVED": 0, "APPROVED_WITH_WARNINGS": 0, "REJECTED": 2, "BLOCKED": 3}


def run_scan(target: str, tag: str = "default", notify: bool = True,
             fail_on: str = "critical") -> int:
    report = scan(target)
    report = enrich_report(report)
    store = Store()
    saved = store.save_report(report, project_tag=tag)
    if notify:
        Notifier().scan_report(report)
    crit = report["counts_by_severity"].get("CRITICAL", 0)
    high = report["counts_by_severity"].get("HIGH", 0)
    print(json.dumps({
        "scan_id": report["scan_id"], "verdict": report["verdict"],
        "security_score": report["security_score"], "files": report["files_scanned"],
        "findings": report["findings_total"], "critical": crit, "high": high,
        "engines": report["engines"], "ai_brains": report.get("ai_brains_used"),
        "storage": saved,
    }, ensure_ascii=False, indent=2))
    if fail_on == "never":
        return 0
    if fail_on == "critical" and crit:
        return EXIT_BY_VERDICT["BLOCKED"]
    if fail_on == "high" and (crit or high):
        return EXIT_BY_VERDICT["BLOCKED"] if crit else EXIT_BY_VERDICT["REJECTED"]
    return EXIT_BY_VERDICT[report["verdict"]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Audit-Skill-ZeroBaran orchestrator")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan")
    s.add_argument("target")
    s.add_argument("--tag", default="default")
    s.add_argument("--no-notify", action="store_true")
    s.add_argument("--fail-on", choices=["critical", "high", "never"], default="critical")

    d = sub.add_parser("demo")
    d.add_argument("--no-notify", action="store_true")

    sub.add_parser("stats")

    f = sub.add_parser("fix")
    f.add_argument("fingerprint")

    w = sub.add_parser("weekly")

    args = ap.parse_args(argv)

    if args.cmd == "scan":
        return run_scan(args.target, args.tag, not args.no_notify, args.fail_on)
    if args.cmd == "demo":
        ex = HERE.parent / "examples" / "vulnerable_repo"
        print(f"🧪 demo: auditing intentionally-vulnerable sample repo at {ex}")
        return run_scan(str(ex), tag="demo", notify=not args.no_notify, fail_on="never")
    if args.cmd == "stats":
        st = Store().stats()
        print(json.dumps(st, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "fix":
        ok = Store().mark_fixed(args.fingerprint)
        print(json.dumps({"marked_fixed": ok, "fingerprint": args.fingerprint}))
        return 0 if ok else 1
    if args.cmd == "weekly":
        store = Store()
        res = Notifier().weekly_digest(store.stats(), store.trend())
        print(json.dumps(res, ensure_ascii=False))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
