# CLI Reference

Engrave provides three commands:

- `engrave build` builds the site once
- `engrave watch` rebuilds on change without serving HTTP
- `engrave server` rebuilds on change and starts a local preview server

Use `engrave --help` or `engrave <command> --help` to inspect the exact CLI for your installed version.

## Parameter rules

Engrave uses named options:

```bash
engrave build --dir-src src-site --dir-dest dist
```

General rules:

- `--dir-src` and `--dir-dest` are required for every command.
- `--copy`, `--exclude`, and `--watch-add` are repeatable regex options.
- `--copy` and `--exclude` are matched against normalized source-relative paths such as `assets/app.js` or `drafts/post.html`.
- `--exclude` is applied before build or copy rules.
- `.html` files are rendered instead of copied, even if a `--copy` regex matches them.
- `--watch-add` is matched against paths relative to the current working directory.

Example:

```bash
engrave build \
  --dir-src src-site \
  --dir-dest dist \
  --copy 'assets/.*\.(css|js|png)$' \
  --exclude 'drafts/.*'
```

## engrave build

Build the site once.

Behavior:

- renders `.html` files that do not have any path segment starting with `_`
- copies non-HTML files selected by `--copy`
- skips any path matched by `--exclude`

Examples:

```bash
engrave build --dir-src src-site --dir-dest dist
```

```bash
engrave build \
  --dir-src src-site \
  --dir-dest dist \
  --copy 'assets/.*\.(css|js|png|svg|ttf)$'
```

## engrave watch

Build once, then rebuild when files change.

This command does not start an HTTP server.

Examples:

```bash
engrave watch --dir-src src-site --dir-dest dist
```

```bash
engrave watch \
  --dir-src src-site \
  --dir-dest dist \
  --copy 'assets/.*\.(css|js)$' \
  --watch-add 'config/.*\.yaml$'
```

## engrave server

Build once, start a local preview server, then rebuild and emit live reload events when files change.

Examples:

```bash
engrave server --dir-src src-site --dir-dest dist
```

```bash
engrave server \
  --dir-src src-site \
  --dir-dest dist \
  --copy 'assets/.*\.(css|js|png)$' \
  --host 127.0.0.1 \
  --port 8000 \
  --sse-url /__engrave/watch
```

Live reload example:

```js
const source = new EventSource('/__engrave/watch');
source.addEventListener('change', () => window.location.reload());
```
