# Live Preview

`engrave server` runs a FastAPI dev server that rebuilds on change and streams file-change events for client-side reloads.

## Starting the server
```bash
engrave server site/ build/ \
  --copy '.*\.(css|png|svg)$' \
  --watch 'build/.*\.(js)$' \
  --exclude 'drafts/.*' \
  --host 127.0.0.1 --port 8000 \
  --sse-url '__engrave/watch'
```
- Performs an initial build, then watches `.html`/`.md` plus any `--copy` targets. `--watch` adds extra regexes matched against your current working directory; these emit SSE events only (they do not trigger builds or copies).
- `--copy` and `--exclude` are regular expressions evaluated against path strings under `site/`; avoid copy patterns that include `.html` to prevent double work.
- Serves `.html` by rendering directly from `site/` (exceptions fall back to the bundled error template) and serves other requests from `build/`.
- Leave out `--watch` if you only care about the source tree. Adjust `--sse-url` if you want the SSE endpoint mounted elsewhere.

## Hooking up reloads
The server exposes an SSE endpoint (default `/__engrave/watch`) that streams JSON lists of file changes. Wire it into your pages with a tiny script:

```html
<script>
  const source = new EventSource('/__engrave/watch'); // match your --sse-url
  source.addEventListener('change', event => {
    const changes = JSON.parse(event.data);
    // Decide how to handle changes; simplest is a full reload.
    window.location.reload();
  });
</script>
```

## What triggers events
- HTML templates: rendered on added/modified; deleted files remove their counterpart in `DIR_DEST` and emit `{type: "html"}`.
- Markdown files: reported as `{type: "markdown"}` so you can reload clients; they are not auto-rendered unless a template pulls them in.
- Copy targets: copied on added/modified and removed on delete with `{type: "copy"}`.
- Extra watch targets: anything matching `--watch` regex patterns relative to the current working directory, emitted as `{type: "watch"}` events for your own handling.
