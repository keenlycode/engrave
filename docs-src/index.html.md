## Description
Engrave is a tool to generate static website.

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
    setup            Install required libraries from npm: parcel, sass, packet-ui
    build            Build html
    dev              Build html and run http server, also watch for changes

optional arguments:
  -h, --help         show this help message and exit
```

## Example
This document is made by **Engrave** and it's a good example how engrave works.
See document's source code at
[](https://github.com/nitipit/engrave/tree/main/docs-src)

To build this document, use command below

```bash
$ git clone https://github.com/nitipit/engrave.git
$ cd engrave
$ engrave dev docs-src docs --server
```