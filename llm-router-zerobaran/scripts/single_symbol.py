#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze one symbol given via SYM env (used by workflow_dispatch). © Baran Avisat."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import llm_router

cfg = llm_router.load_cfg()
sym = os.environ.get("SYM", "").strip()
if not sym:
    print("SYM env missing"); sys.exit(2)
res = llm_router.analyze_symbol(sym, "1d", cfg)
res.pop("narrative", None)
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
