import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engrave.core.build import run as build_run
from engrave.util.dataclass import BuildConfig


class BuildRuleTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.dir_src = self.temp_dir / "src"
        self.dir_dest = self.temp_dir / "dist"

        fixture_root = Path(__file__).resolve().parents[1] / "fixtures" / "project" / "src"
        shutil.copytree(fixture_root, self.dir_src)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_matches_source_relative_paths_and_respects_exclude(self):
        build_run(
            BuildConfig(
                dir_src=str(self.dir_src),
                dir_dest=str(self.dir_dest),
                copy=[r"assets/.*\.(css|js)$", r"data/.*\.json$"],
                exclude=[r"drafts/.*"],
            )
        )

        self.assertTrue((self.dir_dest / "index.html").exists())
        self.assertTrue((self.dir_dest / "section/index.html").exists())
        self.assertTrue((self.dir_dest / "assets/app.css").exists())
        self.assertTrue((self.dir_dest / "assets/app.js").exists())
        self.assertTrue((self.dir_dest / "data/info.json").exists())

        self.assertFalse((self.dir_dest / "_partials/ignored.html").exists())
        self.assertFalse((self.dir_dest / "drafts/skip.html").exists())
        self.assertFalse((self.dir_dest / "drafts/skip.css").exists())

    def test_build_never_copies_html_even_if_copy_regex_matches(self):
        config = BuildConfig(
            dir_src=str(self.dir_src),
            dir_dest=str(self.dir_dest),
            copy=[r".*\.html$", r"assets/.*\.css$"],
            exclude=[r"drafts/.*"],
        )

        with patch("engrave.core.build.process.build_html") as mock_build_html, patch(
            "engrave.core.build.process.copy_file"
        ) as mock_copy_file:
            build_run(config)

        build_paths = sorted(
            path.relative_to(self.dir_src).as_posix()
            for path in (call_args.args[0].path for call_args in mock_build_html.call_args_list)
        )
        copy_paths = sorted(
            path.relative_to(self.dir_src).as_posix()
            for path in (call_args.args[0].path for call_args in mock_copy_file.call_args_list)
        )

        self.assertEqual(
            build_paths,
            ["index.html", "section/index.html"],
        )
        self.assertEqual(copy_paths, ["assets/app.css"])


if __name__ == "__main__":
    unittest.main()
