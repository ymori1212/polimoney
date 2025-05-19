"""画像前処理をまとめたモジュール."""

from typing import Callable

from PIL import Image

# 前処理関数の型
PreprocessFunc = Callable[[Image.Image], Image.Image]


def to_grayscale(image: Image.Image) -> Image.Image:
    """画像をグレースケール化する前処理."""

    return image.convert("L")


def binarize(image: Image.Image, threshold: int = 128) -> Image.Image:
    """指定した閾値で単純二値化を行う前処理."""

    gray = image.convert("L")
    return gray.point(lambda x: 255 if x > threshold else 0, mode="1")


# 利用可能な前処理関数一覧
PREPROCESS_FUNCTIONS: dict[str, PreprocessFunc] = {
    "grayscale": to_grayscale,
    "binarize": binarize,
}


def apply_preprocess(image: Image.Image, methods: list[str]) -> Image.Image:
    """指定された前処理を順番に適用する."""

    processed = image
    for name in methods:
        func = PREPROCESS_FUNCTIONS.get(name)
        if func:
            processed = func(processed)
        else:
            print(f"Warning: unknown preprocess '{name}' is ignored")
    return processed
