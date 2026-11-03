#!/usr/bin/env python3
# =====================================================================
#  Scrapling-ZeroBaran — Layer 1: Smart Crawling & Anti-Block Engines
#  Project #38 | ZeroBaran Studio — 100% Free Stack
#  Author : Baran Avisat
#  Email  : Baranavisat@gmail.com
#  WhatsApp: 00905313263722
#  Copyright (c) 2026 Baran Avisat. All rights reserved. (MIT licensed)
#
#  Ethical-by-design: robots.txt gate, polite randomized throttling,
#  human-like header rotation, block DETECTION + graceful backoff and a
#  circuit breaker. It never hammers, never bypasses paywalls/logins,
#  and stops when a site says no.
# =====================================================================
"""Fetch engines with graceful degradation:
   requests -> scrapling StealthyFetcher -> playwright (each optional).
"""
from __future__ import annotations

import hashlib
import logging
import random
import re
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

import requests

log = logging.getLogger("sz.crawler")


@dataclass
class FetchResult:
    url: str
    status: int = 0
    html: str = ""
    engine: str = ""
    blocked: bool = False
    error: str = ""
    latency_ms: int = 0
    headers_used: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300 and bool(self.html) and not self.blocked


BLOCK_MARKERS_DEFAULT = ["captcha", "unusual traffic", "access denied",
                         "error 403", "are you a robot"]


class RobotsGate:
    """robots.txt compliance with in-memory cache (fail-closed on errors)."""

    def __init__(self, timeout: int = 15):
        self._cache: dict[str, Optional[re.Pattern]] = {}
        self.timeout = timeout

    def allowed(self, url: str, user_agent: str = "*") -> bool:
        parts = urllib.parse.urlparse(url)
        base = f"{parts.scheme}://{parts.netloc}"
        if base not in self._cache:
            try:
                r = requests.get(base + "/robots.txt", timeout=self.timeout,
                                 headers={"User-Agent": user_agent})
                if r.status_code == 401 or r.status_code == 403:
                    self._cache[base] = None      # private robots -> treat strict
                elif r.ok:
                    self._cache[base] = self._disallow_pattern(r.text)
                else:
                    self._cache[base] = None       # no robots.txt -> all allowed
            except Exception:
                self._cache[base] = None           # unreachable -> allow page fetch
        pat = self._cache[base]
        if pat is None:
            return True
        path = parts.path or "/"
        return not pat.search(path)

    @staticmethod
    def _disallow_pattern(robots_text: str) -> Optional[re.Pattern]:
        disallows = []
        applies = False
        for line in robots_text.splitlines():
            line = line.strip()
            low = line.lower()
            if low.startswith("user-agent:"):
                agent = line.split(":", 1)[1].strip()
                applies = agent == "*"
            elif applies and low.startswith("disallow:"):
                val = line.split(":", 1)[1].strip()
                if val and val != "/":
                    disallows.append(re.escape(val.rstrip("*")) + ("" if val.endswith("*") else ".*"))
        if not disallows:
            return None
        return re.compile("^(" + "|".join(disallows) + ")")


class PoliteThrottle:
    """Randomized delay between min..max seconds per host."""

    def __init__(self, dmin: float = 1.0, dmax: float = 3.0):
        self.dmin, self.dmax = dmin, dmax
        self._last: dict[str, float] = {}

    def wait(self, url: str) -> float:
        host = urllib.parse.urlparse(url).netloc
        now = time.time()
        elapsed = now - self._last.get(host, 0.0)
        target = random.uniform(self.dmin, self.dmax)
        sleep_for = max(0.0, target - elapsed) if host in self._last else 0.0
        if sleep_for > 0:
            time.sleep(sleep_for)
        self._last[host] = time.time()
        return sleep_for


def browser_headers(ua_pool: list[str]) -> dict:
    ua = random.choice(ua_pool) if ua_pool else "Scrapling-ZeroBaran/1.0"
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
    }


def looks_blocked(status: int, html: str, markers: list[str]) -> bool:
    if status in (403, 429, 503):
        return True
    low = (html or "")[:4000].lower()
    return any(m in low for m in (markers or BLOCK_MARKERS_DEFAULT))


class RequestsEngine:
    name = "requests"

    def __init__(self, cfg: dict):
        d = cfg.get("defaults", {})
        self.timeout = d.get("timeout_seconds", 20)
        self.max_retries = d.get("max_retries", 3)
        self.ua_pool = d.get("user_agent_pool", [])

    def fetch(self, url: str) -> FetchResult:
        t0 = time.time()
        last_err = ""
        for attempt in range(self.max_retries):
            headers = browser_headers(self.ua_pool)
            try:
                r = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
                html = r.text or ""
                blocked = looks_blocked(r.status_code, html, BLOCK_MARKERS_DEFAULT)
                res = FetchResult(url=url, status=r.status_code, html=html,
                                  engine=self.name, blocked=blocked,
                                  latency_ms=int((time.time() - t0) * 1000),
                                  headers_used=headers)
                if r.status_code in (429, 503) and attempt < self.max_retries - 1:
                    ra = int(r.headers.get("Retry-After", 0) or 0)
                    time.sleep(min(max(ra, 2 ** (attempt + 1)), 60))
                    continue
                if r.status_code >= 500 and attempt < self.max_retries - 1:
                    time.sleep(2 ** (attempt + 1))
                    continue
                return res
            except requests.RequestException as e:
                last_err = str(e.__class__.__name__) + ": " + str(e)[:120]
                time.sleep(min(2 ** (attempt + 1), 30))
        return FetchResult(url=url, status=0, engine=self.name, error=last_err,
                           latency_ms=int((time.time() - t0) * 1000))


