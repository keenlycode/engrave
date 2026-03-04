# Engrave

**A lightweight static-site generator using Python + Jinja2**  
Version: 3.2.1

## 🚀 What is Engrave

Engrave turns a directory of HTML templates (plus optional Markdown snippets) into a ready-to-serve static site. It is ideal for documentation, simple marketing pages, or any static content that benefits from Jinja2 templating without adding a backend.

## 🌟 Highlights

- Renders `.html` templates with Jinja2; path segments starting with `_` are ignored for HTML builds.
- Built-in Markdown helpers: include Markdown files via `markdown('path.md')` and render inline strings with the `|markdown` filter.
- Regex-driven asset copying (`--copy`) and exclusion rules (`--exclude`) applied to both renders and copies.
- Watch mode that rebuilds on change without starting an HTTP server.
- Live preview server powered by FastAPI + Uvicorn with watchfiles + SSE for instant reload hooks.
- Simple Cyclopts-based CLI; works on Python 3.10+.

## 🧰 Installation

```bash
pip install engrave
```

## 📘 CLI Usage

Engrave provides three commands:

- `engrave build` builds the site once.
- `engrave watch` rebuilds on change without starting an HTTP server.
- `engrave server` rebuilds on change and starts a local preview server.

Use `engrave --help` or `engrave <command> --help` for the installed CLI output.

### Parameter rules

- `--dir-src` and `--dir-dest` are required for all commands.
- `--copy`, `--exclude`, and `--watch-add` are repeatable regex options.
- `--copy` and `--exclude` are matched against normalized source-relative paths such as `assets/app.js` or `drafts/post.html`.
- `--exclude` is applied before build or copy rules.
- `.html` files are rendered, not copied, even if a `--copy` regex also matches them.
- `--watch-add` is matched against paths relative to the current working directory.

Example:

```bash
engrave build \
  --dir-src src-site \
  --dir-dest dist \
  --copy 'assets/.*\.(css|js|png)$' \
  --exclude 'drafts/.*'
```

### Build

Build the site once.

```bash
engrave build --dir-src src-site --dir-dest dist
```

### Watch

Build once, then rebuild when files change without starting FastAPI or Uvicorn.

```bash
engrave watch \
  --dir-src src-site \
  --dir-dest dist \
  --copy 'assets/.*\.(css|js)$' \
  --watch-add 'config/.*\.yaml$'
```

### Server

Build once, then start a local preview server and publish live reload events.

```bash
engrave server \
  --dir-src src-site \
  --dir-dest dist \
  --copy 'assets/.*\.(css|js|png)$' \
  --host 127.0.0.1 \
  --port 8000
```

Live reload hook:

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

## 👩‍💻 Development

### Build package artifacts

Build source and wheel distributions into `dist/`:

```bash
uv build
```

### Build docs

Install docs dependencies:

```bash
uv sync --group dev
```

Build the documentation site:

```bash
uv run mkdocs build
```

Preview docs locally with live reload:

```bash
uv run mkdocs serve
```

## 📄 License

MIT — see `LICENSE`.
