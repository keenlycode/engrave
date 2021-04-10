## Description
Engrave is a tool to generate static website.

## Installation
```bash
$ pip install engrave
```

## Usage
```
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
This documents is a good example about generating static website.
Documents source code is at 
```bash
# Install required libraries from npm.
$ engrave setup
$
```