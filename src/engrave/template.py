# Built-in lib
from collections.abc import Callable
from pathlib import Path

import jinja2  # type: ignore
import mistune  # type: ignore
from markupsafe import Markup


def _markdown_to_html(text: str) -> str:
    return mistune.html(text)

class Template:

    markdown_to_html: Callable[[str], str] = mistune.html

    def __init__(
                self,
                *,
                src_dir: Path,
                dest_dir: Path,
                markdown_to_html: Callable[[str], str] | None = None,
                jinja_env: jinja2.Environment | None = None,
        ):

        if markdown_to_html:
            self.markdown_to_html = markdown_to_html

        @jinja2.pass_context
        def _markdown(ctx, path: str | Path) -> str:
            path = src_dir.joinpath(ctx.name).parent.joinpath(path)
            text: str = open(path, 'r').read()
            return Markup(self.markdown_to_html(text))

        template = jinja2.Environment(
            loader=jinja2.FileSystemLoader(src_dir),
            enable_async=True,
            cache_size=0,
            optimized=False,
        )

        template.globals.update(markdown=_markdown)

        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.template = template.get_template
