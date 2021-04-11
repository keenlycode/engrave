Engrave is a tool to generate static website.

## Features
- Write contents in HTML and Markdown.
- Style sheet (CSS) with SASS
- HTML template with Jinja

## Requirement

[NodeJS](https://nodejs.org/en/) v14.16 or later

## Installation
```bash
$ pip install engrave
```

## Usage
```
$ engrave -h
usage: engrave [-h] {setup,build,dev} ...

Static website generator

positional arguments:
  {setup,build,dev}
    setup            Install required libraries from npm: parcel, sass
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