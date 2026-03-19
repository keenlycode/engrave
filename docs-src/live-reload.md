# Live Reload

`engrave server` is the fastest way to work on a site locally. It builds your
project, serves it, and emits change events that can be used for browser
refresh.

## Start the preview server

```bash
engrave server site build
```

This is enough for most local development.

## Reload the browser on change

The preview server exposes an SSE endpoint at `/__engrave/watch` by default.
You can connect to it with a small script:

```html
<script>
  const source = new EventSource("/__engrave/watch");
  source.addEventListener("change", () => window.location.reload());
</script>
```

For exact server options and custom paths, use `engrave server --help`.
