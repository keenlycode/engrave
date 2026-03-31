"""In-memory dependency indexing for incremental watch rebuilds."""

from pathlib import Path

from ..template import RenderDependencies


class DependencyIndex:
    """Track HTML-to-Markdown and Markdown-to-HTML relationships."""

    def __init__(self) -> None:
        self.html_to_markdown: dict[Path, set[Path]] = {}
        self.html_to_template: dict[Path, set[Path]] = {}
        self.markdown_to_html: dict[Path, set[Path]] = {}
        self.template_to_html: dict[Path, set[Path]] = {}

    def update_html(self, path_html: Path, dependencies: RenderDependencies) -> None:
        """Replace the dependency sets for one HTML page."""
        previous_markdown_paths = self.html_to_markdown.get(path_html, set())
        previous_template_paths = self.html_to_template.get(path_html, set())

        for path_markdown in previous_markdown_paths - dependencies.markdown_paths:
            html_paths = self.markdown_to_html.get(path_markdown)
            if html_paths is None:
                continue
            html_paths.discard(path_html)
            if not html_paths:
                del self.markdown_to_html[path_markdown]

        for path_markdown in dependencies.markdown_paths:
            self.markdown_to_html.setdefault(path_markdown, set()).add(path_html)

        for path_template in previous_template_paths - dependencies.template_paths:
            html_paths = self.template_to_html.get(path_template)
            if html_paths is None:
                continue
            html_paths.discard(path_html)
            if not html_paths:
                del self.template_to_html[path_template]

        for path_template in dependencies.template_paths:
            self.template_to_html.setdefault(path_template, set()).add(path_html)

        self.html_to_markdown[path_html] = set(dependencies.markdown_paths)
        self.html_to_template[path_html] = set(dependencies.template_paths)

    def remove_html(self, path_html: Path) -> None:
        """Remove one HTML page and all of its reverse-index entries."""
        previous_markdown_paths = self.html_to_markdown.pop(path_html, set())
        previous_template_paths = self.html_to_template.pop(path_html, set())

        for path_markdown in previous_markdown_paths:
            html_paths = self.markdown_to_html.get(path_markdown)
            if html_paths is None:
                continue
            html_paths.discard(path_html)
            if not html_paths:
                del self.markdown_to_html[path_markdown]

        for path_template in previous_template_paths:
            html_paths = self.template_to_html.get(path_template)
            if html_paths is None:
                continue
            html_paths.discard(path_html)
            if not html_paths:
                del self.template_to_html[path_template]

    def get_markdown_dependents(self, path_markdown: Path) -> set[Path]:
        """Return HTML pages that depend on the given Markdown file."""
        return set(self.markdown_to_html.get(path_markdown, set()))

    def get_template_dependents(self, path_template: Path) -> set[Path]:
        """Return HTML pages that depend on the given template file."""
        return set(self.template_to_html.get(path_template, set()))
