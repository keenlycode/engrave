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

Install docs tooling:

```bash
uv sync --group dev
```

`mike` depends on `mkdocs` under the hood, so keep both installed.

Preview versioned docs locally:

```bash
uv run mike serve -b docs
```

Deploy versioned docs to the `docs` branch:

```bash
./scripts/mike-release.sh
```

Deploy a specific version and alias:

```bash
./scripts/mike-release.sh 3.2.2 latest
```

For versioned docs deployment, use Mike commands above instead of running
`mkdocs build` or `mkdocs serve` directly.

## License

MIT. See `LICENSE`.
