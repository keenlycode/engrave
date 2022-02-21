from pathlib import Path
import asyncio
import re
import shutil
import argparse
import traceback

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
    contextfunction,
    Markup,
    TemplateSyntaxError,
    UndefinedError,
)
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
            autoescape=select_autoescape(['html', 'xml']),
            enable_async=True,
            cache_size=0,
            optimized=False,
        )

        template.globals.update(markdown=markdown)
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.template = template.get_template


class Engrave:
    def __init__(self, src_dir: Path, dest_dir: Path, mode: str = 'dev'):
        src_dir = Path(src_dir)
        dest_dir = Path(dest_dir)
        if not src_dir.exists():
            raise Exception(f"Source directory not found -> '{src_dir}'")

        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.mode = mode
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
        try:
            await proc.communicate()
        except asyncio.CancelledError:
            proc.terminate()

    async def _render_html(self, src: Path, render_exception=False):
        src = src.relative_to(self.src_dir)
        html = ''
        try:
            html = await self.template(str(src)).render_async()
        except TemplateSyntaxError as exception:
            if self.mode == 'build':
                raise exception
            file = open(exception.filename, 'r')
            code = ''
            line_start = None
            for i, line in enumerate(file):
                if (exception.lineno - i+1) <= 10 or (i+1 - exception.lineno) >= 7:
                    if line_start is None:
                        line_start = i+1
                    code += line
            tb = traceback.format_exc(limit=10)
            html = await self.template('error.html').render_async(
                exception=exception,
                code=code,
                line_start=line_start,
                tb=tb,
            )
        except UndefinedError as exception:
            return

        dest = self.dest_dir.joinpath(str(src)).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest = open(dest, 'w')
        dest.write(html)
        dest.close()


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
                await self._render_html(p)
                print(f"template: {p.relative_to(self.src_dir)}")
        elif re.match('.*.html$', path.name):
            await self._render_html(path)
            print(f"template: {path.relative_to(self.src_dir)}")
        elif re.match('.*.html.*.md$', path.name):
            html_file_name = re.match('.*.html', path.name)[0]
            for p in path.parent.glob(html_file_name):
                await self._render_html(p)
                print(f"template: {path.relative_to(self.src_dir)}")

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

    def parse_args(self):
        self.args = self.parser.parse_args()


async def main():
    command = CommandParser()
    command.parse_args()
    if command.args.cmd == 'build':
        engrave = Engrave(command.args.src, command.args.dest, mode='build')
        await engrave.build()
    elif command.args.cmd == 'dev':
        engrave = Engrave(command.args.src, command.args.dest, mode='dev')
        await asyncio.create_task(engrave.dev())
        if command.args.server:
            addr, port = command.args.server.split(':')
            port = int(port)
            server_task = asyncio.create_task(engrave.run_server(addr, port))
            await server_task
    else:
        print(command.parser.print_help())


def app():
    # For calling from installation script generated by setup.py
    asyncio.run(main())
