# Templates + Markdown

Engrave is built around regular Jinja2 templates. If you already know Jinja,
the workflow will feel familiar.

## Build pages from templates

Write `.html` templates under your source directory and render them into a
static output directory with `engrave build`.

```html
{% extends "base.html" %}
{% block content %}
  <h1>About</h1>
{% endblock %}
```

Use Jinja features such as:

- template inheritance
- includes
- variables and control flow
- shared base layouts

Engrave only renders `.html` files as pages. If any part of the file path
starts with `_`, that file is automatically skipped as standalone output. This
makes `_partials/header.html` or `_layouts/base.html` a simple way to keep
reusable templates out of the final site while still including them from other
templates.

## Pull Markdown into templates

Engrave includes a `markdown()` helper for loading Markdown files inside a
template:

```html
<article>
  {{ markdown("includes/intro.md") }}
</article>
```

You can also convert inline Markdown with the `markdown` filter:

```html
<p>{{ "This is **inline** markdown." | markdown }}</p>
```

Markdown files loaded with `markdown()` are rendered with the current Jinja
context before they are converted to HTML. That means template variables from
the page can be used inside the Markdown file too.

## Keep the structure simple

- store page templates in your source directory
- keep reusable fragments in partials or includes
- keep assets alongside the site and copy them as part of your build workflow

For template and CLI details, use the built-in help and the project source as
the source of truth.
