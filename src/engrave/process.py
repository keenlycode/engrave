# lib: built-in
from pathlib import Path
import shutil

# lib: external
from loguru import logger

# lib: local
from engrave.template import get_template


def build_html(
        *,
        path_html: Path,
        dir_src: Path,
        dir_dest: Path,
) -> None:
    # Get template loader
    template = get_template(dir_src=dir_src)

    # Get relative path from source directory
    path_rel = path_html.relative_to(dir_src)

    # Create output directory if needed
    path_dest = dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content to output file
    with open(path_dest, 'w', encoding='utf-8') as file:
        file.write(template(str(path_rel)).render())

    logger.success(f"✓ Built HTML: {path_rel} → {os.path.relpath(path_dest)}")


def copy_file(
        *,
        path_asset: Path,
        dir_src: Path,
        dir_dest: Path,
) -> None:
    # Get relative path from source directory
    path_rel = path_asset.relative_to(dir_src)

    # Create output directory if needed
    path_dest = dir_dest / path_rel
    path_dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy the asset file
    shutil.copy2(path_asset, path_dest)
    logger.success(f"📁 Copied asset: {path_rel} → {os.path.relpath(path_dest)}")


def delete_file(path: Path):
    path.unlink()
    logger.success(f"🗑 Deleted file: {path}")
