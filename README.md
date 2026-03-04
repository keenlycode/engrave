# Engrave

Engrave is a lightweight static-site generator built with Python and Jinja2.
It is designed for small documentation sites, landing pages, and simple
content-driven sites that benefit from templating without adding a backend.

## Installation

```bash
pip install engrave
```

## Simple CLI usage

Engrave has three core commands:

- `engrave build` renders a site once
- `engrave watch` rebuilds on change
- `engrave server` rebuilds on change and starts a local preview server

Use `engrave --help` or `engrave <command> --help` for full command details.

Build once:

```bash
engrave build --dir-src site --dir-dest build
```

Watch and rebuild:

```bash
engrave watch --dir-src site --dir-dest build
```

Run the preview server:

```bash
engrave server --dir-src site --dir-dest build
```

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

## License

MIT. See `LICENSE`.
