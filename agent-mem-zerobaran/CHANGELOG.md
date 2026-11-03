# Changelog — Agent-Mem-ZeroBaran™ (#34)
## v1.0.0 — 2026-11-03
- L1 Recursive splitter (LangChain-equivalent, stdlib) + transcript windowing + dedupe fingerprints.
- L2 Embedding cascade (Gemini free → deterministic Hash-Ngram local) + dual vector store: Supabase pgvector (HNSW, RPC batch upsert) and offline SQLite exact-cosine with hybrid relevance×recency scoring and access heat tracking.
- L3 Memory Brain: Groq→Gemini→MockBrain cascade; memory cards (facts/decisions/preferences/todos/tags); grounded recall with citations, confidence and context-budget-enforced injection block.
- L4 Telegram reports (ingest/recall/weekly digest) + zero-dependency HTTP gateway (/remember /recall /stats /health, token auth) + Streamlit command center.
- GitHub Actions cron: hygiene every 6h, weekly digest Mon 03:07 UTC, artifact persistence.
- Tests: 42/42 offline contract tests green. Docs & branding: README/AUTHORS/SUPPORT/LICENSE (Baran Avisat).
