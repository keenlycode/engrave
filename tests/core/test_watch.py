import asyncio
import shutil
import tempfile
import unittest
from pathlib import Path

from engrave.core.build import run as build_run
from engrave.core.watch import run as watch_run
from engrave.util.dataclass import BuildConfig, WatchConfig


class WatchIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.dir_src = Path(tempfile.mkdtemp())
        self.dir_dest = Path(tempfile.mkdtemp())

    async def asyncTearDown(self):
        shutil.rmtree(self.dir_src, ignore_errors=True)
        shutil.rmtree(self.dir_dest, ignore_errors=True)

    async def test_watch_run_emits_event_and_rebuilds_modified_html(self):
        source_file = self.dir_src / "index.html"
        source_file.write_text("<p>Initial</p>", encoding="utf-8")

        build_run(
            BuildConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[],
                exclude=[],
            )
        )

        watch_config = WatchConfig(
            dir_src=str(self.dir_src),
            dir_dest=str(self.dir_dest),
            copy=[],
            exclude=[],
            watch_add=[],
        )

        watcher = watch_run(watch_config)
        next_batch = asyncio.create_task(watcher.__anext__())

        try:
            await asyncio.sleep(0.2)
            source_file.write_text("<p>Updated</p>", encoding="utf-8")

            batch = await asyncio.wait_for(next_batch, timeout=5)
        finally:
            if not next_batch.done():
                next_batch.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await next_batch
            await watcher.aclose()

        self.assertEqual(len(batch), 1)
        self.assertEqual(batch[0].type, "build")
        self.assertEqual(batch[0].path, str(source_file))
        self.assertIn("Updated", (self.dir_dest / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
