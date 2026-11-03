#!/usr/bin/env python3
"""Clean, hardened agent skill — expected verdict APPROVED (100/100).
Part of Audit-Skill-ZeroBaran examples (c) Baran Avisat."""
import os
import re
import subprocess
from pathlib import Path

ALLOWED_HOSTS = {"api.openweathermap.org"}
PARAM_SQL = "SELECT name, temp FROM cities WHERE code = %s"  # used with bound params


def weather_api_key() -> str:
    return os.environ["WEATHER_API_KEY"]  # never hardcoded


def safe_lookup(code: str) -> str:
    if not re.fullmatch(r"[A-Za-z]{2,8}", code):
        raise ValueError("bad city code")
    return code.lower()


def run_report(code: str) -> str:
    out = subprocess.run(["python", "-c", "print('ok')"], shell=False,
                         capture_output=True, text=True, check=True)
    return out.stdout.strip() + safe_lookup(code)


if __name__ == "__main__":
    print(run_report("OSLO"))
