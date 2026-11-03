#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Layer 4b: Zero-dependency HTTP API Gateway
=============================================================
Project #34 — ZeroBaran Innovation Fleet | © Baran Avisat
Give any agent (LangChain/LlamaIndex/custom) memory over plain HTTP:
  POST /remember   {"doc_id","text","source"}      -> ingests + summarizes
  POST /recall     {"question","top_k","doc_filter"}-> grounded context block
  GET  /stats      memory health JSON
  GET  /health     liveness
Runs on stdlib http.server — free forever, no FastAPI install needed
(FastAPI-compatible drop-in noted in README).
"""
from __future__ import annotations
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(__file__))
from mem_engine import MemoryEngine  # noqa: E402

ENGINE = None
TOKEN = os.environ.get("AGENTMEM_API_TOKEN", "")


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth_ok(self) -> bool:
        if not TOKEN:
            return True
        return self.headers.get("X-Auth-Token", "") == TOKEN

    def do_GET(self):
        if not self._auth_ok():
            return self._json(401, {"error": "unauthorized"})
        if self.path == "/health":
            return self._json(200, {"ok": True, "service": "agent-mem-zerobaran"})
        if self.path == "/stats":
            return self._json(200, ENGINE.stats())
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if not self._auth_ok():
            return self._json(401, {"error": "unauthorized"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length).decode()) if length else {}
        except json.JSONDecodeError:
            return self._json(400, {"error": "invalid json"})
        try:
            if self.path == "/remember":
                res = ENGINE.remember(data["doc_id"], data["text"],
                                      source=data.get("source", "api"))
                return self._json(200, res)
            if self.path == "/recall":
                res = ENGINE.recall(data["question"],
                                    top_k=int(data.get("top_k", 5)),
                                    doc_filter=data.get("doc_filter"),
                                    notify=bool(data.get("notify", False)))
                return self._json(200, res)
        except KeyError as e:
            return self._json(400, {"error": f"missing field {e}"})
        except Exception as e:
            return self._json(500, {"error": str(e)})
        self._json(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        pass


def serve(port: int = 8788):
    global ENGINE
    ENGINE = MemoryEngine()
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"🧠 Agent-Mem gateway listening :{port} (provider={ENGINE.brain.provider}, "
          f"store={ENGINE.store_mode})")
    srv.serve_forever()


if __name__ == "__main__":
    serve(int(os.environ.get("PORT", "8788")))
