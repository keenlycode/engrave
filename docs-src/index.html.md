<h1>Engrave</h1> <el-badge>Ver. 2.1.1</el-badge>

Engrave is a tool to generate static website.

## Features
- Write contents in HTML and Markdown.
- HTML template with Jinja2
- <el-badge>new in V2.1.0</el-badge> : Use `--asset=<RegEx>` to watch and copy asset files.  
  If `<RegEx>` is not provided, default to: `.*.(apng|avif|gif|jpg|png|svg|webp|ttf|otf|woff|woff2|eot|mp4|webm|3gp|ogg)`

## Changes from Ver. 1.x.x
- Now `engrave` only handle html files. Due to the release of
  `parcel v2.0` which cover many features for other files.
- Render error for debugging.

## Installation
```bash
$ pip install engrave
```

## Usage
```bash
$ engrave -h
usage: engrave [-h] {build,dev} ...

Static website generator

positional arguments:
  {build,dev}
    build            Build html
    dev              Build html and watch for changes
```

## Example
This document is made by **Engrave** and it's a good example how engrave works.
See document's source code at
[](https://github.com/nitipit/engrave/tree/main/docs-src)

To build this document and run development server, use command below

```bash
$ git clone https://github.com/nitipit/engrave.git
$ cd engrave
$ npm install # Install Node Libraries
$ engrave dev docs-src docs --server
```