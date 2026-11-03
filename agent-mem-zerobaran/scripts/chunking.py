#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Mem-ZeroBaran — Layer 1: Ingestion & Chunking (LangChain-style, zero deps)
============================================================================
Project #34 of the ZeroBaran Innovation Fleet.
Author   : Baran Avisat
Email    : Baranavisat@gmail.com
WhatsApp : 00905313263722
Copyright: (c) 2026 Baran Avisat — ZeroBaran Studio. All rights reserved.
License  : MIT (see LICENSE). Free forever, self-hosted, private by design.

Splits long agent context into overlapping semantic chunks that are cheap to
embed and precise to retrieve. No LangChain install required — the same
recursive splitter algorithm implemented in pure stdlib Python.
"""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]


@dataclass
class Chunk:
    text: str
    index: int
    section: str = ""
    tokens_est: int = 0
    chunk_id: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def est_tokens(text: str) -> int:
    """Rough token estimate (~3.6 chars/token, works for AR + EN)."""
    return max(1, int(len(text) / 3.6))


def _split_with_sep(text: str, sep: str) -> List[str]:
    if sep == "":
        return list(text)
    parts = text.split(sep)
    out = []
    for i, p in enumerate(parts):
        out.append(p if i == len(parts) - 1 else p + sep)
    return [p for p in out if p.strip()]


def _hard_window(text: str, chunk_size: int, overlap: int) -> List[str]:
    windows = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(text), step):
        windows.append(text[i:i + chunk_size])
    return [w.strip() for w in windows if w.strip()]


def recursive_split(text: str, chunk_size: int = 400, overlap: int = 60,
                    _depth: int = 0) -> List[str]:
    """LangChain RecursiveCharacterTextSplitter equivalent (stdlib only)."""
    if len(text) <= chunk_size:
        return [text.strip()] if text.strip() else []
    if _depth > 6:                       # recursion guard -> graceful windowing
        return _hard_window(text, chunk_size, overlap)
    for sep in SEPARATORS:
        if sep in text:
            pieces = _split_with_sep(text, sep)
            if len(pieces) <= 1:
                continue
            if all(len(p) <= chunk_size for p in pieces):
                return merge_pieces(pieces, chunk_size, overlap)
            deep: List[str] = []
            progressed = False
            for p in pieces:
                sub = recursive_split(p, chunk_size, overlap, _depth + 1)
                deep.extend(sub)
                if len(sub) > 1 or (sub and len(sub[0]) < len(p)):
                    progressed = True
            if progressed and deep:
                return merge_pieces(deep, chunk_size, overlap) \
                    if _depth == 0 else deep
    # last resort: hard window
    return _hard_window(text, chunk_size, overlap)


def merge_pieces(pieces: List[str], chunk_size: int, overlap: int) -> List[str]:
    """Greedy pack with tail-overlap so meaning is never cut cold."""
    out: List[str] = []
    cur = ""
    for p in pieces:
        if cur and len(cur) + len(p) > chunk_size:
            out.append(cur.strip())
            tail = cur[-overlap:] if overlap else ""
            cur = (tail + " " + p).strip() if tail else p
        else:
            cur = (cur + p) if cur else p
    if cur.strip():
        out.append(cur.strip())
    return out


def fingerprint(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "ignore")).hexdigest()[:16]


def detect_section(line: str) -> str:
    m = re.match(r"^(#{1,4}\s.+|\*\*.+\*\*|==.+==|---.+---)\s*$", line.strip())
    return m.group(1).strip("#*= ") if m else ""


def chunk_document(doc_text: str, doc_id: str, source: str = "",
                   chunk_size: int = 400, overlap: int = 60,
                   dedupe: bool = True) -> List[Chunk]:
    """Turn one raw document (chat log / project notes / code comments)
    into deduplicated, identified chunks ready for embedding."""
    raw_pieces = recursive_split(doc_text, chunk_size, overlap)
    seen_fp = set()
    chunks: List[Chunk] = []
    section = ""
    for piece in raw_pieces:
        head_line = piece.split("\n", 1)[0]
        s = detect_section(head_line)
        if s:
            section = s
        fp = fingerprint(piece)
        if dedupe and fp in seen_fp:
            continue
        seen_fp.add(fp)
        cid = f"{doc_id}:{len(chunks):04d}"
        chunks.append(Chunk(
            text=piece,
            index=len(chunks),
            section=section,
            tokens_est=est_tokens(piece),
            chunk_id=cid,
            meta={"source": source, "fingerprint": fp, "lang": guess_lang(piece)},
        ))
    return chunks


def guess_lang(text: str) -> str:
    arabic = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    return "ar" if arabic > max(4, len(text) * 0.15) else "en"


def chunk_transcript(messages: List[Dict[str, str]], doc_id: str,
                     source: str = "telegram", per_window: int = 8,
                     overlap: int = 2) -> List[Chunk]:
    """Slide a message-window over an agent/user transcript so conversational
    memory keeps short-term continuity (window) plus long-term recall."""
    chunks: List[Chunk] = []
    step = max(1, per_window - overlap)
    for start in range(0, len(messages), step):
        win = messages[start:start + per_window]
        if not win:
            break
        body = "\n".join(f"[{m.get('role','user')}]: {m.get('content','')}" for m in win)
        fp = fingerprint(body)
        cid = f"{doc_id}:t{len(chunks):04d}"
        chunks.append(Chunk(text=body, index=len(chunks), section="transcript",
                            tokens_est=est_tokens(body), chunk_id=cid,
                            meta={"source": source, "fingerprint": fp,
                                  "lang": guess_lang(body),
                                  "turn_range": [start, start + len(win)]}))
    return chunks


if __name__ == "__main__":
    demo = ("## Project Alpha\n" + "The client wants a free sentiment radar. " * 30
            + "\n## Budget\nZero dollars forever. " * 40)
    cs = chunk_document(demo, "demo-doc", source="cli")
    print(f"chunks={len(cs)} first={cs[0].chunk_id} tokens~{cs[0].tokens_est}")
