# Engrave Guides

Opinionated documentation for Engrave, a lightweight static-site generator built on Python and Jinja2. Use these guides to get a site rendering quickly, then lean on the CLI reference when you need copy/exclude/watch-add control or live preview.

## Where to go
- [Quickstart](quickstart.md): build a minimal site and understand the directory layout Engrave expects.
- [CLI Reference](cli.md): arguments for `engrave build` and `engrave server`, plus copy/exclude/watch-add notes.
- [Templates + Markdown](templates.md): Jinja usage, Markdown helper/filter behavior, and partial conventions.
- [Live Preview](live-preview.md): how the FastAPI dev server and SSE reload hook fit together.

## Core behaviors to know
- Engrave renders only `.html` files; any path segment starting with `_` is skipped for HTML output (still usable via `{% include %}`).
- Markdown is pulled in from templates via the `markdown()` helper or `|markdown` filter with path-traversal protection and mtime-based caching.
- Asset copying is opt-in with `--copy` regex patterns; `--exclude` uses regex matching across both rendering and copying.
- The dev server renders `.html` directly from `dir_src`, serves other files from `dir_dest`, and streams file-change events from a configurable SSE endpoint (`--sse-url`, default `__engrave/watch`).
