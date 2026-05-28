"""Convert all PNG images in the current directory to WebP format."""

import logging
from pathlib import Path

from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def convert_png_to_webp(directory: str = ".") -> None:
    """Convert all PNG files in the given directory to WebP.

    Args:
        directory: Path to the directory containing PNG files.
    """
    target_dir = Path(directory)
    png_files = list(target_dir.glob("*.png"))

    if not png_files:
        logger.info("No PNG files found in %s", directory)
        return

    for png_file in png_files:
        webp_file = png_file.with_suffix(".webp")
        try:
            with Image.open(png_file) as img:
                img.save(webp_file, "WEBP", quality=85)
            logger.info("Converted: %s -> %s", png_file.name, webp_file.name)
        except Exception as e:
            logger.error("Failed to convert %s: %s", png_file.name, e)

    logger.info("Done. %d file(s) processed.", len(png_files))


if __name__ == "__main__":
    convert_png_to_webp()
