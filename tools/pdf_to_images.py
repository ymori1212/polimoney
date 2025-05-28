# ruff: noqa
"""PDFを画像に変換するスクリプト"""

import argparse
import os
import math  # 桁数計算のため
from pathlib import Path

from pdf2image import convert_from_path

from preprocess import ImagePreprocessor, save_log


def pdf_to_png(
    pdf_path: str, 
    output_dir: str = "output_images", 
    preprocess: list[str] | None = None,
    binarize_threshold: int = 128,
    denoise_filter_size: int = 3
) -> None:
    """
    Converts each page of a PDF file to a PNG image with zero-padded page numbers.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_dir (str): Directory to save the output PNG images. Defaults to the current directory.
        preprocess (list[str] | None): List of preprocessing steps to apply (grayscale, binarize, denoise).
        binarize_threshold (int): Threshold for binarization (0-255, default: 128).
        denoise_filter_size (int): Filter size for denoising (odd integer, default: 3).
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    try:
        # PDFを画像オブジェクトのリストに変換
        # poppler_path は環境に合わせて設定が必要な場合があります
        print(f"Converting PDF: {pdf_path} ...")
        images = convert_from_path(pdf_path)  # poppler_path=poppler_path
        print(f"Found {len(images)} pages.")

        if not images:
            print("No pages found in the PDF.")
            return

        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        # ページ番号の桁数を計算 (例: 100ページなら3桁)
        total_pages = len(images)
        num_digits = math.ceil(math.log10(total_pages + 1)) if total_pages > 0 else 1  # 0ページや1ページの場合も考慮

        print(f"Saving images with {num_digits}-digit zero-padded page numbers...")
        processor = ImagePreprocessor(
            preprocess, 
            binarize_threshold=binarize_threshold,
            denoise_filter_size=denoise_filter_size
        ) if preprocess else None
        processed_dir = Path(output_dir) / "processed"
        log_entries: list[dict] = []

        for i, image in enumerate(images):
            page_num = i + 1
            # ページ番号をゼロ埋めしてファイル名を生成
            output_filename = os.path.join(output_dir, f"{base_filename}_page_{page_num:0{num_digits}d}.png")
            image.save(output_filename, "PNG")
            # print(f"Saved: {output_filename}") # 毎回表示すると冗長なのでコメントアウト

            if processor:
                processed_path = processor.process_file(Path(output_filename), processed_dir)
                log_entries.append(
                    {
                        "source": output_filename,
                        "processed": str(processed_path),
                        "steps": processor.steps,
                    }
                )

        if processor:
            save_log(processed_dir / "preprocess_log.json", log_entries)

        print(f"Conversion complete. {total_pages} images saved in {output_dir}")

    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        print("Please ensure poppler is installed and in your PATH, or specify poppler_path if needed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF pages to PNG images with zero-padded filenames.")
    parser.add_argument("pdf_file", help="Path to the input PDF file.")
    parser.add_argument(
        "-o",
        "--output",
        default="output_images",
        help="Output directory for PNG images (default: output_images).",
    )  # デフォルトを変更
    parser.add_argument(
        "--preprocess",
        nargs="*",
        help="Apply preprocessing steps (grayscale, binarize, denoise) after conversion",
    )
    parser.add_argument(
        "--binarize-threshold",
        type=int,
        default=128,
        help="Threshold for binarization (0-255, default: 128)",
    )
    parser.add_argument(
        "--denoise-filter-size",
        type=int,
        default=3,
        help="Filter size for denoising (odd integer, default: 3)",
    )

    # parser.add_argument("--poppler_path", help="Path to the poppler installation directory (bin).")

    args = parser.parse_args()

    # 出力ディレクトリのデフォルトを 'output_images' に変更
    output_directory = args.output if args.output != "." else "output_images"

    # poppler_path_arg = args.poppler_path if hasattr(args, 'poppler_path') else None
    pdf_to_png(
        args.pdf_file, 
        output_directory, 
        preprocess=args.preprocess,
        binarize_threshold=args.binarize_threshold,
        denoise_filter_size=args.denoise_filter_size
    )
