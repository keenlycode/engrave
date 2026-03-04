# CLI Reference

Engrave ships three commands: `build`, `watch`, and `server`. They share build/copy/exclude options; `watch` and `server` add live-update controls.

## engrave build
```bash
$ engrave build -h
Usage: engrave build [ARGS] [OPTIONS]

Build static HTML files from templates.

╭─ Parameters ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  DIR-SRC --dir-src          [required]                                                                           │
│ *  DIR-DEST --dir-dest        [required]                                                                           │
│    --copy --empty-copy        [default: []]                                                                        │
│    --exclude --empty-exclude  [default: []]                                                                        │
│    --log-level                [choices: CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET] [default:      │
│                               INFO]                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Behavior highlights:
- Only `.html` files are rendered; any path segment starting with `_` is skipped for HTML output (but still available for `{% include %}`).
- Markdown files are not auto-rendered; pull them into templates via `markdown()` or `|markdown`.
- Files matching a copy regex are copied as-is; avoid copy rules that include `.html` so you do not process the same file twice.

## engrave server
```bash
$ engrave server -h
Usage: engrave server [ARGS] [OPTIONS]

Start a development server with live preview.

╭─ Parameters ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  DIR-SRC --dir-src              [required]                                                                       │
│ *  DIR-DEST --dir-dest            [required]                                                                       │
│    --copy --empty-copy            [default: []]                                                                    │
│    --exclude --empty-exclude      [default: []]                                                                    │
│    --log-level                    [choices: CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET] [default:  │
│                                   INFO]                                                                            │
│    --watch-add --empty-watch-add  [default: []]                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- Performs an initial build using the same pipeline as `engrave build`.
- Serves `.html` by rendering directly from `DIR_SRC`; other requests are served from `DIR_DEST`.
- Watches `.html` and `.md` under `DIR_SRC`, plus copy targets. Additional `--watch-add` regexes are matched against the current working directory and only emit SSE events (no build/copy).
- Streams change events to the SSE endpoint at `--sse-url` (default `/__engrave/watch`) for browser reload hooks.
- Host/port control the FastAPI + Uvicorn development server; log level follows `--log-level` / `LOG_LEVEL`.

## engrave watch
```bash
$ engrave watch -h
Usage: engrave watch [ARGS] [OPTIONS]

Watch source files and rebuild/copy without starting an HTTP server.

╭─ Parameters ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  DIR-SRC --dir-src              [required]                                                                       │
│ *  DIR-DEST --dir-dest            [required]                                                                       │
│    --copy --empty-copy            [default: []]                                                                    │
│    --exclude --empty-exclude      [default: []]                                                                    │
│    --log-level                    [choices: CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET] [default:  │
│                                   INFO]                                                                            │
│    --host                         [default: 127.0.0.1]                                                             │
│    --port                         [default: 8000]                                                                  │
│    --watch-add --empty-watch-add  [default: []]                                                                    │
│    --sse-url                      [default: /__engrave/watch]                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- Performs an initial build using the same pipeline as `engrave build`.
- Watches `.html` and `.md` under `DIR_SRC`, plus copy targets.
- Additional `--watch-add` regexes are matched against the current working directory and are logged as `type='watch'`.
- Does not start FastAPI, Uvicorn, or the SSE endpoint.
