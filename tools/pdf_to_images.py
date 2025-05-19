# ruff: noqa
"""PDFを画像に変換するスクリプト.

オプションで画像前処理も実行できる。前処理後の画像は
`preprocessed_images` フォルダに保存される。"""

import argparse
import os
import math  # 桁数計算のため
from typing import List

from pdf2image import convert_from_path

from image_preprocess import apply_preprocess


def pdf_to_png(pdf_path: str, output_dir: str = ".", preprocess: List[str] | None = None) -> None:
    """
    Converts each page of a PDF file to a PNG image with zero-padded page numbers.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_dir (str): Directory to save the output PNG images.
        preprocess (List[str] | None): 適用する前処理名のリスト。Noneの場合は前処理を行わない。
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
        preprocess_dir = os.path.join(output_dir, "preprocessed_images")
        log_path = os.path.join(preprocess_dir, "preprocess.log")
        if preprocess:
            os.makedirs(preprocess_dir, exist_ok=True)

        for i, image in enumerate(images):
            page_num = i + 1
            # ページ番号をゼロ埋めしてファイル名を生成
            output_filename = os.path.join(output_dir, f"{base_filename}_page_{page_num:0{num_digits}d}.png")
            image.save(output_filename, "PNG")

            if preprocess:
                processed = apply_preprocess(image, preprocess)
                pre_filename = os.path.join(
                    preprocess_dir,
                    f"{base_filename}_page_{page_num:0{num_digits}d}.png",
                )
                processed.save(pre_filename, "PNG")
                with open(log_path, "a", encoding="utf-8") as logf:
                    logf.write(f"{pre_filename}: {','.join(preprocess)}\n")

            # print(f"Saved: {output_filename}") # 毎回表示すると冗長なのでコメントアウト

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
        help="カンマ区切りで前処理を指定 (例: grayscale,binarize)",
    )
    # parser.add_argument("--poppler_path", help="Path to the poppler installation directory (bin).")

    args = parser.parse_args()

    # 出力ディレクトリのデフォルトを 'output_images' に変更
    output_directory = args.output if args.output != "." else "output_images"

    # poppler_path_arg = args.poppler_path if hasattr(args, 'poppler_path') else None
    preprocess = args.preprocess.split(",") if args.preprocess else None

    # poppler_path_arg = args.poppler_path if hasattr(args, 'poppler_path') else None
    pdf_to_png(args.pdf_file, output_directory, preprocess)  # poppler_path=poppler_path_arg
