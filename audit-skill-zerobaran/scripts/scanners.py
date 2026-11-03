#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit-Skill-ZeroBaran — Layer 1: Static Security Analysis Engine (Zero-Cost)
============================================================================
Project   : #35 — Audit-Skill-ZeroBaran (Autonomous Agent-Security Auditor)
Author    : Baran Avisat  |  ZeroBaran Studio
Email     : Baranavisat@gmail.com
WhatsApp  : 00905313263722
License   : MIT (c) 2026 Baran Avisat — Free for commercial use with attribution

This module implements a *cascade* of free static-analysis engines:
  1. Semgrep OSS   (if installed)  -> rules from ./rules/semgrep/
  2. Bandit        (if installed)  -> Python SAST
  3. Native engine (ALWAYS works)  -> 40+ hand-written detectors covering:
        - Hardcoded secrets / API keys / private keys (entropy + patterns)
        - SQL injection & command injection sinks
        - eval/exec/pickle/yaml.unsafe_load deserialization
        - Insecure TLS (verify=False), weak crypto (MD5/SHA1/DES), ssl defaults
        - SSRF, path traversal, unsafe temp files, debug=True Flask/Django
        - CORS '*', dangerous subprocess shell=True
        - AGENT-SPECIFIC threats (LLM skill auditing):
            * prompt-injection surfaces in agent code
            * tool-call definitions granting exec/file/network to agents
            * missing human-in-the-loop on irreversible actions
            * .well-known/mcp/skill manifests with over-broad permissions
        - Dependency risk (requirements.txt pinned-to-latest, known-bad names)
        - IaC / Dockerfile risks (latest tag, privileged, host mount, curl|sh)

Every finding is normalized into one JSON shape so the AI brain, the DB layer
and the Telegram gateway stay engine-agnostic.

CLI:
  python scanners.py scan <path> [--json out.json] [--format text|sarif-lite]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

__version__ = "1.0.0"
__author__ = "Baran Avisat"

SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}

CODE_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".rb", ".go", ".java",
    ".php", ".sh", ".bash", ".zsh", ".sql", ".html", ".htm", ".yaml", ".yml",
    ".json", ".toml", ".env", ".tf", ".dockerfile", ".cs", ".rs", ".kt", ".swift",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
             "build", ".next", ".tox", "site-packages", ".mypy_cache"}
MAX_FILE_BYTES = 1_500_000  # skip giant blobs


@dataclass
class Finding:
    rule_id: str
    title: str
    severity: str                 # CRITICAL/HIGH/MEDIUM/LOW/INFO
    category: str                 # secret|injection|deserialization|crypto|agent|config|deps|iaco|ssrf|misc
    file: str
    line: int
    snippet: str
    cwe: str = ""
    owasp: str = ""
    engine: str = "native"
    confidence: float = 0.8
    fix_hint: str = ""
    fingerprint: str = ""

    def __post_init__(self):
        if not self.fingerprint:
            raw = f"{self.rule_id}|{self.file}|{self.line}|{self.snippet.strip()[:120]}"
            self.fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq: Dict[str, int] = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def iter_files(root: Path) -> List[Path]:
    out: List[Path] = []
    if root.is_file():
        return [root]
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                if p.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            suf = p.suffix.lower()
            if suf in CODE_EXTS or fn.lower() in ("dockerfile", "makefile", ".env",
                                                  "requirements.txt", "gemfile",
                                                  "package.json", "skill.yaml",
                                                  "skill.yml", "manifest.json"):
                out.append(p)
    return sorted(out)


