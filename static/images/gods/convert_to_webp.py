"""Convert all PNG and JPG images in the current directory to WebP format."""

import logging
from pathlib import Path

from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = ("*.png", "*.jpg", "*.jpeg")


def convert_images_to_webp(directory: str = ".") -> None:
    """Convert all PNG and JPG files in the given directory to WebP.

    Args:
        directory: Path to the directory containing image files.
    """
    target_dir = Path(directory)
    image_files = [f for ext in SUPPORTED_EXTENSIONS for f in target_dir.glob(ext)]

    if not image_files:
        logger.info("No PNG or JPG files found in %s", directory)
        return

    for image_file in image_files:
        webp_file = image_file.with_suffix(".webp")
        try:
            with Image.open(image_file) as img:
                img.save(webp_file, "WEBP", quality=85)
            image_file.unlink()
            logger.info("Converted and removed: %s -> %s", image_file.name, webp_file.name)
        except Exception as e:
            logger.error("Failed to convert %s: %s", image_file.name, e)

    logger.info("Done. %d file(s) processed.", len(image_files))


if __name__ == "__main__":
    convert_images_to_webp()
