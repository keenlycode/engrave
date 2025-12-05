"""Integration-like tests exercising CLI commands with real filesystem I/O."""
import asyncio
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI

from engrave.core import cli


class CLICoreIntegrationTests(unittest.TestCase):
    """Runs CLI entrypoints against temporary directories to verify side effects."""

    def setUp(self):
        self.dir_src = Path(tempfile.mkdtemp())
        self.dir_dest = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir_src, ignore_errors=True)
        shutil.rmtree(self.dir_dest, ignore_errors=True)

    def _write(self, rel_path: str, content: str) -> Path:
        path = self.dir_src / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_build_command_renders_html_and_copies_assets(self):
        self._write("index.html", "<p>Hello Build</p>")
        self._write("static/style.css", "body { color: black; }")

        config = cli.BuildConfig(
            dir_src=str(self.dir_src),
            dir_dest=str(self.dir_dest),
            copy=[r".*\.css$"],
            watch=[],
            exclude=[],
        )

        # Run the build coroutine so we exercise the real build pipeline.
        asyncio.run(cli.build(config))

        html_out = self.dir_dest / "index.html"
        css_out = self.dir_dest / "static/style.css"

        self.assertTrue(html_out.exists(), "HTML file should be rendered to destination")
        self.assertTrue(css_out.exists(), "Asset file should be copied to destination")
        self.assertIn("Hello Build", html_out.read_text(encoding="utf-8"))
        self.assertIn("color: black", css_out.read_text(encoding="utf-8"))

    def test_server_builds_and_invokes_uvicorn(self):
        self._write("home.html", "<h1>Server Page</h1>")

        server_config = cli.ServerConfig(
            dir_src=str(self.dir_src),
            dir_dest=str(self.dir_dest),
            copy=[],
            watch=[],
            exclude=[],
            host="0.0.0.0",
            port=5050,
        )

        with patch("engrave.core.cli.uvicorn.run") as mock_uvicorn_run:
            cli.server(server_config)

        html_out = self.dir_dest / "home.html"
        self.assertTrue(html_out.exists(), "Server should trigger an initial build")

        self.assertTrue(mock_uvicorn_run.called)
        args, kwargs = mock_uvicorn_run.call_args
        self.assertIsInstance(args[0], FastAPI)
        self.assertEqual(kwargs["host"], "0.0.0.0")
        self.assertEqual(kwargs["port"], 5050)


if __name__ == "__main__":
    unittest.main()
