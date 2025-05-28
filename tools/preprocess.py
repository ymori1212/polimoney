"""Basic image preprocessing utilities."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

logger = logging.getLogger("preprocess")


class ImagePreprocessor:
    """Apply simple preprocessing steps to images."""

    AVAILABLE_STEPS = {"grayscale", "binarize", "denoise"}

    def __init__(
        self, 
        steps: Iterable[str], 
        binarize_threshold: int = 128, 
        denoise_filter_size: int = 3
    ) -> None:
        self.steps: list[str] = list(steps)
        invalid = [s for s in self.steps if s not in self.AVAILABLE_STEPS]
        if invalid:
            raise ValueError(f"Unknown preprocessing steps: {invalid}")

        # Validate binarize_threshold (should be between 0 and 255)
        if not isinstance(binarize_threshold, int) or binarize_threshold < 0 or binarize_threshold > 255:
            raise ValueError(f"binarize_threshold must be an integer between 0 and 255, got {binarize_threshold}")

        # Validate denoise_filter_size (should be a positive odd integer)
        if not isinstance(denoise_filter_size, int) or denoise_filter_size <= 3 or denoise_filter_size % 2 == 0:
            raise ValueError(f"denoise_filter_size must be a positive odd integer, got {denoise_filter_size}")

        self.binarize_threshold = binarize_threshold
        self.denoise_filter_size = denoise_filter_size

    def apply(self, image: Image.Image) -> Image.Image:
        result = image
        for step in self.steps:
            if step == "grayscale":
                result = ImageOps.grayscale(result)
            elif step == "binarize":
                if result.mode != "L":
                    result = ImageOps.grayscale(result)
                result = result.point(lambda x: 0 if x < self.binarize_threshold else 255, "1")
            elif step == "denoise":
                result = result.filter(ImageFilter.MedianFilter(size=self.denoise_filter_size))
        return result

    def process_file(self, input_path: Path, output_dir: Path) -> Path:
        try:
            image = Image.open(input_path)
        except (IOError, FileNotFoundError) as e:
            logger.error("Failed to open image %s: %s", input_path, str(e))
            raise IOError(f"Failed to open image {input_path}: {str(e)}") from e

        processed = self.apply(image)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / input_path.name

        try:
            processed.save(output_path)
            logger.info("Saved preprocessed image: %s", output_path)
        except (IOError, OSError) as e:
            logger.error("Failed to save processed image to %s: %s", output_path, str(e))
            raise IOError(f"Failed to save processed image to {output_path}: {str(e)}") from e

        return output_path


def save_log(path: Path, entries: list[dict]) -> bool:
    """
    Save preprocessing log as JSON.

    Args:
        path: Path to save the log file
        entries: List of log entries to save

    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        with path.open("w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
            return True
    except OSError:
        logger.exception("Failed to save log file to %s", path)
        return False
    except json.JSONDecodeError:
        logger.exception("Failed to encode log entries to JSON")
        return False
