from pathlib import Path
import asyncio
import re
import shutil
import argparse
from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
    contextfunction,
    Markup)
import mistune
from watchgod import awatch, Change


class Template:
    def __init__(self, src_dir: Path, dest_dir: Path):

        @contextfunction
        def markdown(ctx, path: str):
            html = src_dir.joinpath(ctx.name).parent.joinpath(path)
            html = mistune.html(open(html, 'r').read())
            return Markup(html)

        template = Environment(
            loader=FileSystemLoader(src_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        template.globals.update(markdown=markdown)
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.get = template.get_template

    def build(self, path: Path):
        if re.match('(?!_).*.html$', path.name):
            self._to_html(path)
            print(f"template: {path.relative_to(self.src_dir)}")
        elif re.match('^_.*.html$', path.name):
            print(f"template {path.relative_to(self.src_dir)}")
            for p in path.parent.glob('**/[!_]*.html'):
                self._to_html(p)
                print(f"template: {p.relative_to(self.src_dir)}")

    def _to_html(self, path: Path):
        path = path.relative_to(self.src_dir)
        html = self.get(str(path)).render()
        dest = self.dest_dir.joinpath(str(path)).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest = open(dest, 'w')
        dest.write(html)


class Pillari:
    def __init__(self, src_dir: Path, dest_dir: Path):
        src_dir = Path(src_dir)
        dest_dir = Path(dest_dir)
        if not src_dir.exists():
            raise Exception(f"Source directory not found -> '{src_dir}'")

        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.template = Template(src_dir=src_dir, dest_dir=dest_dir)
        self.http_server = None

    async def build(self):
        for path in self.src_dir.glob('**/*'):
            if re.match('^_.*.html$', path.name):
                continue
            if re.match('.*.md$', path.name):
                continue
            path = Path(path)
            await self._file_handler(path)

    async def dev(self, addr="0.0.0.0", port=8000):
        await self.build()
        await asyncio.gather(
            self._file_watch(),
            self._run_http_server(addr, port))

    async def _run_http_server(self, addr="0.0.0.0", port=8000):
        proc = await asyncio.create_subprocess_shell(
            f"python -m http.server {port} --bind {addr} "
            f"--directory {self.dest_dir}"
        )
        self.http_server = proc
        await proc.communicate()

    async def _file_watch(self):
        async for changes in awatch(self.src_dir):
            for change, path in changes:
                path = Path(path)
                await self._file_change_handler(change, path)

    async def _file_handler(self, path: Path):
        if re.match('.*.html$', path.name):
            self.template.build(path)
        elif re.match('(?!_).*.(scss|sass)$', path.name):
            dest = path.relative_to(self.src_dir).with_suffix('.css')
            dest = self.dest_dir.joinpath(dest)
            proc = await asyncio.create_subprocess_shell(
                f"npx sass {path} {dest}")
            await proc.communicate()
            print(f"sass {path.relative_to(self.src_dir)}")
        elif re.match('(?!_).*.(js)$', path.name):
            proc = await asyncio.create_subprocess_shell(
                f"npx parcel build {path} --dist-dir {self.dest_dir}")
            await proc.communicate()
        elif re.match('.*.(jpg|png|svg|ttf|otf|woff)$', path.name):
            dest = path.relative_to(self.src_dir).with_suffix(path.suffix)
            dest = self.dest_dir.joinpath(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(path, dest)
            print(f"copy {path} -> {dest}")
        elif re.match('.*.md$', path.name):
            html_file_name = re.match('.*.html', path.name)[0]
            for p in path.parent.glob(html_file_name):
                self.template.build(p)

    async def _file_change_handler(self, change, path: Path):
        if change == Change.deleted:
            path = path.relative_to(self.src_dir)
            path = self.dest_dir.joinpath(path)
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
            print(f"delete: {path.relative_to(self.dest_dir)}")
        if (change == Change.added or
                change == Change.modified):
            await self._file_handler(path)


async def main():
    proc = await asyncio.create_subprocess_shell(
        'npx --version',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if stderr:
        error = f"{stderr.decode('utf-8')}"
        error += "Please install NodeJS -> https://nodejs.org"
        raise Exception(error)

    parser = argparse.ArgumentParser(
        prog="pillari",
        description='Static HTML Generator')
    parser.add_argument(
        '--dev', default=False, action="store_true",
        help='Use develepment mode')
    parser.add_argument(
        'src', help='Source directory')
    parser.add_argument(
        'dest', help='Destination directory')
    args = parser.parse_args()
    pillari = Pillari(args.src, args.dest)

    if args.dev is False:
        await pillari.build()
    elif args.dev is True:
        try:
            await pillari.dev()
        except Exception:
            if pillari.http_server:
                pillari.http_server.terminate()
            raise


def run():
    asyncio.run(main())
