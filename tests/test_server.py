import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from watchfiles import Change

from engrave.server import create_fastapi, watch_to_queue
from engrave.util.dataclass import FileChangeResult, ServerConfig


class ServerRoutingTests(unittest.TestCase):
    def setUp(self):
        fixtures_root = Path(__file__).parent / "fixtures" / "server"
        self.temp_root = Path(tempfile.mkdtemp())
        self.dir_src = self.temp_root / "src"
        self.dir_dest = self.temp_root / "dest"

        shutil.copytree(fixtures_root / "src", self.dir_src)
        shutil.copytree(fixtures_root / "dest", self.dir_dest)

        self.server_config = ServerConfig(
            dir_src=str(self.dir_src),
            dir_dest=str(self.dir_dest),
            copy=[],
            watch_add=[],
            exclude=[],
        )

        self.watch_patch = patch("engrave.server.watch_to_queue", new=AsyncMock())
        self.watch_patch.start()

        self.app = create_fastapi(self.server_config)
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.watch_patch.stop()
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_root_path_renders_root_index_from_source(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Home From Source", response.text)
        self.assertNotIn("Home From Dest", response.text)

    def test_nested_directory_path_renders_nested_index_from_source(self):
        response = self.client.get("/nested/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nested From Source", response.text)
        self.assertNotIn("Nested From Dest", response.text)

    def test_javascript_file_returns_expected_content_type(self):
        response = self.client.get("/assets/app.js")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content, (self.dir_dest / "assets" / "app.js").read_bytes()
        )
        self.assertEqual(
            response.headers["content-type"], "text/javascript; charset=utf-8"
        )

    def test_png_file_returns_expected_content_type(self):
        response = self.client.get("/assets/logo.png")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content, (self.dir_dest / "assets" / "logo.png").read_bytes()
        )
        self.assertEqual(response.headers["content-type"], "image/png")

    def test_ttf_file_returns_expected_content_type(self):
        response = self.client.get("/assets/font.ttf")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content, (self.dir_dest / "assets" / "font.ttf").read_bytes()
        )
        self.assertEqual(response.headers["content-type"], "font/ttf")

    def test_html_request_uses_source_even_when_dest_differs(self):
        (self.dir_src / "index.html").write_text(
            "<!DOCTYPE html><html><body><h1>Fresh Source</h1></body></html>",
            encoding="utf-8",
        )
        (self.dir_dest / "index.html").write_text(
            "<!DOCTYPE html><html><body><h1>Stale Dest</h1></body></html>",
            encoding="utf-8",
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Fresh Source", response.text)
        self.assertNotIn("Stale Dest", response.text)


if __name__ == "__main__":
    unittest.main()


class ServerWatchQueueTests(unittest.IsolatedAsyncioTestCase):
    async def test_watch_to_queue_publishes_one_payload_per_batch(self):
        server_config = ServerConfig(dir_src="src", dir_dest="dest")
        batch = [
            FileChangeResult(path="index.html", type="build", change=Change.modified),
            FileChangeResult(
                path="assets/site.css", type="copy", change=Change.modified
            ),
        ]

        async def fake_watch_run(*args, **kwargs):
            yield batch

        publish_mock = AsyncMock()

        with (
            patch("engrave.server.watch_run", fake_watch_run),
            patch("engrave.server.publish_queue_put", publish_mock),
        ):
            await watch_to_queue(server_config)

        publish_mock.assert_awaited_once_with(
            [
                {"path": "index.html", "type": "build", "change": Change.modified},
                {
                    "path": "assets/site.css",
                    "type": "copy",
                    "change": Change.modified,
                },
            ],
            set(),
        )
