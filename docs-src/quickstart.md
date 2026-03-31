# Quickstart

This guide walks through the smallest useful Engrave setup: a template, a
Markdown snippet, and a local build.

## Install

```bash
pip install engrave
```

## Create a simple site

One possible layout:

```text
site/
  base.html
  index.html
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
      {{ markdown("includes/intro.md") }}
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
  <p>This page is rendered by Engrave.</p>
{% endblock %}
```

Example `includes/intro.md`:

```markdown
## Engrave

This text comes from a Markdown file included inside a template.
```

## Build the site

```bash
engrave build site build --copy 'assets/.*'
```

This renders your templates into `build/`. For more advanced options, check the
CLI help with `engrave build --help`.

`assets/site.css` is copied because it matches the `--copy 'assets/.*'` rule.
Engrave always renders HTML templates, but non-HTML assets are only copied when
they match at least one `--copy` regex.

## Preview while you work

```bash
engrave server site build --copy 'assets/.*'
```

This gives you a local preview server while you edit templates and content.
When you only want rebuilds without serving HTTP, use `engrave watch` instead.
