import asyncio
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from engrave.core.build import run as build_run
from engrave.core.watch import run as watch_run
from engrave.util.dataclass import BuildConfig, WatchConfig


class WatchIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.previous_cwd = Path.cwd()
        self.temp_dir = Path(tempfile.mkdtemp())
        fixture_root = Path(__file__).resolve().parents[1] / "fixtures" / "project"

        shutil.copytree(fixture_root / "src", self.temp_dir / "src")
        shutil.copytree(fixture_root / "config", self.temp_dir / "config")

        self.dir_src = self.temp_dir / "src"
        self.dir_dest = self.temp_dir / "dist"
        os.chdir(self.temp_dir)

    async def asyncTearDown(self):
        os.chdir(self.previous_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def _next_batch_after(self, watcher, mutation) -> list:
        next_batch = asyncio.create_task(watcher.__anext__())

        try:
            await asyncio.sleep(0.2)
            mutation()
            return await asyncio.wait_for(next_batch, timeout=5)
        finally:
            if not next_batch.done():
                next_batch.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await next_batch

    async def test_watch_run_emits_build_event_and_rebuilds_modified_html(self):
        source_file = self.dir_src / "index.html"

        build_run(
            BuildConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[],
                exclude=[],
            )
        )

        watcher = watch_run(
            WatchConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[],
                exclude=[],
                watch_add=[],
            )
        )

        try:
            batch = await self._next_batch_after(
                watcher,
                lambda: source_file.write_text("<p>Updated</p>", encoding="utf-8"),
            )
        finally:
            await watcher.aclose()

        self.assertEqual(len(batch), 1)
        self.assertEqual(batch[0].type, "build")
        self.assertEqual(batch[0].path, "index.html")
        self.assertIn(
            "Updated", (self.dir_dest / "index.html").read_text(encoding="utf-8")
        )

    async def test_watch_add_emits_watch_event_without_copying_or_building(self):
        build_run(
            BuildConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[r"assets/.*\.css$"],
                exclude=[],
            )
        )

        watched_file = self.temp_dir / "config" / "settings.yaml"
        watcher = watch_run(
            WatchConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[r"assets/.*\.css$"],
                exclude=[],
                watch_add=[r"config/.*\.yaml$"],
            )
        )

        try:
            batch = await self._next_batch_after(
                watcher,
                lambda: watched_file.write_text("reload: false\n", encoding="utf-8"),
            )
        finally:
            await watcher.aclose()

        self.assertEqual([result.type for result in batch], ["watch"])
        self.assertEqual(batch[0].path, "config/settings.yaml")
        self.assertFalse((self.dir_dest / "config/settings.yaml").exists())

    async def test_watch_run_deletes_copied_file_on_source_delete(self):
        asset_path = self.dir_src / "data" / "info.json"

        build_run(
            BuildConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[r"data/.*\.json$"],
                exclude=[],
            )
        )

        self.assertTrue((self.dir_dest / "data/info.json").exists())

        watcher = watch_run(
            WatchConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[r"data/.*\.json$"],
                exclude=[],
                watch_add=[],
            )
        )

        try:
            batch = await self._next_batch_after(watcher, asset_path.unlink)
        finally:
            await watcher.aclose()

        self.assertEqual([result.type for result in batch], ["copy"])
        self.assertEqual(batch[0].change.name, "deleted")
        self.assertEqual(batch[0].path, "data/info.json")
        self.assertFalse((self.dir_dest / "data/info.json").exists())

    async def test_watch_run_rebuilds_only_dependent_html_on_markdown_change(self):
        source_file = self.dir_src / "index.html"
        other_file = self.dir_src / "section" / "index.html"
        markdown_file = self.dir_src / "content.md"

        source_file.write_text(
            '<html><body>{{ markdown("content.md") }}</body></html>',
            encoding="utf-8",
        )
        other_file.write_text(
            "<html><body><p>Static section</p></body></html>", encoding="utf-8"
        )
        markdown_file.write_text("# Initial\n\nHello", encoding="utf-8")

        dependency_index = build_run(
            BuildConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[],
                exclude=[],
            ),
        )

        watcher = watch_run(
            WatchConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[],
                exclude=[],
                watch_add=[],
            ),
            dependency_index=dependency_index,
        )

        try:
            batch = await self._next_batch_after(
                watcher,
                lambda: markdown_file.write_text(
                    "# Updated\n\nChanged", encoding="utf-8"
                ),
            )
        finally:
            await watcher.aclose()

        self.assertEqual([result.path for result in batch], ["index.html"])
        self.assertTrue((self.dir_dest / "index.html").exists())
        self.assertIn(
            "Updated", (self.dir_dest / "index.html").read_text(encoding="utf-8")
        )
        self.assertIn(
            "Static section",
            (self.dir_dest / "section/index.html").read_text(encoding="utf-8"),
        )

    async def test_watch_run_rebuilds_dependents_for_partial_html_change(self):
        source_file = self.dir_src / "index.html"
        partial_file = self.dir_src / "_partials" / "ignored.html"

        source_file.write_text(
            '<html><body>{% include "_partials/ignored.html" %}</body></html>',
            encoding="utf-8",
        )
        partial_file.write_text("<p>Initial partial</p>", encoding="utf-8")

        dependency_index = build_run(
            BuildConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[],
                exclude=[],
            ),
        )

        self.assertFalse((self.dir_dest / "_partials/ignored.html").exists())

        watcher = watch_run(
            WatchConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[],
                exclude=[],
                watch_add=[],
            ),
            dependency_index=dependency_index,
        )

        try:
            batch = await self._next_batch_after(
                watcher,
                lambda: partial_file.write_text(
                    "<p>Updated partial</p>", encoding="utf-8"
                ),
            )
        finally:
            await watcher.aclose()

        self.assertEqual([result.path for result in batch], ["index.html"])
        self.assertIn(
            "Updated partial",
            (self.dir_dest / "index.html").read_text(encoding="utf-8"),
        )
        self.assertFalse((self.dir_dest / "_partials/ignored.html").exists())


if __name__ == "__main__":
    unittest.main()
