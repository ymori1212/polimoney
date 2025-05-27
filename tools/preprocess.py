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

    def __init__(self, steps: Iterable[str]) -> None:
        self.steps: list[str] = list(steps)
        invalid = [s for s in self.steps if s not in self.AVAILABLE_STEPS]
        if invalid:
            raise ValueError(f"Unknown preprocessing steps: {invalid}")

    def apply(self, image: Image.Image) -> Image.Image:
        result = image
        for step in self.steps:
            if step == "grayscale":
                result = ImageOps.grayscale(result)
            elif step == "binarize":
                if result.mode != "L":
                    result = ImageOps.grayscale(result)
                result = result.point(lambda x: 0 if x < 128 else 255, "1")
            elif step == "denoise":
                result = result.filter(ImageFilter.MedianFilter(size=3))
        return result

    def process_file(self, input_path: Path, output_dir: Path) -> Path:
        image = Image.open(input_path)
        processed = self.apply(image)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / input_path.name
        processed.save(output_path)
        logger.info("Saved preprocessed image: %s", output_path)
        return output_path


def save_log(path: Path, entries: list[dict]) -> None:
    """Save preprocessing log as JSON."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)