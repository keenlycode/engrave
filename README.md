# Engrave

Engrave is a lightweight static-site generator built with Python and Jinja2.
It is designed for small documentation sites, landing pages, and simple
content-driven sites that benefit from templating without adding a backend.

## Installation

```bash
pip install engrave
```

## CLI overview

Top-level usage:

```bash
engrave <command>
```

Core commands:

- `engrave build` builds the site once
- `engrave watch` builds once, then rebuilds when files change
- `engrave server` builds once, then starts a local preview server with watch events

Use `engrave --help` or `engrave <command> --help` for full command details.

Build once:

```bash
engrave build site build --copy 'assets/.*'
```

Watch and rebuild:

```bash
engrave watch site build --copy 'assets/.*'
```

Run the preview server:

```bash
engrave server site build --copy 'assets/.*'
```

HTML files are rendered automatically. Non-HTML assets such as CSS, JS, images,
and fonts are only copied when their source-relative paths match one or more
`--copy` regex patterns.

## Testing

```bash
python -m unittest
```

## Development

Build package artifacts:

```bash
uv build
```

Build docs:

```bash
uv sync --group dev
uv run mkdocs build
```

Preview docs locally:

```bash
uv run mkdocs serve
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

MIT. See `LICENSE`.
