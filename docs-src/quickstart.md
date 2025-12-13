# Quickstart

Spin up a small Engrave site to see how HTML rendering, Markdown inclusion, and asset copying work together.

## 1) Install
```bash
pip install engrave
```

## 2) Create a source tree
Use any layout you like. Only `.html` files are rendered; any path segment starting with `_` is skipped for HTML output (handy for partials/includes). Markdown lives alongside templates and is pulled in from HTML.

```
site/
  base.html
  index.html
  about/index.html
  includes/intro.md
  assets/site.css
```

Example `base.html`:
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{{ title or "Engrave demo" }}</title>
    <link rel="stylesheet" href="/assets/site.css" />
  </head>
  <body>
    <main>
      {{ markdown('includes/intro.md') }}
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

Example `index.html`:
```html
{% extends "base.html" %}
{% set title = "Home" %}
{% block content %}
  <h1>Welcome</h1>
  <p>Edit this file and rebuild to see Engrave render it.</p>
{% endblock %}
```

`includes/intro.md`:
```markdown
## Engrave

This site is rendered from HTML templates. Markdown is pulled in on demand with
`{{ markdown("includes/intro.md") }}`.
```

## 3) Build once
```bash
engrave build site/ build/ --copy '.*\.(css|png|svg)$' --exclude 'drafts/.*'
```
- HTML under `site/` is rendered into `build/` (segments prefixed with `_` are skipped for HTML rendering).
- Assets matching the regex are copied verbatim; `--exclude` uses regex matching against the path string to skip both rendering and copying.
- Add `--log-level DEBUG` (or set `LOG_LEVEL`) if you want more verbose output.

## 4) Develop with live preview
```bash
engrave server site/ build/ --copy '.*\.(css|png|svg)$' --watch 'build/.*\.(html|css|png|svg|js)$'
```
- Engrave builds once, renders `.html` requests directly from `site/`, and copies matching assets into `build/`.
- Watches `.html` and `.md` under `site/` plus any copy targets. Add `--watch REGEX` for extra paths relative to your current working directory—these emit SSE events only (no auto-copy/build).
- Browse `http://127.0.0.1:8000/` and add the reload snippet from [Live Preview](live-preview.md) for auto-refresh via SSE (default endpoint `/__engrave/watch`).
