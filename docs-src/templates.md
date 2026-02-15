# Templates + Markdown

Engrave renders Jinja2 templates discovered under your source directory. Use standard Jinja features plus a built-in Markdown helper/filter.

## Rendering rules
- Only `.html` files are rendered. A template is skipped if any path segment starts with `_` (e.g., `_partials/header.html`), but it can still be included by other templates.
- The relative path under `DIR_SRC` is preserved in `DIR_DEST` (e.g., `pages/about/index.html` stays nested).
- Jinja loads templates relative to `DIR_SRC` (or a list of template roots if you pass more than one), so `{% extends "base.html" %}` or `{% include "partials/nav.html" %}` work as usual.

## Bringing in Markdown files
Use the global `markdown()` helper inside templates to load and render a Markdown file relative to the current template.

```html title="HTML"
<article>
  {{ markdown('includes/intro.md') }}
</article>
```

Details:
- Markdown files are rendered as Jinja templates first (using the current context), then converted to HTML, so you can use template variables in your `.md` snippets.
- Paths must be relative to the template; absolute paths raise an error and attempts to escape outside the configured loader roots are blocked.
- Lookups walk the loader search paths (handy when you pass multiple template roots) and fall back with a `FileNotFoundError` if the file is missing.
- File reads and compilation are cached per modification time, but Markdown content is re-rendered for each request so context changes are reflected.

## Inline Markdown filter
Convert inline strings to HTML with the `markdown` filter. Results are cached with an LRU to avoid repeated parsing.

```html title="HTML"
<p>{{ "This text **is** inline markdown." | markdown }}</p>
```

## Organizing partials and assets
- Keep non-page templates under `_partials/` or any `_`-prefixed folder to prevent standalone rendering (copy rules still apply to those paths).
- Store reusable Markdown snippets in `includes/` (or any folder) and pull them into pages with `markdown()`.
- Pair your templates with asset copy rules (`--copy '.*\\.(css|js|svg)$'`) so builds place files alongside rendered HTML.