# ---------------------------------------------------------------------------
# NATIVE DETECTOR ENGINE
# ---------------------------------------------------------------------------
# (rule_id, regex, severity, category, title, cwe, fix_hint, min_confidence)
PATTERN_RULES: List[tuple] = [
    # --- Secrets -------------------------------------------------------------
    ("ASZ-SEC-001", re.compile(r"(?i)(api[_-]?key|apikey|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"]([A-Za-z0-9\-_/+=]{16,})['\"]"),
     "CRITICAL", "secret", "Hardcoded API key / token literal", "CWE-798",
     "Move the value to an environment variable or a secret manager; rotate the leaked key immediately.", 0.85),
    ("ASZ-SEC-002", re.compile(r"(?i)(aws_access_key_id)\s*[:=]\s*['\"]?(AKIA[0-9A-Z]{16})"),
     "CRITICAL", "secret", "Hardcoded AWS Access Key ID", "CWE-798",
     "Use IAM roles / AWS Secrets Manager and rotate this access key now.", 0.95),
    ("ASZ-SEC-003", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
     "CRITICAL", "secret", "Private key committed to source", "CWE-798",
     "Remove from VCS history (git filter-repo), load keys from KMS/secret store.", 0.98),
    ("ASZ-SEC-004", re.compile(r"(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|glpat-[A-Za-z0-9_\-]{20}|xox[baprs]-[A-Za-z0-9\-]{10,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_\-]{35})"),
     "CRITICAL", "secret", "Provider token pattern detected (GitHub/GitLab/Slack/OpenAI/Google)", "CWE-798",
     "Revoke & reissue the token; keep it only in CI secrets.", 0.95),
    ("ASZ-SEC-005", re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"),
     "HIGH", "secret", "Hardcoded password literal", "CWE-259",
     "Source credentials from env/vault; enforce strong generated secrets.", 0.75),
    # --- Injection -----------------------------------------------------------
    ("ASZ-INJ-001", re.compile(r"(?i)(execute|query|cursor\.\w+)\s*\(\s*f['\"]"),
     "CRITICAL", "injection", "f-string interpolated into SQL execution (SQLi sink)", "CWE-89",
     "Use parameterized queries: cur.execute('... WHERE id=%s', (user_id,)).", 0.9),
    ("ASZ-INJ-002", re.compile(r"(?i)(SELECT|INSERT INTO|UPDATE .* SET|DELETE FROM)[^'\"]*['\"]\s*(\+|%|\.format\(|f')"),
     "HIGH", "injection", "String-built SQL statement", "CWE-89",
     "Switch to bound parameters or an ORM query builder.", 0.7),
    ("ASZ-INJ-003", re.compile(r"os\.system\s*\(|subprocess\.(call|run|Popen|check_output)\s*\([^)]*shell\s*=\s*True"),
     "HIGH", "injection", "Shell command execution with interpolation risk", "CWE-78",
     "Pass an argument list and shell=False; validate/sanitize any user input.", 0.85),
    ("ASZ-INJ-004", re.compile(r"(?i)eval\s*\(|exec\s*\("),
     "HIGH", "injection", "Dynamic code evaluation (eval/exec)", "CWE-95",
     "Replace with ast.literal_eval or explicit dispatch tables.", 0.6),
    ("ASZ-INJ-005", re.compile(r"(?i)render_template_string\s*\(|Template\s*\(.+\)\.render"),
     "CRITICAL", "injection", "Server-side template injection surface", "CWE-1336",
     "Never render user-controlled templates; use fixed templates + escaped vars.", 0.8),
    # --- Deserialization -----------------------------------------------------
    ("ASZ-DESER-001", re.compile(r"pickle\.loads?\s*\(|marshal\.loads\s*\(|shelve\.open"),
     "CRITICAL", "deserialization", "Unsafe deserialization (pickle/marshal)", "CWE-502",
     "Use JSON or signed messages (itsdangerous); pickle of untrusted bytes = RCE.", 0.9),
    ("ASZ-DESER-002", re.compile(r"yaml\.load\s*\((?![^)]*Loader\s*=)[^)]*\)|yaml\.unsafe_load"),
     "HIGH", "deserialization", "YAML load without SafeLoader", "CWE-502",
     "Use yaml.safe_load(...) explicitly.", 0.85),
    # --- Crypto / TLS --------------------------------------------------------
    ("ASZ-CRY-001", re.compile(r"(?i)hashlib\.(md5|sha1)\s*\("),
     "MEDIUM", "crypto", "Weak hash (MD5/SHA1) used", "CWE-327",
     "Use SHA-256+ (or argon2/bcrypt for passwords).", 0.7),
    ("ASZ-CRY-002", re.compile(r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify\s*:\s*true|ssl\._create_unverified|CURLOPT_SSL_VERIFYPEER.*0)"),
     "HIGH", "crypto", "TLS certificate validation disabled", "CWE-295",
     "Keep verification ON; pin CA bundles instead of disabling checks.", 0.9),
    ("ASZ-CRY-003", re.compile(r"(?i)(DES\.new|RC4|AES\.new\([^)]*MODE_ECB)"),
     "HIGH", "crypto", "Weak cipher / ECB mode", "CWE-327",
     "Use AES-GCM or ChaCha20-Poly1305 (authenticated encryption).", 0.85),
    ("ASZ-CRY-004", re.compile(r"(?i)random\.(randint|random|choice)\s*\([^)]*\).{0,40}(token|secret|nonce|otp|session|password)"),
     "MEDIUM", "crypto", "Non-crypto RNG used for security value", "CWE-330",
     "Use secrets.token_urlsafe / secrets.SystemRandom.", 0.65),
    # --- Config / framework --------------------------------------------------
    ("ASZ-CFG-001", re.compile(r"(?i)debug\s*=\s*True"),
     "MEDIUM", "config", "Debug mode enabled (Flask/Django style)", "CWE-489",
     "Gate DEBUG behind env var defaulting to False in production.", 0.7),
    ("ASZ-CFG-002", re.compile(r"(?i)Access-Control-Allow-Origin['\"]?\s*[:=]\s*['\"]\*['\"]|app\.cors_after_init\(App\.create|CORS\(app\)"),
     "LOW", "config", "Permissive CORS wildcard", "CWE-942",
     "Whitelist exact origins; avoid '*' with credentialed requests.", 0.6),
    ("ASZ-CFG-003", re.compile(r"(?i)(ALLOWED_HOSTS\s*=\s*\[\s*['\"]\*['\"]\s*\])"),
     "MEDIUM", "config", "Django ALLOWED_HOSTS wildcard", "CWE-1021",
     "List explicit domains.", 0.8),
    ("ASZ-SSRF-001", re.compile(r"(?i)requests\.(get|post)\s*\(\s*(?!['\"]https?://(api|cdn)\.)[^)'\"]*\b(url|link|endpoint|target|href|uri)\b"),
     "MEDIUM", "ssrf", "Outbound request to user-controlled URL (SSRF)", "CWE-918",
     "Validate against allow-list; block RFC1918/metadata IPs (169.254.169.254).", 0.55),
    ("ASZ-PATH-001", re.compile(r"(?i)(open\s*\(|send_file\s*\(|FileResponse\s*\()[^)]*(request\.|params\[|query|\+\s*name|\buser_input\b|f['\"])"),
     "MEDIUM", "misc", "Path built from user input (traversal risk)", "CWE-22",
     "Normalize + confine within a base dir (os.path.realpath startswith check).", 0.55),
    # --- Docker / IaC --------------------------------------------------------
    ("ASZ-IAC-001", re.compile(r"(?i)^FROM\s+\S+:latest|RUN\s+(curl|wget)[^|]*\|\s*(ba)?sh"),
     "HIGH", "iaco", "Risky Dockerfile practice (latest tag / pipe-to-shell)", "CWE-829",
     "Pin image digests; download then verify checksum before executing.", 0.8),
    ("ASZ-IAC-002", re.compile(r"(?i)(--privileged|hostPID\s*:\s*true|/var/run/docker\.sock|network_mode\s*:\s*[\"']host)"),
     "CRITICAL", "iaco", "Container escape enabler (privileged/docker.sock/host ns)", "CWE-1610",
     "Drop privileges, read-only rootfs; never expose docker.sock to workloads.", 0.9),
    ("ASZ-IAC-003", re.compile(r"(?i)(USER\s+root|chmod\s+777)"),
     "MEDIUM", "iaco", "Root user / world-writable permissions", "CWE-732",
     "Create non-root USER; chmod 750/640.", 0.7),
    # --- Dependencies --------------------------------------------------------
    ("ASZ-DEP-001", re.compile(r"(?i)(pyjwt==1\.[0-6]|flask<[0-2]|requests<[2]|jinja2<3\.[01]|pillow<9|tensorflow<2\.[056]|numpy<1\.[0-19]|log4j-core|apache-commons-collections[^:]*)"),
     "HIGH", "deps", "Dependency with known critical CVEs", "CWE-1395",
     "Bump to patched version; run `pip-audit`/`npm audit` in CI.", 0.75),
    ("ASZ-DEP-002", re.compile(r"(?i)(colors?|event-stream|merge|coa|ua-parser-js|flat|dot-prop|got@11\.8\.[0-4])\s*@\s*(latest|\d)"),
     "MEDIUM", "deps", "Package historically hit by supply-chain takeover", "CWE-1395",
     "Pin + verify provenance (sigstore); prefer actively maintained alternatives.", 0.5),
    # --- LLM-AGENT SPECIFIC (the 'Audit-Skill' niche) -------------------------
    ("ASZ-AGT-001", re.compile(r"(?i)(ignore (all |any )previous instructions|disregard.{0,20}(prior|previous|above)|you are now|pretend to be|reveal your system prompt|DAN|developer mode)"),
     "HIGH", "agent", "Prompt-injection payload embedded in code/config/data", "CWE-74",
     "Treat all fetched content as untrusted; wrap external text in delimiters + instruct model to ignore instructions inside it.", 0.8),
    ("ASZ-AGT-002", re.compile(r"(?i)(system_prompt\s*=\s*f['\"]|SYSTEM_PROMPT\s*\+?=.*(user|request|input|query))"),
     "HIGH", "agent", "User input concatenated into system prompt", "CWE-74",
     "Never interpolate user content into the system role; separate channels strictly.", 0.85),
    ("ASZ-AGT-003", re.compile(r"(?i)(tool|function)s?\s*[:=].{0,80}(shell|exec|subprocess|filesystem|rmtree|unlink|delete|payment|transfer|purchase)"),
     "CRITICAL", "agent", "Agent tool grants destructive/irreversible capability", "CWE-250",
     "Add human-in-the-loop confirmation + sandbox + allow-listed args for destructive tools.", 0.7),
    ("ASZ-AGT-004", re.compile(r"(?i)(auto_approve|require_confirmation\s*[:=]\s*(false|no)|human_in_the_loop\s*[:=]\s*(false|off)|yolo_mode|dangerously_skip)"),
     "CRITICAL", "agent", "Confirmation gate disabled for agent actions", "CWE-1059",
     "Default require_confirmation=true for anything mutating state/spending money.", 0.9),
    ("ASZ-AGT-005", re.compile(r"(?i)(allowed_origins|webhook_url|callback_url)\s*[:=]\s*['\"]\*['\"]"),
     "MEDIUM", "agent", "Agent webhook/callback accepts any origin", "CWE-284",
     "Pin expected origins + HMAC-sign callbacks.", 0.65),
    ("ASZ-AGT-006", re.compile(r"(?i)(role\s*:\s*system.{0,200}content.*(http|url|fetch|browse))|(fetch_url|http_get).{0,60}(llm|model|prompt|completion)"),
     "HIGH", "agent", "Unvalidated web content fed directly into model context (indirect injection)", "CWE-74",
     "Sanitize/quote fetched content; strip instruction-like lines; lower privilege of resulting context.", 0.6),
    ("ASZ-AGT-007", re.compile(r"(?i)(permissions?).{0,40}\[.{0,80}(\*|all|admin|root|sudo|full_access)"),
     "HIGH", "agent", "Over-broad permission scope in manifest/config", "CWE-269",
     "Apply least-privilege: enumerate exact scopes.", 0.6),
]

ENV_ASSIGN = re.compile(r"(?i)^\s*(?:export\s+)?([A-Z0-9_]*(SECRET|TOKEN|KEY|PASSWORD|PASSPHRASE|APIKEY|API_KEY|CREDENTIAL)[A-Z0-9_]*)\s*=\s*['\"]?([^'\"\s#]{12,})")


def native_scan_file(path: Path, rel: str) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings
    lines = text.splitlines()
    low_name = path.name.lower()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") and "TODO" not in stripped.upper() and not re.search(r"(key|token|secret|password)", stripped, re.I):
            # still scan commented-out secrets but downgrade below via confidence
            pass
        for (rid, rx, sev, cat, title, cwe, fix, conf) in PATTERN_RULES:
            m = rx.search(line)
            if m:
                findings.append(Finding(
                    rule_id=rid, title=title, severity=sev, category=cat,
                    file=rel, line=i, snippet=line.strip()[:200], cwe=cwe,
                    owasp=_owasp_for(cat), engine="native",
                    confidence=conf, fix_hint=fix))
        # high-entropy credential in .env-style lines
        me = ENV_ASSIGN.match(line)
        if me:
            val = me.group(3)
            if _looks_secret(val):
                findings.append(Finding(
                    rule_id="ASZ-SEC-006", title="High-entropy credential assigned inline",
                    severity="CRITICAL", category="secret", file=rel, line=i,
                    snippet=line.strip()[:200], cwe="CWE-798", owasp=_owasp_for("secret"),
                    engine="native", confidence=0.85,
                    fix_hint="Load from secret manager; add file to .gitignore; rotate."))
    # whole-file heuristics
    if low_name.endswith(("requirements.txt",)) or "pip install" in text:
        findings += _dep_risk(text, rel)
    if low_name == "dockerfile" or path.suffix == "" and text.lstrip().startswith("FROM"):
        findings += _docker_heuristics(text, rel)
    if low_name in ("skill.yaml", "skill.yml", "manifest.json") or '"mcp"' in text:
        findings += _manifest_heuristics(text, rel)
    return findings


_SECRET_OK = re.compile(r"^[A-Za-z0-9\-_+/=.]{12,}$")


def _looks_secret(v: str) -> bool:
    v = v.strip("'\"")
    if not _SECRET_OK.match(v):
        return False
    placeholders = ("your_", "example", "changeme", "xxxx", "<", "${", "{{", "dummy", "placeholder")
    if any(p in v.lower() for p in placeholders):
        return False
    return len(v) >= 16 and _shannon_ok(v)


def _shannon_ok(v: str) -> bool:
    return shannon_entropy(v) >= 3.2


def _owasp_for(cat: str) -> str:
    return {
        "secret": "A07:2021 Identification and Authentication Failures",
        "injection": "A03:2021 Injection",
        "deserialization": "A08:2021 Software and Data Integrity Failures",
        "crypto": "A02:2021 Cryptographic Failures",
        "ssrf": "A10:2021 Server-Side Request Forgery",
        "agent": "LLM01:2025 Prompt Injection / LLM06 Excessive Agency",
        "iaco": "A05:2021 Security Misconfiguration",
        "deps": "A06:2021 Vulnerable & Compromised Components",
        "config": "A05:2021 Security Misconfiguration",
    }.get(cat, "A05:2021 Security Misconfiguration")


KNOWN_BAD_DEPS = {
    "pyjwt<2.4": ("CVE-2022-29217", "JWT algorithm confusion -> auth bypass"),
    "flask<2.2": ("CVE-2023-30861", "Session fixation on unauthenticated cookie rotation"),
    "werkzeug<2.2": ("CVE-2023-25577", "Denial of service via multipart parsing"),
    "requests<2.31": ("CVE-2023-32681", "Proxy-Authorization leak on redirect"),
    "jinja2<3.1": ("CVE-2024-22195", "Sandbox escape via HTML attributes"),
    "pillow<10": ("CVE-2023-50447", "Arbitrary code via crafted ImageMath eval"),
    "torch<2": ("CVE-2023-48022", "Deserialization of unpickled models"),
}


def _dep_risk(text: str, rel: str) -> List[Finding]:
    out = []
    for ln, line in enumerate(text.splitlines(), 1):
        l = line.strip().lower()
        if not l or l.startswith("#"):
            continue
        for pat, (cve, why) in KNOWN_BAD_DEPS.items():
            name, _, ver = pat.partition("<")
            if l.startswith(name) and ("<" in l or "==" in l):
                mm = re.search(r"[<>=!~]*\s*([0-9][0-9a-zA-Z.\-]*)", l[len(name):])
                if mm:
                    try:
                        bad = tuple(int(x) for x in ver.replace("~", ".").split("."))
                        got = tuple(int(x) for x in mm.group(1).split(".")[:len(bad)])
                        if got < bad:
                            out.append(Finding(
                                rule_id="ASZ-DEP-003",
                                title=f"Vulnerable dependency {name} ({cve}): {why}",
                                severity="HIGH", category="deps", file=rel, line=ln,
                                snippet=line[:200], cwe="CWE-1395",
                                owasp=_owasp_for("deps"), engine="native",
                                confidence=0.9, fix_hint=f"Upgrade {name} to >= {ver}"))
                    except ValueError:
                        pass
        if re.match(r"^[a-z0-9_.\-]+$", l) and "@" not in l and "==" not in l and ">=" not in l:
            out.append(Finding(rule_id="ASZ-DEP-004", title="Unpinned dependency (supply-chain drift)",
                               severity="LOW", category="deps", file=rel, line=ln, snippet=line[:200],
                               cwe="CWE-1104", owasp=_owasp_for("deps"), engine="native",
                               confidence=0.6, fix_hint="Pin exact versions or use hashes (--require-hashes)."))
    return out


def _docker_heuristics(text: str, rel: str) -> List[Finding]:
    out = []
    for ln, line in enumerate(text.splitlines(), 1):
        l = line.strip()
        if re.search(r"(?i)^from\s+\S+$", l) and ":" not in l and "@" not in l:
            out.append(Finding("ASZ-IAC-004", "Unpinned base image tag", "MEDIUM", "iaco",
                               rel, ln, l[:200], "CWE-1104", _owasp_for("iaco"), "native", 0.7,
                               "Pin digest: FROM image@sha256:..."))
        if re.search(r"(?i)^copy.*(--chown=root|secret)", l):
            out.append(Finding("ASZ-IAC-005", "COPY may bake secrets into image layers", "HIGH",
                               "secret", rel, ln, l[:200], "CWE-538", _owasp_for("secret"),
                               "native", 0.6, "Use BuildKit --mount=type=secret (not COPY)."))
    return out


def _manifest_heuristics(text: str, rel: str) -> List[Finding]:
    out = []
    try:
        data = json.loads(text) if rel.endswith(".json") else None
    except Exception:
        data = None
    blob = json.dumps(data) if data is not None else text
    if re.search(r"(?i)networking|network|http", blob) and re.search(r"(?i)allowlist|allowed_domains|domains", blob) is None:
        out.append(Finding("ASZ-AGT-008", "Skill manifest grants network access without domain allow-list",
                           "MEDIUM", "agent", rel, 1, text.strip()[:200], "CWE-284",
                           _owasp_for("agent"), "native", 0.55,
                           "Enumerate allowed_domains; deny-by-default egress."))
    if re.search(r"(?i)(\"scripts\"|entrypoint|command)\s*[:=]", blob) and re.search(r"(?i)(curl|wget|python -c|bash -c|node -e)", blob):
        out.append(Finding("ASZ-AGT-009", "Manifest ships executable entry that fetches remote code",
                           "CRITICAL", "agent", rel, 1, text.strip()[:200], "CWE-829",
                           _owasp_for("agent"), "native", 0.8,
                           "Vendor code locally + checksum; remove runtime downloads."))
    return out


# ---------------------------------------------------------------------------
# EXTERNAL ENGINE WRAPPERS (Semgrep / Bandit) — optional, auto-detected
# ---------------------------------------------------------------------------
def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_semgrep(target: Path, rules_dir: Optional[Path]) -> List[Finding]:
    if not _have("semgrep"):
        return []
    args = ["semgrep", "--json", "--quiet", "--metrics=off", "--lang", "auto"]
    if rules_dir and rules_dir.exists():
        args += ["--config", str(rules_dir)]
    else:
        args += ["--config", "auto"]  # community registry (still free)
    args += ["--", str(target)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=600)
        data = json.loads(proc.stdout or "{}")
    except Exception:
        return []
    out = []
    for r in data.get("results", []):
        sev_map = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}
        out.append(Finding(
            rule_id=f"SEM-{r.get('check_id', 'rule').split('.')[-1]}",
            title=r.get("extra", {}).get("message", "Semgrep finding")[:180],
            severity=sev_map.get(r.get("extra", {}).get("severity", "WARNING"), "MEDIUM"),
            category="injection",
            file=str(r.get("path", target)), line=int(r.get("start", {}).get("line", 1)),
            snippet=(r.get("extra", {}).get("lines", "") or "").strip()[:200],
            cwe=", ".join(re.findall(r"cwe:\s*([-\d]+)", r.get("extra", {}).get("metadata", {}).get("cwe", "") or "", re.I)) or "CWE-noinfo",
            engine="semgrep", confidence=0.8,
            fix_hint=r.get("extra", {}).get("fix", "")[:300]))
    return out


