#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Orchestrator (End-to-End Pipeline)
#  Project #38 | ZeroBaran Studio — 100% Free Stack
#  Author : Baran Avisat | Baranavisat@gmail.com | WhatsApp: 00905313263722
#  Copyright (c) 2026 Baran Avisat. All rights reserved. (MIT licensed)
#
#  Layer1 crawl+extract  ->  Layer2 AI structure  ->  Layer3 store+diff
#                        ->  Layer4 telegram report/alerts
#
#  Usage:
#    python scrape_run.py run            (all targets)
#    python scrape_run.py run --target quotes-demo
#    python scrape_run.py demo          (offline fixture HTML, zero network)
#    python scrape_run.py stats
#    python scrape_run.py export        (JSONL dump to exports/)
# =====================================================================
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urljoin

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

try:
    import yaml
except ImportError:  # minimal fallback loader for CI without pyyaml
    yaml = None

from crawler import Crawler, checksum
from extractor import extract_items, follow_pagination, make_soup
from parsing_brain import get_brain, structure_page_text, structure_records
from store import Store
from notify import Notifier

log = logging.getLogger("sz.run")


def load_config() -> dict:
    f = BASE_DIR / "config.yaml"
    text = f.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    # extremely small subset parser fallback (lists of scalars + nested maps)
    raise RuntimeError("PyYAML required for config; pip install pyyaml")


DEMO_HTML = """<html><body>
<div class="quote"><span class="text">“The world is moved not by those who say great things but those who do them.”</span><small class="author">Mock Author</small><a class="tag" href="#">wisdom</a><a class="tag" href="#">work</a></div>
<div class="quote"><span class="text">“Price of the premium plan is $29 USD while our license costs €120 EUR forever.”</span><small class="author">Finance Bot</small><a class="tag" href="#">pricing</a></div>
<table><tr><th>Product</th><th>Price</th></tr><tr><td>Widget A</td><td>$9.99</td></tr><tr><td>Widget B</td><td>$14.50</td></tr></table>
<nav class="pager"><a href="/page/2/">Next →</a></nav>
</body></html>"""


def process_target(cfg: dict, target: dict, store: Store, brain, notifier: Notifier,
                   crawler: Crawler, offline_html: str | None = None) -> dict:
    name = target["name"]
    recipe = target.get("extractors", {}) or {}
    max_pages = int(target.get("max_pages", 3))
    queue = list(target.get("start_urls", []))[:1]
    visited: set[str] = set()
    pages = 0
    blocks = 0
    engines_used: dict[str, int] = {}
    all_raw: list[dict] = []
    tables_all: list[list[dict]] = []
    healed: list[str] = []
    dom_hashes: dict[str, str] = {}

    while queue and pages < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        if offline_html is not None:
            from crawler import FetchResult
            res = FetchResult(url=url, status=200, html=offline_html, engine="demo")
        else:
            res = crawler.fetch(url)
        if not res.ok:
            if res.blocked:
                blocks += 1
                log.warning("[%s] blocked at %s (%s)", name, url, res.error or res.status)
            continue
        pages += 1
        engines_used[res.engine] = engines_used.get(res.engine, 0) + 1
        h = checksum(res.html)
        if dom_hashes.get(url) == h:
            log.info("[%s] page unchanged: %s", name, url)
        dom_hashes[url] = h
        soup = make_soup(res.html)
        rep = extract_items(soup, recipe, cfg, url)
        all_raw.extend(rep.records)
        tables_all.extend(rep.tables)
        healed.extend(rep.healed_selectors)
        # table rows become records too
        for tbl in rep.tables:
            for row in tbl:
                row = dict(row); row["_source_url"] = url
                row.setdefault("id", f"{url}::tbl::{list(row.values())[0][:40]}")
                all_raw.append(row)
        # full-text mode when no recipe produced anything
        if not rep.records and cfg.get("ai", {}).get("structure_raw_text", True):
            txt_recs, _ = structure_page_text(brain, rep.page_text, url,
                                              cfg.get("ai", {}).get("max_items_per_call", 20))
            all_raw.extend(txt_recs)
        # pagination
        if pages < max_pages:
            for nxt in follow_pagination(soup, url, target.get("follow_links_selector")):
                if nxt not in visited:
                    queue.append(nxt)
        if crawler.tripped:
            break

    # ---- Layer 2: AI structuring ----
    enriched, brain_name = structure_records(brain, all_raw,
                                             cfg.get("ai", {}).get("max_items_per_call", 20)) \
        if all_raw else ([], getattr(brain, "name", "mock"))

    # ---- Layer 3: store + change detection ----
    known_ids = store.count_known([r.get("id", "") for r in enriched])
    changes = store.put_records(enriched, target=name)
    new_count = sum(1 for r in enriched if r.get("id") not in known_ids)

    # ---- Layer 4: alerts ----
    a = cfg.get("alerts", {})
    if a.get("send_change_alerts", True):
        for ev in list(changes.values())[:10]:
            notifier.send(notifier.change_alert(ev))
    if crawler.tripped:
        notifier.send(notifier.breaker_alert(name, "توقف متسلسل بعد حواجز متعددة — سنعاود لاحقاً بأدب."))

    return {"target": name, "pages_fetched": pages, "blocks_detected": blocks,
            "engines_used": engines_used, "records_extracted": len(enriched),
            "records_new": new_count, "records_changed": len(changes),
            "tables_found": len(tables_all), "healed_selectors": sorted(set(healed)),
            "brain": brain_name, "status": "ok" if not crawler.tripped else "breaker-tripped"}


