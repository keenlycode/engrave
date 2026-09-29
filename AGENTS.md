- Write Python docstrings in NumPy format.
- Write CLI help for Cyclopts using short command docstrings and parameter help on parameters.
- Keep command help high-level. Put detailed option semantics in parameter help.
- Use reStructuredText for Cyclopts command help when formatting is needed.

## Docs

- Keep README and docs under `docs-src/` aligned with the actual CLI behavior.
- Treat `docs-src/` as the source for Zensical pages; keep the compatible `mkdocs.yml` configuration for Mike versioning.
- Keep `mkdocs.yml` navigation labels aligned with actual page titles in `docs-src/`.
- Prefer simple, benefit-focused docs pages; leave detailed CLI option semantics to `engrave --help`.
- When docs change, verify with `uv run zensical build` or `uv run zensical serve` when appropriate.
- Versioned GitHub Pages docs are published to the `docs` branch with the pinned Zensical-compatible Mike fork. Publishing requires explicit authorization.