def run_bandit(target: Path) -> List[Finding]:
    if not (target.is_dir() or target.suffix == ".py") or not _have("bandit"):
        return []
    try:
        proc = subprocess.run(["bandit", "-f", "json", "-q", "-r", str(target)],
                              capture_output=True, text=True, timeout=600)
        data = json.loads(proc.stdout or "{}")
    except Exception:
        return []
    sev_map = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
    out = []
    for r in data.get("results", []):
        out.append(Finding(
            rule_id=r.get("test_id", "B000"), title=r.get("issue_text", "")[:180],
            severity=sev_map.get(r.get("issue_severity", "MEDIUM"), "MEDIUM"),
            category="injection", file=r.get("filename", ""), line=int(r.get("line_number", 1)),
            snippet=(r.get("code", "") or "").strip()[:200],
            cwe=re.sub(r"\D", "", str(r.get("issue_cwe", {}).get("id", ""))) and f"CWE-{re.sub(r'[^0-9]', '', str(r.get('issue_cwe', {}).get('id', '')))}" or "CWE-noinfo",
            engine="bandit", confidence=0.85,
            fix_hint=r.get("issue_text", "")[:200]))
    return out


# ---------------------------------------------------------------------------
# ORCHESTRATION
# ---------------------------------------------------------------------------
def scan(target: str | Path, rules_dir: Optional[str | Path] = None,
         engines: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run the full cascade and return a normalized report dict."""
    t = Path(target).resolve()
    engines = engines or ["native", "semgrep", "bandit"]
    findings: List[Finding] = []
    files_scanned = 0
    engines_used = []

    if "native" in engines:
        for p in iter_files(t):
            files_scanned += 1
            rel = str(p.relative_to(t.parent) if t.is_dir() else p.name)
            findings += native_scan_file(p, rel)
        engines_used.append(f"native-v{__version__}")
    if "semgrep" in engines:
        s = run_semgrep(t, Path(rules_dir) if rules_dir else None)
        findings += s
        if s or _have("semgrep"):
            engines_used.append("semgrep")
    if "bandit" in engines:
        b = run_bandit(t)
        findings += b
        if b or _have("bandit"):
            engines_used.append("bandit")

    # dedupe by fingerprint, keep highest-confidence engine view
    seen: Dict[str, Finding] = {}
    for f in findings:
        k = f.fingerprint
        if k not in seen or SEVERITY_ORDER[f.severity] > SEVERITY_ORDER[seen[k].severity]:
            seen[k] = f
    uniq = sorted(seen.values(), key=lambda x: (-SEVERITY_ORDER[x.severity], x.file, x.line))

    counts = {s: 0 for s in SEVERITY_ORDER}
    cats: Dict[str, int] = {}
    for f in uniq:
        counts[f.severity] += 1
        cats[f.category] = cats.get(f.category, 0) + 1

    score = _risk_score(counts)
    report = {
        "schema": "audit-skill-zerobaran/report@1",
        "scan_id": hashlib.sha256(f"{t}|{_now_iso()}|{len(uniq)}".encode()).hexdigest()[:16],
        "started_at": _now_iso(),
        "target": str(t),
        "files_scanned": files_scanned or len(iter_files(t)),
        "engines": engines_used,
        "findings_total": len(uniq),
        "counts_by_severity": counts,
        "counts_by_category": cats,
        "security_score": score,          # 0..100 (100 = clean)
        "verdict": _verdict(score, counts),
        "findings": [asdict(f) for f in uniq],
        "meta": {"project": "Audit-Skill-ZeroBaran", "author": __author__,
                 "license": "MIT (c) 2026 Baran Avisat", "contact": "Baranavisat@gmail.com"},
    }
    return report


def _risk_score(counts: Dict[str, int]) -> int:
    penalty = (counts.get("CRITICAL", 0) * 25 + counts.get("HIGH", 0) * 10 +
               counts.get("MEDIUM", 0) * 4 + counts.get("LOW", 0) * 1)
    return max(0, 100 - penalty)


def _verdict(score: int, counts: Dict[str, int]) -> str:
    if counts.get("CRITICAL", 0):
        return "BLOCKED"      # must-fix before deploy
    if score >= 90:
        return "APPROVED"
    if score >= 70:
        return "APPROVED_WITH_WARNINGS"
    return "REJECTED"


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Audit-Skill-ZeroBaran static scanner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("scan")
    sp.add_argument("target")
    sp.add_argument("--rules", default=None)
    sp.add_argument("--out", default="-")
    sp.add_argument("--format", choices=["json", "text"], default="json")
    sp.add_argument("--engines", default="native,semgrep,bandit")
    args = ap.parse_args(argv)

    rep = scan(args.target, args.rules, args.engines.split(","))
    if args.format == "json":
        payload = json.dumps(rep, ensure_ascii=False, indent=2)
    else:
        lines = [f"🛡️ Audit-Skill-ZeroBaran — verdict: {rep['verdict']} "
                 f"(score {rep['security_score']}/100)",
                 f"files={rep['files_scanned']} findings={rep['findings_total']} "
                 f"engines={','.join(rep['engines'])}"]
        for f in rep["findings"]:
            lines.append(f"  [{f['severity']:8}] {f['rule_id']} {f['file']}:{f['line']} — {f['title']}")
        payload = "\n".join(lines)
    if args.out == "-":
        print(payload)
    else:
        Path(args.out).write_text(payload, encoding="utf-8")
    return 0 if rep["verdict"] != "BLOCKED" else 2


if __name__ == "__main__":
    sys.exit(main())
