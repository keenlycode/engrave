# Recommended Plan

1. Fix watch-mode Markdown handling so `.md` changes rebuild affected output behavior consistently.
2. Fix SSE publishing to emit exactly one event per change batch.
3. Make delete handling idempotent in watch/server flows.
4. Add regression tests for the three cases above.
5. Align `README.md` and `docs-src/quickstart.md` with actual `--copy` requirements.
6. Decide whether `server` should preview rendered source or built output before touching that behavior.
