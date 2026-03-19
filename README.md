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
engrave build site build
```

Watch and rebuild:

```bash
engrave watch site build
```

Run the preview server:

```bash
engrave server site build
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
./scripts/mike-release.sh 3.2.4 latest
```

For versioned docs deployment, use Mike commands above instead of running
`mkdocs build` or `mkdocs serve` directly.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## License

MIT. See `LICENSE`.
