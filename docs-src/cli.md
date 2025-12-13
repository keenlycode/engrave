# CLI Reference

Engrave ships two commands: `build` and `server`. They share build/copy/exclude options; `server` adds live preview controls.

## engrave build
```bash
engrave build DIR_SRC DIR_DEST [--copy REGEX ...] [--exclude GLOB ...] [--log-level LEVEL]
```
- `DIR_SRC`: root directory containing templates/assets to process.
- `DIR_DEST`: output directory (created if missing).
- `--copy`: regex patterns (evaluated against paths inside `DIR_SRC`) for files to copy verbatim.
- `--exclude`: glob-style patterns applied to both HTML rendering and copying.
- `--log-level`: log verbosity (`INFO` default); `LOG_LEVEL` env var is also honored.

Behavior highlights:
- Only `.html` files are rendered; any path segment starting with `_` is skipped for HTML output (but still available for `{% include %}`).
- Markdown files are not auto-rendered; pull them into templates via `markdown()` or `|markdown`.
- Files matching a copy regex are copied as-is; avoid copy rules that include `.html` so you do not process the same file twice.

## engrave server
```bash
engrave server DIR_SRC DIR_DEST \
  [--copy REGEX ...] [--exclude GLOB ...] [--watch REGEX ...] \
  [--host 127.0.0.1] [--port 8000] [--sse-url __engrave/watch] \
  [--log-level LEVEL]
```
- Performs an initial build using the same pipeline as `engrave build`.
- Serves `.html` by rendering directly from `DIR_SRC`; other requests are served from `DIR_DEST`.
- Watches `.html` and `.md` under `DIR_SRC`, plus copy targets. Additional `--watch` regexes are matched against the current working directory and only emit SSE events (no build/copy).
- Streams change events to the SSE endpoint at `--sse-url` (default `__engrave/watch`) for browser reload hooks.
- Host/port control the FastAPI + Uvicorn development server; log level follows `--log-level` / `LOG_LEVEL`.
