# Engrave

**A lightweight static-site generator using Python + Jinja2**  
Version: 3.1.6dev

## 🚀 What is Engrave

Engrave turns a directory of HTML templates (plus optional Markdown snippets) into a ready-to-serve static site. It is ideal for documentation, simple marketing pages, or any static content that benefits from Jinja2 templating without adding a backend.

## 🌟 Highlights

- Renders `.html` templates with Jinja2; path segments starting with `_` are ignored for HTML builds.
- Built-in Markdown helpers: include Markdown files via `markdown('path.md')` and render inline strings with the `|markdown` filter.
- Regex-driven asset copying (`--copy`) and exclusion rules (`--exclude`) applied to both renders and copies.
- Live preview server powered by FastAPI + Uvicorn with watchfiles + SSE for instant reload hooks.
- Simple Cyclopts-based CLI; works on Python 3.10+.

## 🧰 Installation

```bash
pip install engrave
```

## 📘 CLI Usage

### Build

Render templates and copy assets from a source directory into an output directory.

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

### Development Server (auto-rebuild + SSE)

Run an initial build, start FastAPI/Uvicorn, and stream file-change events for live reload.

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
│    --watch --empty-watch      Additional path regex patterns to watch for changes (in addition to .html and patterns       │
│                               matched by --copy). Matching paths will trigger Server-Sent Events (SSE). [default: []]      │
│    --sse-url                  SSE URL (Server Side Event) to emite watch event [default: __engrave/watch]                  │
│    --log-level                [choices: CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET] [default: INFO]        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

- Serves rendered `.html` directly from `DIR_SRC` and other assets from `DIR_DEST`.
- Watches `DIR_SRC` for `.html`/`.md` changes, applies the same copy/exclude rules as `build`, and mirrors deletions.
- `--watch` accepts additional regex patterns (relative to the current working directory) whose changes are forwarded to clients as `type='watch'`.
- Add a reload hook in your page:

```js
const source = new EventSource('/__engrave/watch');
source.addEventListener('change', () => window.location.reload());
```

## 🧱 Templates & Markdown helpers

- `markdown('path.md')` loads a Markdown file relative to the current template (stays inside configured template roots).
- `{{ content | markdown }}` converts inline Markdown strings.
- Markdown files are rendered as Jinja templates with the current context before Markdown conversion, so you can use template variables inside `.md` snippets.
- Markdown rendering uses Mistune by default and caches file reads/compilation by mtime; you can supply a custom parser via `get_template(..., markdown_to_html=...)` if embedding Engrave programmatically.
- Multiple template roots are supported by passing a list to `dir_src`.

## 🛠️ Testing

```bash
python -m unittest
```

## 📄 License

MIT — see `LICENSE`.
