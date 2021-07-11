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
        self.template = template.get_template


class Engrave:
    def __init__(self, src_dir: Path, dest_dir: Path):
        src_dir = Path(src_dir)
        dest_dir = Path(dest_dir)
        if not src_dir.exists():
            raise Exception(f"Source directory not found -> '{src_dir}'")

        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.template = Template(src_dir=src_dir, dest_dir=dest_dir).template

    async def build(self):
        for path in self.src_dir.glob('**/*'):
            path = Path(path)
            if re.match('^_.*.html$', path.name):
                continue
            await self._file_handler(path)
        print("\n✔ Build finished\n")

    async def dev(self):
        await self.build()
        await self._file_watch()

    async def run_server(self, addr="0.0.0.0", port=8000):
        proc = await asyncio.create_subprocess_shell(
            f"python -m http.server {port} --bind {addr} "
            f"--directory {self.dest_dir}"
        )
        await proc.communicate()

    def _build_html(self, path: Path):
        path = path.relative_to(self.src_dir)
        html = self.template(str(path)).render()
        dest = self.dest_dir.joinpath(str(path)).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest = open(dest, 'w')
        dest.write(html)


    async def _file_watch(self):
        print('Watching files ...')
        async for changes in awatch(self.src_dir):
            for change, path in changes:
                path = Path(path)
                await self._file_change_handler(change, path)

    async def _file_handler(self, path: Path):
        if path.is_dir():
            return
            
        # Handle HTML files
        elif re.match('^_.*.html$', path.name):
            print(f"template: {path.relative_to(self.src_dir)}")
            for p in path.parent.glob('**/[!_]*.html'):
                self._build_html(p)
                print(f"template: {p.relative_to(self.src_dir)}")
        elif re.match('.*.html$', path.name):
            self._build_html(path)
            print(f"template: {path.relative_to(self.src_dir)}")
        elif re.match('.*.html.*.md$', path.name):
            html_file_name = re.match('.*.html', path.name)[0]
            for p in path.parent.glob(html_file_name):
                self._build_html(p)
                print(f"template: {path.relative_to(self.src_dir)}")

        # Handle SASS
        elif re.match('(?!_).*.(scss|sass)$', path.name):
            print(path.name)
            dest = path.relative_to(self.src_dir).with_suffix('.css')
            dest = self.dest_dir.joinpath(dest)
            proc = await asyncio.create_subprocess_shell(
                f"npx sass {path} {dest}")
            await proc.communicate()
            print(f"sass {path.relative_to(self.src_dir)}")
        elif re.match('^_.*.(scss|sass)$', path.name):
            return

        # Handle Javascript ES5 and Typescript
        elif re.match('.*.(js|ts)$', path.name):
            print(path.name)
            dest_dir = path.relative_to(self.src_dir).parent
            dest_dir = self.dest_dir.joinpath(dest_dir)
            proc = await asyncio.create_subprocess_shell(
                f"npx parcel build {path} --dist-dir {dest_dir}")
            await proc.communicate()

        # Handle static files
        else:
            dest = path.relative_to(self.src_dir)
            dest = self.dest_dir.joinpath(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"copy {path} -> {dest}")
            shutil.copy(path, dest)

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


class CommandParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="engrave",
            description='Static website generator')

        self.sub_parser = self.parser.add_subparsers(dest='cmd')
        self.make_setup_parser()
        self.make_build_parser()
        self.make_dev_parser()

    def make_build_parser(self):
        parser = self.sub_parser.add_parser('build', help='Build html')
        parser.add_argument('src', help='Source directory')
        parser.add_argument('dest', help='Destination directory')

    def make_dev_parser(self):
        parser = self.sub_parser.add_parser(
            'dev',
            help='Build html and watch for changes')
        parser.add_argument(
            '--server',
            nargs='?',
            const='0.0.0.0:8000',
            default=None,
            metavar='addr:port',
            help=(
                "set development http server address and port, "
                "default to 0.0.0.0:8000"
            )
        )
        parser.add_argument('src', help='Source directory')
        parser.add_argument('dest', help='Destination directory')

    def make_setup_parser(self):
        self.sub_parser.add_parser(
            'setup',
            help='Install required libraries from npm',
        )

    def parse_args(self):
        self.args = self.parser.parse_args()


async def main():
    command = CommandParser()
    command.parse_args()
    if command.args.cmd == 'setup':
        proc = await asyncio.create_subprocess_shell(
            'npm install parcel@next sass packet-ui')
        await proc.communicate()
    if command.args.cmd == 'build':
        builder = Engrave(command.args.src, command.args.dest)
        await builder.build()
    elif command.args.cmd == 'dev':
        builder = Engrave(command.args.src, command.args.dest)
        dev_task = asyncio.create_task(builder.dev())
        if command.args.server:
            addr, port = command.args.server.split(':')
            port = int(port)
            server_task = asyncio.create_task(builder.run_server(addr, port))
            await server_task
        await dev_task
    else:
        print(command.parser.print_help())


def app():
    # For calling from installation script generated by setup.py
    asyncio.run(main())