def cmd_run(args) -> int:
    cfg = load_config()
    store = Store(cfg, BASE_DIR)
    brain = get_brain(cfg)
    notifier = Notifier(cfg)
    crawler = Crawler(cfg)
    targets = cfg.get("targets", [])
    if args.target:
        targets = [t for t in targets if t["name"] == args.target]
    run_id = uuid.uuid4().hex[:12]
    started = int(time.time())
    results = []
    for t in targets:
        if t.get("tos_prohibited") and cfg.get("compliance", {}).get("enforce_tos_gate", True):
            log.warning("[%s] skipped: flagged tos_prohibited", t["name"])
            continue
        results.append(process_target(cfg, t, store, brain, notifier, crawler))
    agg = {
        "run_id": run_id, "ts": started,
        "targets": [r["target"] for r in results],
        "pages_fetched": sum(r["pages_fetched"] for r in results),
        "records_new": sum(r["records_new"] for r in results),
        "records_changed": sum(r["records_changed"] for r in results),
        "blocks_detected": sum(r["blocks_detected"] for r in results),
        "engines_used": {},
        "brain": results[0]["brain"] if results else "n/a",
        "status": "ok" if all(r["status"] == "ok" for r in results) else "partial",
        "duration_s": int(time.time()) - started,
        "per_target": results,
    }
    for r in results:
        for k, v in r["engines_used"].items():
            agg["engines_used"][k] = agg["engines_used"].get(k, 0) + v
    store.log_run(agg)
    msg = notifier.crawl_report(agg)
    if msg:
        notifier.send(msg)
    print(json.dumps(agg, ensure_ascii=False, indent=2))
    return 0


def cmd_demo(args) -> int:
    cfg = load_config()
    store = Store(cfg, BASE_DIR)
    brain = get_brain(cfg)
    notifier = Notifier(cfg)
    crawler = Crawler(cfg)
    fake_target = {"name": "demo-fixture", "start_urls": ["https://demo.local/page1"],
                   "max_pages": 1, "follow_links_selector": "nav.pager a",
                   "extractors": {"item_selector": "div.quote",
                                  "fields": {"text": {"selector": "span.text"},
                                             "author": {"selector": "small.author"},
                                             "tags": {"selector": "a.tag", "multiple": True, "join": ","}}}}
    res = process_target(cfg, fake_target, store, brain, notifier, crawler, offline_html=DEMO_HTML)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


def cmd_stats(args) -> int:
    cfg = load_config()
    print(json.dumps(Store(cfg, BASE_DIR).stats(), ensure_ascii=False, indent=2))
    return 0


def cmd_export(args) -> int:
    cfg = load_config()
    out = BASE_DIR.parent / "exports" / f"scraped-{int(time.time())}.jsonl"
    p = Store(cfg, BASE_DIR).export_jsonl(out)
    print(f"exported -> {p}")
    return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(prog="scrape_run", description="Scrapling-ZeroBaran orchestrator — © Baran Avisat")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--target", default=None); r.set_defaults(fn=cmd_run)
    d = sub.add_parser("demo"); d.set_defaults(fn=cmd_demo)
    s = sub.add_parser("stats"); s.set_defaults(fn=cmd_stats)
    e = sub.add_parser("export"); e.set_defaults(fn=cmd_export)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
