# Built-in lib
from collections.abc import Callable
from pathlib import Path
from typing import cast

import jinja2  # type: ignore
import mistune  # type: ignore
from markupsafe import Markup


def get_template(
        *args,
        src_dir: str | Path,
        markdown_to_html: Callable[[str], str] | None = None,
        **kw,
):
    """
    Creates a Jinja2 environment with markdown parsing capabilities.

    Args:
        src_dir: Directory containing template files
        markdown_to_html: Optional custom markdown parser function
        *args, **kw: Additional arguments passed to jinja2.Environment

    Returns:
        A configured Jinja2 environment with markdown support
    """
    # Use mistune as default markdown parser if none provided
    if not markdown_to_html:
        markdown_to_html = mistune.html  # type: ignore
    markdown_to_html = cast(Callable[[str], str], markdown_to_html)

    @jinja2.pass_context
    def _markdown(ctx, path: str | Path) -> str:
        """
        Jinja2 filter/function to load and parse markdown files

        Usage in template: {{ markdown('path/to/file.md') }}
        """
        _path: Path | None = None
        for search_dir in ctx.environment.loader.searchpath:
            search_dir = Path(search_dir)
            _path = search_dir.joinpath(ctx.name).parent.joinpath(path)
            if _path.exists():
                break

        if not _path:
            raise Exception(f'Markdown file not found: {path}')

        text: str = open(_path, "r").read()
        return Markup(markdown_to_html(text))

    # Create Jinja2 environment with file system loader
    template_env = jinja2.Environment(*args, **kw, loader=jinja2.FileSystemLoader(src_dir))

    # Register markdown function in template environment
    template_env.globals.update(markdown=_markdown)

    # You can also use it as a filter if needed: {{ content|markdown_filter }}
    template_env.filters['markdown'] = lambda text: Markup(markdown_to_html(text))

    return template_env