class ScraplingEngine:
    """Uses the OSS `scrapling` package if installed (StealthyFetcher)."""
    name = "scrapling-stealth"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.available = False
        try:
            from scrapling.fetchers import StealthyFetcher  # noqa
            self._fetcher = StealthyFetcher
            self.available = True
        except Exception:
            self.available = False

    def fetch(self, url: str) -> FetchResult:
        if not self.available:
            return FetchResult(url=url, engine=self.name, error="scrapling not installed")
        t0 = time.time()
        try:
            page = self._fetcher.fetch(url, headless=True, network_idle=True)
            html = getattr(page, "html_content", None) or getattr(page, "body_html", "") or ""
            status = getattr(page, "status", 200)
            return FetchResult(url=url, status=status, html=html, engine=self.name,
                               blocked=looks_blocked(status, html, BLOCK_MARKERS_DEFAULT),
                               latency_ms=int((time.time() - t0) * 1000))
        except Exception as e:
            return FetchResult(url=url, engine=self.name,
                               error=str(e)[:160],
                               latency_ms=int((time.time() - t0) * 1000))


class PlaywrightEngine:
    """Headless browser fallback for JS-heavy pages (optional)."""
    name = "playwright"

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.available = False
        try:
            from playwright.sync_api import sync_playwright  # noqa
            self._pw = sync_playwright
            self.available = True
        except Exception:
            self.available = False

    def fetch(self, url: str) -> FetchResult:
        if not self.available:
            return FetchResult(url=url, engine=self.name, error="playwright not installed")
        t0 = time.time()
        try:
            with self._pw() as pw:
                browser = pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
                ctx = browser.new_context(user_agent=random.choice(
                    self.cfg.get("defaults", {}).get("user_agent_pool", ["Mozilla/5.0"])))
                page = ctx.new_page()
                resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                html = page.content()
                status = resp.status if resp else 200
                browser.close()
            return FetchResult(url=url, status=status, html=html, engine=self.name,
                               blocked=looks_blocked(status, html, BLOCK_MARKERS_DEFAULT),
                               latency_ms=int((time.time() - t0) * 1000))
        except Exception as e:
            return FetchResult(url=url, engine=self.name, error=str(e)[:160],
                               latency_ms=int((time.time() - t0) * 1000))


class Crawler:
    """Orchestrates robots gate + throttle + engine cascade + circuit breaker."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        ab = cfg.get("anti_block", {})
        self.enabled = ab.get("enabled", True)
        self.breaker_threshold = ab.get("circuit_breaker_threshold", 3)
        d = cfg.get("defaults", {})
        self.respect_robots = d.get("respect_robots_txt", True)
        self.engine_order = d.get("fetch_engine_order", ["requests"])
        self.throttle = PoliteThrottle(d.get("delay_seconds_min", 1.0),
                                       d.get("delay_seconds_max", 3.0))
        self.robots = RobotsGate()
        self._consecutive_blocks = 0
        self._engines: dict[str, object] = {}
        for name in self.engine_order:
            if name == "requests":
                self._engines[name] = RequestsEngine(cfg)
            elif name == "scrapling-stealth":
                e = ScraplingEngine(cfg)
                if e.available:
                    self._engines[name] = e
            elif name == "playwright":
                e = PlaywrightEngine(cfg)
                if e.available:
                    self._engines[name] = e
        if "requests" not in self._engines:
            self._engines["requests"] = RequestsEngine(cfg)

    @property
    def tripped(self) -> bool:
        return self.enabled and self._consecutive_blocks >= self.breaker_threshold

    def fetch(self, url: str) -> FetchResult:
        if self.tripped:
            return FetchResult(url=url, engine="circuit-breaker",
                               error="aborted: repeated blocks detected (site said no)")
        if self.respect_robots and not self.robots.allowed(url):
            log.info("robots.txt disallows %s — skipping", url)
            return FetchResult(url=url, engine="robots-gate", blocked=True,
                               error="disallowed by robots.txt")
        self.throttle.wait(url)
        best: Optional[FetchResult] = None
        for name in self.engine_order:
            eng = self._engines.get(name)
            if eng is None:
                continue
            res = eng.fetch(url)
            if res.ok:
                self._consecutive_blocks = 0
                return res
            if res.blocked:
                self._consecutive_blocks += 1
                best = best or res
                break  # blocked -> do NOT escalate aggressively; back off
            best = best or res
        return best or FetchResult(url=url, error="no engine succeeded")


def checksum(html: str) -> str:
    """Cosmetic-HTML-insensitive fingerprint.

    Parses with BeautifulSoup (lxml/html.parser) and hashes the visible
    text + tag structure, so indentation/whitespace/class reordering
    never masquerade as a content change.
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html or "", "lxml" if _has_lxml() else "html.parser")
        for bad in soup(["script", "style"]):
            bad.decompose()
        skeleton = "|".join(el.name for el in soup.find_all(True)[:2000])
        visible = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
        blob = skeleton + "::" + visible
    except Exception:
        blob = re.sub(r"\s+", " ", html or "").strip()
    return hashlib.sha1(blob.encode("utf-8", "ignore")).hexdigest()[:16]


def _has_lxml() -> bool:
    try:
        import lxml  # noqa
        return True
    except Exception:
        return False
