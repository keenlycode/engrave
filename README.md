<h1>Engrave</h1> <el-badge>Ver. 2.0.5</el-badge>

Engrave is a tool to generate static website.

## Features
- Write contents in HTML and Markdown.
- HTML template with Jinja2

## Changes from Ver. 1.x.x
- Now `engrave` only handle html files. Due to the release of
  `parcel v2.0` which cover many features for other files.

## Installation
```bash
$ pip install engrave
```

## Usage
```
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