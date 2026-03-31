"""Jinja template loading with Markdown helpers for one source root.

The public ``get_template()`` helper keeps the existing ergonomic API while an
internal ``TemplateEngine`` class owns the render-time state used for template
loading, Markdown resolution, and optional Markdown dependency recording.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import jinja2  # type: ignore
import mistune  # type: ignore
from markupsafe import Markup


@dataclass(frozen=True)
class RenderDependencies:
    """Dependencies discovered while rendering one public HTML page."""

    markdown_paths: set[Path]
    template_paths: set[Path]


class TrackingLoader(jinja2.BaseLoader):
    """File-system loader wrapper that records resolved template dependencies."""

    def __init__(
        self,
        *,
        dir_src: Path,
        template_dependency_collector: Callable[[Path], None] | None = None,
    ) -> None:
        self.dir_src = dir_src.resolve()
        self.template_dependency_collector = template_dependency_collector
        self.loader = jinja2.FileSystemLoader(str(dir_src))

    def get_source(self, environment, template):
        source, filename, uptodate = self.loader.get_source(environment, template)

        if self.template_dependency_collector is not None:
            path_template = Path(filename).resolve().relative_to(self.dir_src)
            self.template_dependency_collector(path_template)

        return source, filename, uptodate

    def list_templates(self):
        """Delegate template listing to the wrapped file-system loader."""
        return self.loader.list_templates()


class TemplateEngine:
    """Stateful template environment for one source root."""

    def __init__(
        self,
        *args,
        dir_src: str | Path,
        markdown_to_html: Callable[[str], str] | None = None,
        markdown_dependency_collector: Callable[[Path], None] | None = None,
        template_dependency_collector: Callable[[Path], None] | None = None,
        **kw,
    ) -> None:
        self.dir_src = Path(dir_src)
        self.dir_src_resolved = self.dir_src.resolve()
        if markdown_to_html is None:
            markdown_to_html = mistune.html  # type: ignore
        self.markdown_to_html = cast(Callable[[str], str], markdown_to_html)
        self.markdown_dependency_collector = markdown_dependency_collector
        self.template_dependency_collector = template_dependency_collector
        self.template_env = jinja2.Environment(
            *args,
            **kw,
            loader=TrackingLoader(
                dir_src=self.dir_src,
                template_dependency_collector=template_dependency_collector,
            ),
        )
        self.template_env.globals.update(markdown=self.markdown)
        self.template_env.filters["markdown"] = self.markdown_inline

    def get_template(self, name: str) -> jinja2.Template:
        """Return a template by name from the configured environment."""
        return self.template_env.get_template(name)

    def is_child_path(self, root: Path, child: Path) -> bool:
        """Return whether ``child`` stays under ``root``."""
        try:
            child.relative_to(root)
            return True
        except Exception:
            return False

    def resolve_markdown_path(self, ctx, req_path: Path) -> Path | None:
        """Resolve a Markdown include relative to the current template."""
        base_dir = (self.dir_src_resolved / Path(ctx.name)).parent
        candidate = (base_dir / req_path).resolve()
        if self.is_child_path(self.dir_src_resolved, candidate) and candidate.is_file():
            return candidate
        return None

    def markdown_inline(self, text: str) -> Markup:
        """Render inline Markdown text to safe HTML."""
        return Markup(self.markdown_to_html(text))

    @jinja2.pass_context
    def markdown(self, ctx, path: str | Path) -> Markup:
        """Load and render a Markdown file relative to the current template.

        Parameters
        ----------
        ctx : jinja2.runtime.Context
            Jinja2 rendering context (injected via ``@pass_context``).
        path : str or pathlib.Path
            Relative path to a Markdown file, resolved against the directory of
            the currently rendering template.

        Returns
        -------
        markupsafe.Markup
            Safe HTML produced from the Markdown file.

        Raises
        ------
        ValueError
            If an absolute path is provided.
        FileNotFoundError
            If the file cannot be found within ``dir_src``.
        RuntimeError
            If reading or rendering the Markdown file fails.
        """
        path = Path(path)
        if path.is_absolute():
            raise ValueError(f"Absolute paths are not allowed in markdown(): {path}")

        path_markdown = self.resolve_markdown_path(ctx, path)
        if path_markdown is None:
            raise FileNotFoundError("Markdown file not found or outside allowed roots")

        if self.markdown_dependency_collector is not None:
            self.markdown_dependency_collector(
                path_markdown.relative_to(self.dir_src_resolved)
            )

        try:
            text = path_markdown.read_text(encoding="utf-8")
            md_template = self.template_env.from_string(text)
            rendered = md_template.render(**ctx.get_all())
            return Markup(self.markdown_to_html(rendered))
        except Exception as error:
            raise RuntimeError(
                f"Error processing markdown file {path_markdown}: {error}"
            ) from error


def get_template(
    *args,
    dir_src: str | Path,
    markdown_to_html: Callable[[str], str] | None = None,
    markdown_dependency_collector: Callable[[Path], None] | None = None,
    template_dependency_collector: Callable[[Path], None] | None = None,
    **kw,
) -> Callable[[str], jinja2.Template]:
    """Create a Jinja2 environment with Markdown support.

    Parameters
    ----------
    dir_src : str or pathlib.Path
        Root directory containing template files and Markdown includes.
    markdown_to_html : callable, optional
        Function that converts Markdown text to HTML. Defaults to
        ``mistune.html`` when omitted.
    markdown_dependency_collector : callable, optional
        Callback invoked with each source-relative Markdown path used while
        rendering a template.
    template_dependency_collector : callable, optional
        Callback invoked with each source-relative Jinja template path loaded
        while rendering a template.
    *args
        Additional positional arguments forwarded to ``jinja2.Environment``.
    **kw
        Additional keyword arguments forwarded to ``jinja2.Environment``.

    Returns
    -------
    collections.abc.Callable
        The bound ``TemplateEngine.get_template`` method for loading templates by
        name.
    """
    return TemplateEngine(
        dir_src=dir_src,
        markdown_to_html=markdown_to_html,
        markdown_dependency_collector=markdown_dependency_collector,
        template_dependency_collector=template_dependency_collector,
        *args,
        **kw,
    ).get_template
