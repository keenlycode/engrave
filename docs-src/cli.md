# CLI Reference

Engrave ships two commands: `build` and `server`. They share build/copy/exclude options; `server` adds live preview controls.

## engrave build
```bash
engrave build -h
Usage: engrave build [ARGS] [OPTIONS]

Build static HTML files from templates.

╭─ Parameters ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --dir-src                  Source directory containing input files [required]                                           │
│ *  --dir-dest                 Destination directory for build output [required]                                            │
│    --copy --empty-copy        Path RegEx copy verbatim [default: []]                                                       │
│    --exclude --empty-exclude  Path RegEx to exclude from processing [default: []]                                          │
│    --log-level                [choices: CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET] [default: INFO]        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Behavior highlights:
- Only `.html` files are rendered; any path segment starting with `_` is skipped for HTML output (but still available for `{% include %}`).
- Markdown files are not auto-rendered; pull them into templates via `markdown()` or `|markdown`.
- Files matching a copy regex are copied as-is; avoid copy rules that include `.html` so you do not process the same file twice.

## engrave server
```bash
engrave server -h
Usage: engrave server [ARGS] [OPTIONS]

Start a development server with live preview.

╭─ Parameters ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --dir-src                  Source directory containing input files [required]                                           │
│ *  --dir-dest                 Destination directory for build output [required]                                            │
│    --copy --empty-copy        Path RegEx copy verbatim [default: []]                                                       │
│    --exclude --empty-exclude  Path RegEx to exclude from processing [default: []]                                          │
│    --host                     Host interface to bind the development server [default: 127.0.0.1]                           │
│    --port                     Port number for the development server [default: 8000]                                       │
│    --watch-add --empty-watch-add                                                                                           │
│                               Additional path regex patterns to watch for changes (in addition to .html and patterns       │
│                               matched by --copy). Matching paths will trigger Server-Sent Events (SSE). [default: []]      │
│    --sse-url                  SSE URL (Server Side Event) to emite watch event [default: __engrave/watch]                  │
│    --log-level                [choices: CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET] [default: INFO]        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- Performs an initial build using the same pipeline as `engrave build`.
- Serves `.html` by rendering directly from `DIR_SRC`; other requests are served from `DIR_DEST`.
- Watches `.html` and `.md` under `DIR_SRC`, plus copy targets. Additional `--watch-add` regexes are matched against the current working directory and only emit SSE events (no build/copy).
- Streams change events to the SSE endpoint at `--sse-url` (default `__engrave/watch`) for browser reload hooks.
- Host/port control the FastAPI + Uvicorn development server; log level follows `--log-level` / `LOG_LEVEL`.
