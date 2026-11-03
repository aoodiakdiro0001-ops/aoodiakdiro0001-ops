#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Layer 1b: Structural Extraction + Self-Healing
#  Project #38 | ZeroBaran Studio — 100% Free Stack
#  Author : Baran Avisat | Baranavisat@gmail.com | WhatsApp: 00905313263722
#  Copyright (c) 2026 Baran Avisat. All rights reserved. (MIT licensed)
#
#  Scrapling-style adaptive selectors, implemented natively in OSS Python:
#  when a CSS selector misses, the extractor re-anchors via structural
#  similarity scoring instead of returning nothing.
# =====================================================================
from __future__ import annotations

import hashlib
import json
import logging
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Optional

from bs4 import BeautifulSoup

log = logging.getLogger("sz.extract")


@dataclass
class ExtractReport:
    url: str
    records: list[dict] = field(default_factory=list)
    tables: list[list[dict]] = field(default_factory=list)
    page_text: str = ""
    links: list[str] = field(default_factory=list)
    healed_selectors: list[str] = field(default_factory=list)
    failed_selectors: list[str] = field(default_factory=list)
    dom_hash: str = ""

    @property
    def record_count(self) -> int:
        return len(self.records)


def make_soup(html: str) -> BeautifulSoup:
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def norm_text(el) -> str:
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


def fingerprint(el) -> str:
    """Structural fingerprint: tag + classes + text-shape signature."""
    cls = "".join(sorted(el.get("class", [])))
    shape = re.sub(r"[A-Za-z\u0600-\u06FF]+", "w", norm_text(el)[:40])
    shape = re.sub(r"\d+", "n", shape)
    shape = re.sub(r"\s+", "", shape)
    return f"{el.name}.{cls}#{shape}"


# ---------------- Self-healing selector ------------------------------
class AdaptiveSelector:
    """Try exact CSS; on miss, re-anchor by nearest structural sibling."""

    def __init__(self, soup: BeautifulSoup, cfg: dict):
        self.soup = soup
        self.enabled = cfg.get("adaptive_selectors", {}).get("enabled", True)
        self.reanchor = cfg.get("adaptive_selectors", {}).get("reanchor_on_failure", True)

    def select(self, css: str, root=None) -> tuple[list, bool]:
        root = root or self.soup
        found = root.select(css)
        if found:
            return found, False
        if not (self.enabled and self.reanchor):
            return [], False
        healed = self._reanchor(root, css)
        return healed, bool(healed)

    def _reanchor(self, root, css: str) -> list:
        parts = [p.strip() for p in re.split(r"[\s>]+", css) if p.strip()]
        if not parts:
            return []
        last = parts[-1]
        m = re.match(r"([a-zA-Z][\w-]*)\.([\w-]+)", last)
        if not m:
            return []
        tag, cls = m.group(1), m.group(2)
        cands = root.find_all(tag)
        scored = []
        for c in cands:
            score = 0.0
            if cls.split("-")[0] in "".join(c.get("class", [])):
                score += 0.6
            t = norm_text(c)
            if t and len(t) > 20:
                score += 0.2
            if c.parent and cls.split("-")[0] in "".join(c.parent.get("class", [])):
                score += 0.2
            if score >= 0.6:
                scored.append((score, c))
        scored.sort(key=lambda x: -x[0])
        return [c for _, c in scored[:50]]


# ---------------- Field / item extraction ----------------------------
def extract_field(el, spec: dict, ad: AdaptiveSelector) -> tuple[Any, bool]:
    css = spec.get("selector", "")
    attr = spec.get("attr")
    multiple = spec.get("multiple", False)
    join = spec.get("join", "|")
    found, healed = ad.select(css, root=el)
    if not found:
        return (None, True)
    values = []
    for f in found:
        v = f.get(attr) if attr else norm_text(f)
        if v:
            values.append(str(v).strip())
    if not values:
        return (None, True)
    return ((join.join(values) if multiple else values[0]), healed)


