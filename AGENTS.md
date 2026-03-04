- Write Python docstrings in NumPy format.
- Write CLI help for Cyclopts using short command docstrings and parameter help on parameters.
- Keep command help high-level. Put detailed option semantics in parameter help.
- Use reStructuredText for Cyclopts command help when formatting is needed.

## Docs

- Keep README and docs under `docs-src/` aligned with the actual CLI behavior.
- Treat `docs-src/` as the source for MkDocs pages.
- Keep `mkdocs.yml` navigation labels aligned with actual page titles in `docs-src/`.
- Prefer simple, benefit-focused docs pages; leave detailed CLI option semantics to `engrave --help`.
- When docs change, verify with `uv run mkdocs build` or `uv run mkdocs serve` when appropriate.
