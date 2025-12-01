# Built-in lib
from collections.abc import Callable
from pathlib import Path
from typing import (
    cast,
    List,
    Union,
)

import jinja2  # type: ignore
import mistune  # type: ignore
from markupsafe import Markup
from functools import lru_cache


TYPE_DIR_SRC = Union[str, Path, List[Union[str, Path]]]

# Tunable cache size for inline Markdown filter
INLINE_MARKDOWN_CACHE_SIZE = 256


def get_template(
        *args,
        dir_src: TYPE_DIR_SRC,
        markdown_to_html: Callable[[str], str] | None = None,
        **kw,
):
    """
    Create a Jinja2 environment with Markdown support and return its template loader.

    Parameters
    ----------
    dir_src : str or pathlib.Path or list of (str or pathlib.Path)
        Directory or directories containing template files. Passed to
        ``jinja2.FileSystemLoader``.
    markdown_to_html : callable, optional
        Function that converts Markdown text (str) to HTML (str). Defaults to
        ``mistune.html`` if not provided.
    *args
        Additional positional arguments forwarded to ``jinja2.Environment``.
    **kw
        Additional keyword arguments forwarded to ``jinja2.Environment``.

    Returns
    -------
    callable
        The bound method ``Environment.get_template`` used to load templates by name.

    Notes
    -----
    - Registers a global ``markdown(path)`` helper for including and rendering
      Markdown files relative to the current template, with path traversal protection
      and on-disk caching keyed by file modification time.
    - Registers a ``markdown`` filter to convert inline Markdown strings to HTML
      with an LRU cache.
    """
    # Use mistune as default markdown parser if none provided
    if not markdown_to_html:
        markdown_to_html = mistune.html  # type: ignore
    markdown_to_html = cast(Callable[[str], str], markdown_to_html)

    # Normalize template directories to a list of Path objects
    def _normalize_dirs(dirs: TYPE_DIR_SRC) -> list[Path]:
        if isinstance(dirs, (str, Path)):
            return [Path(dirs)]
        return [Path(d) for d in dirs]

    list_dir_src = _normalize_dirs(dir_src)

    # Helper to ensure a path is within an allowed root
    def _is_child_path(root: Path, child: Path) -> bool:
        try:
            child.relative_to(root)
            return True
        except Exception:
            return False

    # Cache for file-based markdown rendering: path -> (mtime_ns, Markup)
    _file_cache: dict[Path, tuple[int, Markup]] = {}

    # Cached inline markdown filter
    @lru_cache(maxsize=INLINE_MARKDOWN_CACHE_SIZE)
    def _markdown_inline(text: str) -> Markup:
        return Markup(markdown_to_html(text))

    # Resolve a requested Markdown file path securely within loader roots
    def _resolve_markdown_path(ctx, req_path: Path) -> Path | None:
        # Resolve candidate relative to the current template's directory for each root
        for search_dir in ctx.environment.loader.searchpath:
            root = Path(search_dir).resolve()
            base_dir = (root / Path(ctx.name)).parent
            candidate = (base_dir / req_path).resolve()
            if _is_child_path(root, candidate) and candidate.is_file():
                return candidate
        return None


    @jinja2.pass_context
    def _markdown(ctx, path: str | Path) -> str:
        """
        Load and render a Markdown file relative to the current template.

        Parameters
        ----------
        ctx : jinja2.runtime.Context
            Jinja2 rendering context (injected via ``@pass_context``).
        path : str or pathlib.Path
            Relative path to a Markdown file, resolved against the directory of the
            currently rendering template.

        Returns
        -------
        str
            Safe HTML string (``Markup``) produced from the Markdown file.

        Raises
        ------
        ValueError
            If an absolute path is provided.
        FileNotFoundError
            If the file cannot be found within the allowed loader roots.
        Exception
            If reading or rendering the Markdown file fails.

        Notes
        -----
        - Resolution is restricted to the configured loader roots; attempts to escape
          via ``..`` are ignored.
        - Results are cached per file using modification time to avoid re-rendering
          unchanged files.

        Examples
        --------
        In a Jinja2 template::

            {{ markdown('includes/intro.md') }}
        """

        # Disallow absolute paths to prevent escaping the search roots
        path = Path(path)
        if path.is_absolute():
            raise ValueError(f'Absolute paths are not allowed in markdown(): {path}')

        # Resolve candidate relative to the current template's directory, staying within loader roots
        _path = _resolve_markdown_path(ctx, path)
        if not _path:
            raise FileNotFoundError(f'Markdown file not found or outside allowed roots: {_path}')
        path = _path

        try:
            mtime_ns = path.stat().st_mtime_ns
            cached = _file_cache.get(path)
            if cached and cached[0] == mtime_ns:
                return cached[1]

            text = path.read_text(encoding="utf-8")

            html = Markup(markdown_to_html(text))
            _file_cache[path] = (mtime_ns, html)
            return html
        except Exception as e:
            raise RuntimeError(f"Error processing markdown file {path}: {e}") from e

    # Create Jinja2 environment with file system loader
    template_env = jinja2.Environment(*args, **kw, loader=jinja2.FileSystemLoader(list_dir_src))

    # Register markdown function in template environment
    template_env.globals.update(markdown=_markdown)

    # You can also use it as a filter if needed: {{ content | markdown }}
    template_env.filters['markdown'] = _markdown_inline

    return template_env.get_template
