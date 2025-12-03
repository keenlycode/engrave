# Engrave

**A lightweight static-site generator using Python + Jinja2**
Version: 3.1.4

## 🚀 What is Engrave

Engrave is a static-site generator that transforms plain HTML or Markdown files into ready-to-deploy static websites using Jinja2 templating. It’s ideal for documentation sites, project landing pages, blogs, or any static content without server-side rendering.

## ✅ Why use Engrave / Use-cases

* Quickly build documentation sites, landing pages, or simple blogs without needing a database or backend
* Write content in HTML or Markdown and reuse templates/layouts easily
* Lightweight and easy to deploy (works well with GitHub Pages, Netlify, S3/static-hosting)
* Highly flexible via Jinja2 templates — layout, partials, includes

## 🌟 Features

* Supports HTML and Markdown as input
* Uses Jinja2 templates for layout and partials
* Simple CLI command for build and watch/rebuild workflow
* Clean project structure and Python packaging-ready

## 🧰 Installation

```bash
pip install engrave
```

## 🚀 Quick Start / Usage

## 📘 CLI Usage

### Build

Generate a static site from a source directory into the output directory.

```bash
engrave build <content_dir> <output_dir>
```

### Development Mode (Auto‑Rebuild + SSE)

Rebuilds automatically when files change. Can optionally run a preview server.

```bash
engrave server <content_dir> <output_dir> [--watch]

# Example: watch only Markdown + HTML files
engrave server docs/ build/ --watch ".*\.(md|html)$"
```

### CLI Help
`engrave -h`  
`engrave server -h`

```
Usage: engrave server [ARGS] [OPTIONS]

Start a development server with live preview.

╭─ Parameters ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  DIR-SRC --dir-src                  Source directory [required]                                                          │
│ *  DIR-DEST --dir-dest                Destination directory for build output [required]                                    │
│    COPY --copy --empty-copy           RegEx patterns based on dir_src for files/directories to copy verbatim [default: []] │
│    WATCH --watch --empty-watch        Additional paths to watch, expressed as regular expression patterns relative to the  │
│                                       current working directory. These are in addition to files under dir_src and any      │
│                                       paths matched by copy. Changes to matched paths will be streamed to web clients via  │
│                                       Server-Sent Events (SSE) to enable live preview/reload. [default: []]                │
│    EXCLUDE --exclude --empty-exclude  RegEx patterns to exclude from processing and watching [default: []]                 │
│    LOG --log                          [default: INFO]                                                                      │
│    HOST --host                        Host interface to bind the development server [default: 127.0.0.1]                   │
│    PORT --port                        Port number for the development server [default: 8000]                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 🛠️ Testing

To run all tests, use:

```bash
python -m unittest
```

## 📄 License

This project is licensed under the MIT License — see the LICENSE file.
