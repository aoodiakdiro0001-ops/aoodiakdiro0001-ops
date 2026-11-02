#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-Zero :: Ingestion Layer (طبقة الجلب والمسح الرقمي)
========================================================
يجمع آراء العملاء الخام من مصادر مجانية متعددة ويوحّدها في كائنات Mention:

  1. RSS/Atom feeds       — متاجر/Reddit/مدونات توفر Feed  (feedparser)
  2. Google News RSS      — رصد المقالات والمنشورات العامة  (RSS مجاني بلا مفتاح)
  3. HTML scraping        — صفحات تقييمات عامة مسموحة       (BeautifulSoup)
  4. Demo mode            — بيانات تجريبية لاختبار الأنبوب دون إنترنت

كل مصدر يفشل => يسجّل الخطأ ويستمر النظام (لا ينهار أبداً).
يعمل داخل GitHub Actions على خادم مجاني مجدول.
"""

from __future__ import annotations

import hashlib
import html as htmllib
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Iterable, Optional

try:
    import urllib.parse
    import urllib.request

    def http_get(url: str, timeout: int = 20) -> bytes:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "PulseZero/1.0 (+reputation monitor; contact: baranavisat@gmail.com)",
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/html;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
except Exception:  # pragma: no cover
    http_get = None  # type: ignore

# مكتبات اختيارية — إن وُجدت تُستخدم، وإلا نعود لبدائل قياسية
try:
    import feedparser  # type: ignore
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

try:
    from bs4 import BeautifulSoup  # type: ignore
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


@dataclass
class Mention:
    """وحدّة البيانات الأساسية: رأي عميل واحد خام."""
    id: str                    # بصمة ثابتة لمنع التكرار النهائي
    source: str                # rss | google_news | html | demo
    source_name: str
    title: str
    body: str
    url: str
    author: str
    published: str             # ISO-8601 UTC
    lang_hint: str = "auto"
    meta: dict = field(default_factory=dict)

    @staticmethod
    def make_id(source: str, url: str, body: str) -> str:
        raw = f"{source}|{url}|{body[:400]}".encode("utf-8", "ignore")
        return hashlib.sha1(raw).hexdigest()[:16]


def _strip_tags(text: str) -> str:
    if HAS_BS4:
        return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"<[^>]+>", " ", text or "")
    return htmllib.unescape(re.sub(r"\s+", " ", text)).strip()


def _clean(s: Optional[str]) -> str:
    return (s or "").strip()


# ---------------------------------------------------------------- RSS parsing
def _parse_feed_stdlib(raw: bytes) -> list[dict]:
    """محلل RSS/Atom قياسي بلا اعتماديات — fallback إذا غاب feedparser."""
    items: list[dict] = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return items

    ns_atom = "{http://www.w3.org/2005/Atom}"

    # Atom
    for e in root.iter(f"{ns_atom}entry"):
        title = e.findtext(f"{ns_atom}title", "")
        link_el = e.find(f"{ns_atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        summary = e.findtext(f"{ns_atom}summary", "") or e.findtext(f"{ns_atom}content", "")
        published = e.findtext(f"{ns_atom}published", "") or e.findtext(f"{ns_atom}updated", "")
        author = (e.findtext(f"{ns_atom}author/{ns_atom}name", "") or "").strip()
        items.append({"title": title, "link": link, "summary": summary,
                      "published": published, "author": author})

    if items:
        return items

    # RSS 2.0
    for item in root.iter("item"):
        items.append({
            "title": item.findtext("title", ""),
            "link": item.findtext("link", ""),
            "summary": item.findtext("description", ""),
            "published": item.findtext(f"pubDate", "") or item.findtext(
                "{http://purl.org/dc/elements/1.1/}date", ""),
            "author": item.findtext("{http://purl.org/dc/elements/1.1/}creator", "")
                      or item.findtext("author", ""),
        })
    return items


def _to_iso(dt_str: str) -> str:
    try:
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
            try:
                d = datetime.strptime(dt_str.strip(), fmt)
                return d.astimezone(timezone.utc).isoformat()
            except ValueError:
                continue
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()


def fetch_rss_feeds(feeds: Iterable[dict]) -> tuple[list[Mention], list[str]]:
    mentions: list[Mention] = []
    errors: list[str] = []
    for feed_cfg in feeds:
        name, url = _clean(feed_cfg.get("name", "feed")), _clean(feed_cfg.get("url", ""))
        if not url:
            continue
        try:
            raw = http_get(url) if http_get else b""
            entries = []
            if HAS_FEEDPARSER:
                parsed = feedparser.parse(raw)
                entries = [
                    {"title": e.get("title", ""), "link": e.get("link", ""),
                     "summary": e.get("summary", "") or e.get("description", ""),
                     "published": e.get("published", ""),
                     "author": e.get("author", "")}
                    for e in parsed.entries
                ]
            if not entries:
                entries = _parse_feed_stdlib(raw)

            for e in entries:
                body = _strip_tags(e.get("summary", ""))
                title = _strip_tags(e.get("title", ""))
                if not (body or title):
                    continue
                mid = Mention.make_id("rss", e.get("link", url), body or title)
                mentions.append(Mention(
                    id=mid, source="rss", source_name=name,
                    title=title[:300], body=(body or title)[:2000],
                    url=_clean(e.get("link", "")), author=_clean(e.get("author", "")) or "unknown",
                    published=_to_iso(_clean(e.get("published", ""))),
                ))
        except Exception as exc:
            errors.append(f"[rss:{name}] {type(exc).__name__}: {exc}")
    return mentions, errors


# ------------------------------------------------------------ Google News RSS
def fetch_google_news(query: str, limit: int = 30) -> tuple[list[Mention], list[str]]:
    url = ("https://news.google.com/rss/search?"
           f"q={urllib.parse.quote(query)}&hl=ar&gl=AR&ceid=AR:ar") if http_get else ""
    try:
        raw = http_get(url)
        entries = _parse_feed_stdlib(raw)
        mentions, errors = [], []
        for e in entries[:limit]:
            title = _strip_tags(e.get("title", ""))
            body = _strip_tags(e.get("summary", "")) or title
            mid = Mention.make_id("google_news", e.get("link", ""), title)
            mentions.append(Mention(
                id=mid, source="google_news", source_name="Google News",
                title=title[:300], body=body[:2000], url=_clean(e.get("link", "")),
                author=_clean(e.get("author", "")) or "press",
                published=_to_iso(_clean(e.get("published", ""))),
            ))
        return mentions, errors
    except Exception as exc:
        return [], [f"[google_news] {type(exc).__name__}: {exc}"]


# ------------------------------------------------------------- HTML scraping
def fetch_html_pages(pages: Iterable[dict]) -> tuple[list[Mention], list[str]]:
    """مسح صفحات تقييمات عامة عبر CSS selectors من config.yaml (يتطلب bs4)."""
    if not HAS_BS4:
        return [], ["[html] BeautifulSoup غير مثبتة — تم تخطي طبقة HTML"]
    mentions, errors = [], []
    for page in pages:
        url = _clean(page.get("url", ""))
        sel = page.get("selectors", {})
        if not url:
            continue
        try:
            soup = BeautifulSoup(http_get(url), "html.parser")
            for node in soup.select(sel.get("item", "div.review")):
                t = node.select_one(sel.get("title", "h3"))
                b = node.select_one(sel.get("body", "p"))
                r = node.select_one(sel.get("rating", "[data-rating]"))
                body = _clean(b.get_text(" ", strip=True)) if b else ""
                title = _clean(t.get_text(" ", strip=True)) if t else ""
                if not (body or title):
                    continue
                rating = r.get("data-rating") if r is not None and r.has_attr("data-rating") else None
                mid = Mention.make_id("html", url, body or title)
                mentions.append(Mention(
                    id=mid, source="html", source_name=page.get("name", url[:60]),
                    title=title[:300], body=(body or title)[:2000], url=url,
                    author="customer", published=datetime.now(timezone.utc).isoformat(),
                    meta={"rating": rating} if rating else {},
                ))
        except Exception as exc:
            errors.append(f"[html:{url[:60]}] {type(exc).__name__}: {exc}")
    return mentions, errors


# ------------------------------------------------------------------ Demo mode
_DEMO_POOL = [
    ("تجربة المنتج", "المنتج رائع وسهل الاستخدام، وفّر عليّ ساعات من العمل اليومي!", "en?no", "★★★★★"),
    ("شكوى توصيل", "المنتج وصل تالفاً ولم يعمل معي، أريد استرجاع المبلغ فوراً.", "ar", "★"),
    ("سؤال تقني", "هل يدعم المشروع ربط Telegram Bot؟ أحتاج تنبيهات فورية لفريقي.", "ar", None),
    ("مديح", "Best free reputation tool I have used this year. Saved us hundreds of dollars!", "en", "★★★★★"),
    ("نقد بناء", "التصميم جميل لكن لوحة التحكم بطيئة قليلاً على الجوال.", "ar", "★★★"),
    ("غضب عارم", "عمليتي لم تصل ولا يوجد رد من الدعم منذ ثلاثة أيام!! هذا احتيال", "ar", "★"),
    ("محايد", "جربت النسخة التجريبية، لا أستطيع الحكم بعد.", "ar", "★★★"),
]


def demo_mentions() -> list[Mention]:
    now = datetime.now(timezone.utc)
    out = []
    for i, (title, body, lang, stars) in enumerate(_DEMO_POOL):
        out.append(Mention(
            id=Mention.make_id("demo", f"demo://{i}", body),
            source="demo", source_name="Demo Sandbox",
            title=title, body=body, url=f"https://example.com/demo/{i}",
            author=f"user_{i:02d}", published=now.isoformat(), lang_hint=lang,
            meta={"stars": stars},
        ))
    return out


# ------------------------------------------------------------------ Public API
def collect_all(cfg: dict) -> tuple[list[Mention], list[str]]:
    """النقطة الوحيدة للدخول: يعيد كل Mentions + قائمة أخطاء المصادر."""
    src = cfg.get("sources", {})
    all_mentions: list[Mention] = []
    all_errors: list[str] = []

    if src.get("demo"):
        all_mentions.extend(demo_mentions())

    rss_cfg = src.get("rss") or []
    if rss_cfg:
        m, e = fetch_rss_feeds(rss_cfg)
        all_mentions += m
        all_errors += e

    gn = src.get("google_news") or {}
    if gn.get("enabled") and gn.get("query"):
        m, e = fetch_google_news(gn["query"], int(gn.get("limit", 30)))
        all_mentions += m
        all_errors += e

    h = src.get("html") or {}
    if h.get("enabled"):
        m, e = fetch_html_pages([{"name": p.get("name", "page"), **h, **p}
                                 for p in (h.get("pages") or [])] or [h])
        all_mentions += m
        all_errors += e

    # إزالة التكرار داخل نفس الدفعة (بصمة ID واحدة = نسخة واحدة)
    seen: set[str] = set()
    unique = []
    for mm in all_mentions:
        if mm.id not in seen:
            seen.add(mm.id)
            unique.append(mm)

    return unique, all_errors


if __name__ == "__main__":
    import json
    import sys
    try:
        import yaml
        cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "config.yaml")))
    except Exception:
        cfg = {"sources": {"demo": True}}
    ms, errs = collect_all(cfg)
    print(json.dumps([asdict(m) for m in ms], ensure_ascii=False, indent=2))
    for err in errs:
        print("WARN:", err, file=sys.stderr)
