import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from engrave.server import create_fastapi
from engrave.util.dataclass import ServerConfig


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

        self.build_patch = patch("engrave.server.build_run")
        self.watch_patch = patch("engrave.server.watch_to_queue", new=AsyncMock())
        self.mock_build_run = self.build_patch.start()
        self.watch_patch.start()

        self.app = create_fastapi(self.server_config)
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.watch_patch.stop()
        self.build_patch.stop()
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_root_path_returns_root_index_file(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Home From Dest", response.text)
        self.mock_build_run.assert_called_once()

    def test_nested_directory_path_returns_nested_index_file(self):
        response = self.client.get("/nested/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Nested From Dest", response.text)
        self.mock_build_run.assert_called_once()

    def test_javascript_file_returns_expected_content_type(self):
        response = self.client.get("/assets/app.js")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, (self.dir_dest / "assets" / "app.js").read_bytes())
        self.assertEqual(response.headers["content-type"], "text/javascript; charset=utf-8")
        self.mock_build_run.assert_not_called()

    def test_png_file_returns_expected_content_type(self):
        response = self.client.get("/assets/logo.png")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, (self.dir_dest / "assets" / "logo.png").read_bytes())
        self.assertEqual(response.headers["content-type"], "image/png")
        self.mock_build_run.assert_not_called()

    def test_ttf_file_returns_expected_content_type(self):
        response = self.client.get("/assets/font.ttf")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, (self.dir_dest / "assets" / "font.ttf").read_bytes())
        self.assertEqual(response.headers["content-type"], "font/ttf")
        self.mock_build_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