def extract_items(soup: BeautifulSoup, recipe: dict, cfg: dict, url: str) -> ExtractReport:
    rep = ExtractReport(url=url, dom_hash=dom_fingerprint(soup))
    ad = AdaptiveSelector(soup, cfg)
    fields = recipe.get("fields", {}) or {}
    item_css = recipe.get("item_selector")
    if item_css:
        items, healed = ad.select(item_css)
        if healed:
            rep.healed_selectors.append(item_css)
        for it in items:
            rec: dict[str, Any] = {"_source_url": url}
            any_value = False
            for fname, fspec in fields.items():
                val, fld_healed = extract_field(it, fspec, ad)
                if fld_healed:
                    rep.healed_selectors.append(f"{item_css} {fspec.get('selector')}")
                if val is None and not fld_healed:
                    rep.failed_selectors.append(fspec.get("selector", fname))
                if val is not None:
                    rec[fname] = val
                    any_value = True
            if any_value:
                rec["id"] = record_id(url, rec, cfg)
                rep.records.append(rec)
    # generic <table> harvesting even without a recipe
    for tbl in soup.find_all("table"):
        rows = parse_table(tbl)
        if rows:
            rep.tables.append(rows)
    explicit = recipe.get("table_selectors") or []
    for css in explicit:
        for tbl in soup.select(css):
            rows = parse_table(tbl)
            if rows:
                rep.tables.append(rows)
    rep.page_text = get_page_text(soup)
    rep.links = discover_links(soup, url)
    return rep


def parse_table(tbl) -> list[dict]:
    headers: list[str] = []
    hrow = tbl.find("tr")
    if hrow and hrow.find("th"):
        headers = [norm_text(th) or f"col{i}" for i, th in enumerate(hrow.find_all("th"))]
    rows_out = []
    body_rows = tbl.find_all("tr")
    start = 1 if headers else 0
    for tr in body_rows[start:]:
        cells = [norm_text(td) for td in tr.find_all(["td", "th"])]
        if not any(cells):
            continue
        if headers and len(headers) == len(cells):
            rows_out.append(dict(zip(headers, cells)))
        else:
            rows_out.append({f"col{i+1}": c for i, c in enumerate(cells)})
    return rows_out


def get_page_text(soup: BeautifulSoup) -> str:
    for bad in soup(["script", "style", "noscript", "template"]):
        bad.decompose()
    main = soup.find("main") or soup.find(id="content") or soup.body or soup
    txt = re.sub(r"\n{3,}", "\n\n", main.get_text("\n", strip=True))
    return txt[:20000]


def discover_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    out = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("javascript:", "mailto:", "#")):
            continue
        full = urllib.parse.urljoin(base_url, href)
        if urllib.parse.urlparse(full).netloc != urllib.parse.urlparse(base_url).netloc:
            continue  # stay on-site (sovereign crawl scope)
        if full not in seen:
            seen.add(full)
            out.append(full)
    return out


def dom_fingerprint(soup: BeautifulSoup) -> str:
    sig = "|".join(sorted({fingerprint(el) for el in soup.find_all(["div", "span", "li", "article"])[:400]}))
    return hashlib.sha1(sig.encode("utf-8", "ignore")).hexdigest()[:16]


def record_id(url: str, rec: dict, cfg: dict) -> str:
    keys = cfg.get("ai", {}).get("dedupe_key_fields", [])
    payload = {k: rec.get(k, "") for k in keys} if keys else {k: v for k, v in rec.items() if k != "_source_url"}
    blob = url + "::" + json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(blob.encode("utf-8", "ignore")).hexdigest()


def follow_pagination(soup: BeautifulSoup, base_url: str, selector: Optional[str]) -> list[str]:
    if not selector:
        return []
    urls = []
    for a in soup.select(selector):
        href = a.get("href")
        if href:
            urls.append(urllib.parse.urljoin(base_url, href))
    return urls
