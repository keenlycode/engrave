# Engrave Guide

Ship template-driven static sites faster with Engrave.

Engrave is a lightweight static-site generator built on Python and Jinja2 for developers who want full control without backend complexity. Build from familiar templates, preview changes quickly, and deploy static output anywhere.

## Why Engrave
- Build with tools you already know: use standard Jinja2 templates for layouts, includes, and reusable page structure.
- Keep your pipeline explicit: render `.html`, copy matching assets, and apply regex-based excludes with predictable behavior.
- Move faster during development: run `engrave server` for initial build, file watching, and SSE-driven live reload hooks.
- Deploy without friction: generated output is plain static files, ready for simple hosting workflows.

## Start Here
- [Quickstart](quickstart.md): go from empty folder to running site in minutes.
- [CLI Reference](cli.md): master `engrave build` and `engrave server` options, including copy/exclude/watch-add controls.
- [Templates + Markdown](templates.md): compose pages with Jinja templates and Markdown helpers.
- [Live Reload](live-reload.md): wire SSE events into browser refresh or your own dev workflow.
