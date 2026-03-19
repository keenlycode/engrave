# CLI Overview

Engrave keeps the command line small on purpose. Most people only need three
commands:

- `engrave build` for one-off builds
- `engrave watch` for rebuild-on-save workflows
- `engrave server` for local preview during development

## Choose the right command

### `engrave build`

Use this when you want static output written to a destination directory.

```bash
engrave build site build
```

### `engrave watch`

Use this when you want Engrave to keep rebuilding in the background without
starting a local web server.

```bash
engrave watch site build
```

### `engrave server`

Use this when you want a local preview server alongside automatic rebuilds.

```bash
engrave server site build
```

## Need the full CLI?

The docs stay intentionally short. For the exact options available in your
installed version, use:

```bash
engrave --help
engrave build --help
engrave watch --help
engrave server --help
```
