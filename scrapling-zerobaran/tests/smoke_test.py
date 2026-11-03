#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Contract Smoke Test (CI self-check)
#  Project #38 | Author: Baran Avisat | WhatsApp: 00905313263722
#  Runs fully offline: no network, no keys. Validates all 4 layers.
# =====================================================================
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append((name, detail))
    print(f"{'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ""))


FIXTURE = """<html><body>
<div class="quote"><span class="text">“Patience is bitter but its fruit is sweet.”</span><small class="author">Aristotle</small><a class="tag" href="#">virtue</a></div>
<div class="quote"><span class="text">“Pro plan now $49 USD, was $79 USD — limited offer.”</span><small class="author">DealDesk</small><a class="tag" href="#">sale</a></div>
<table><tr><th>Item</th><th>Cost</th></tr><tr><td>Gadget</td><td>$12.00</td></tr></table>
<nav class="pager"><a href="/page/2/">Next →</a></nav>
</body></html>"""

CFG = {
    "defaults": {"user_agent_pool": ["UA-Test"], "max_retries": 1, "timeout_seconds": 5,
                 "respect_robots_txt": True, "fetch_engine_order": ["requests"]},
    "anti_block": {"enabled": True, "circuit_breaker_threshold": 3},
    "adaptive_selectors": {"enabled": True, "reanchor_on_failure": True},
    "ai": {"provider": "mock", "dedupe_key_fields": ["text", "author"], "max_items_per_call": 20,
           "structure_raw_text": True},
    "storage": {"local_state_dir": tempfile.mkdtemp(), "history_keep_per_key": 10},
    "alerts": {"send_run_report": True, "send_change_alerts": True},
}


def main() -> int:
    # ---- Layer 1: crawler safety rails (no network calls) ----
    from crawler import Crawler, looks_blocked, browser_headers, PoliteThrottle, checksum
    from crawler import RobotsGate
    c = Crawler(CFG)
    check("L1: engine cascade built", "requests" in c._engines)
    check("L1: breaker not tripped initially", not c.tripped)
    check("L1: block marker detection (429)", looks_blocked(429, "", []) is True)
    check("L1: captcha text detected", looks_blocked(200, "<h1>Enter Captcha to continue</h1>", []) is True)
    check("L1: clean page not flagged", looks_blocked(200, "<p>hello world</p>", []) is False)
    h = browser_headers(CFG["defaults"]["user_agent_pool"])
    check("L1: human-like headers", "User-Agent" in h and "Accept-Language" in h)
    # robots parser unit
    pat = RobotsGate._disallow_pattern("User-agent: *\nDisallow: /private/\nDisallow: /admin*")
    check("L1: robots disallow parsed", pat is not None and bool(pat.search("/private/x")) and not pat.search("/public"))
    check("L1: checksum stable", checksum("<a> x </a>") == checksum("<a>x</a>"))

    # ---- Layer 1b: extraction + adaptive selectors ----
    from extractor import extract_items, make_soup, follow_pagination, parse_table
    soup = make_soup(FIXTURE)
    recipe = {"item_selector": "div.quote",
              "fields": {"text": {"selector": "span.text"}, "author": {"selector": "small.author"},
                         "tags": {"selector": "a.tag", "multiple": True, "join": ","}}}
    rep = extract_items(soup, recipe, CFG, "https://demo.local/")
    check("L1b: recipe extracted 2 items", rep.record_count == 2, f"got {rep.record_count}")
    check("L1b: tags joined", rep.records[0].get("tags") == "virtue")
    check("L1b: ids deterministic", rep.records[0]["id"] == extract_items(make_soup(FIXTURE), recipe, CFG, "https://demo.local/").records[0]["id"])
    # self-healing: broken selector should re-anchor onto span.text elements
    broken = {"item_selector": "div.quote",
              "fields": {"text": {"selector": "span.typo-class-that-no-longer-exists"}}}
    rep2 = extract_items(make_soup("""<div class="quote"><span class="text">Long enough sentence to anchor healing here.</span></div>"""),
                         broken, CFG, "https://demo.local/")
    check("L1b: adaptive selector healed miss", len(rep2.healed_selectors) > 0 or rep2.records,
          "healing produced neither records nor heal log")
    tbl = parse_table(soup.find("table"))
    check("L1b: table -> dicts", tbl and tbl[0].get("Item") == "Gadget")
    pg = follow_pagination(soup, "https://demo.local/", "nav.pager a")
    check("L1b: pagination link resolved", pg == ["https://demo.local/page/2/"], str(pg))

    # ---- Layer 2: AI brain (mock offline) ----
    from parsing_brain import MockBrain, structure_records, structure_page_text, get_brain
    brain = get_brain(CFG)
    check("L2: auto provider falls back to mock offline", brain.name == "mock")
    enriched, bn = structure_records(brain, rep.records)
    check("L2: records enriched", len(enriched) == 2 and all("ai_category" in r for r in enriched))
    priced = [r for r in enriched if (r.get("ai_values") or {}).get("price")]
    check("L2: price normalized to float", priced and isinstance(priced[0]["ai_values"]["price"], float),
          json.dumps(priced[:1]))
    txt_recs, _ = structure_page_text(brain, "The premium widget costs $25 USD.\nBuy the deluxe pack €30 EUR today.", "https://x/")
    check("L2: raw text structured into records", len(txt_recs) >= 2)

    # ---- Layer 3: store + change detection ----
    from store import Store
    st = Store(CFG, BASE)
    known = st.count_known([r["id"] for r in enriched])
    ch1 = st.put_records(enriched, target="unittest")
    new_n = sum(1 for r in enriched if r["id"] not in known)
    check("L3: first store marks NEW (no changes yet)", new_n == len(enriched) and ch1 == {})
    mutated = [dict(r, ai_values={**(r.get("ai_values") or {}), "price": 1.11}) for r in enriched]
    ch2 = st.put_records(mutated, target="unittest")
    check("L3: price mutation -> CHANGED event", len(ch2) >= 1, str(ch2)[:120])
    ev = next(iter(ch2.values()), {})
    check("L3: alert title readable (not dict-dump)", ev.get("title", "").strip() and not ev.get("title", "").startswith("{"),
          ev.get("title", ""))
    st.log_run({"run_id": "t1", "ts": 1, "targets": ["unittest"], "pages_fetched": 1,
                "records_new": new_n, "records_changed": len(ch2), "blocks_detected": 0,
                "engines_used": {"requests": 1}, "status": "ok"})
    stats = st.stats()
    check("L3: stats aggregate", stats["total_records"] >= len(enriched) and stats["total_runs"] >= 1)

    # ---- Layer 4: notifier report format ----
    from notify import Notifier
    n = Notifier(CFG)
    report = n.crawl_report({"status": "ok", "engines_used": {"requests": 3}, "records_new": 145,
                             "records_changed": 2, "targets": ["a"], "pages_fetched": 5,
                             "blocks_detected": 0, "brain": "mock"})
    check("L4: report has 🕸️ headline + counts", "🕸️" in report and "145" in report)
    check("L4: report says 100% no-block", "اكتمل بنسبة 100% دون أي حظر" in report)
    check("L4: owner footer present", "Baran Avisat" in report and "00905313263722" in report)
    alert = n.change_alert({"field": "price", "old": 9.99, "new": 7.49, "title": "Widget"})
    check("L4: drop arrow on decrease", "🔻" in alert)

    # ---- Orchestrator end-to-end offline ----
    from scrape_run import process_target, DEMO_HTML
    tcfg = {"name": "e2e", "start_urls": ["https://demo.local/"], "max_pages": 1,
            "follow_links_selector": "nav.pager a", "extractors": recipe}
    res = process_target(CFG, tcfg, st, MockBrain(), Notifier(CFG), Crawler(CFG), offline_html=DEMO_HTML)
    check("E2E: pipeline returns ok with records", res["status"] == "ok" and res["records_extracted"] >= 4,
          json.dumps(res)[:200])

    # ---- Config & schema sanity ----
    import yaml
    cfg_text = (BASE / "scripts" / "config.yaml").read_text(encoding="utf-8")
    cfg = yaml.safe_load(cfg_text)
    check("CFG: valid YAML with targets", bool(cfg.get("targets")))
    check("CFG: compliance gate present", cfg.get("compliance", {}).get("enforce_tos_gate") is True)
    sql = (BASE / "supabase" / "schema.sql").read_text(encoding="utf-8")
    check("SQL: tables defined", "scraped_records" in sql and "crawl_runs" in sql)
    wf = Path("/workspace/.github/workflows/scrapling-zerobaran.yml")
    check("CI: workflow exists & parses", wf.exists() and bool(yaml.safe_load(wf.read_text()).get("jobs")))

    total = len(PASS) + len(FAIL)
    print(f"\n{'🏆 ALL LAYER CONTRACTS OK' if not FAIL else '💥 FAILURES: ' + str(len(FAIL))} ({len(PASS)}/{total})")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
