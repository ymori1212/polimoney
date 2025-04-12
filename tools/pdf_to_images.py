import os
import argparse
from pdf2image import convert_from_path

def pdf_to_png(pdf_path, output_dir="."):
    """
    Converts each page of a PDF file to a PNG image.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_dir (str): Directory to save the output PNG images. Defaults to current directory.
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
        # 例: poppler_path=r"C:\path\to\poppler\bin" (Windows)
        images = convert_from_path(pdf_path) # poppler_path=poppler_path

        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        for i, image in enumerate(images):
            page_num = i + 1
            output_filename = os.path.join(output_dir, f"{base_filename}_page_{page_num}.png")
            image.save(output_filename, "PNG")
            print(f"Saved: {output_filename}")

        print("Conversion complete.")

    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        print("Please ensure poppler is installed and in your PATH, or specify poppler_path.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF pages to PNG images.")
    parser.add_argument("pdf_file", help="Path to the input PDF file.")
    parser.add_argument("-o", "--output", default=".", help="Output directory for PNG images (default: current directory).")
    # Windowsなどでpopplerのパス指定が必要な場合、引数を追加することもできます
    # parser.add_argument("--poppler_path", help="Path to the poppler installation directory (bin).")

    args = parser.parse_args()

    # poppler_path_arg = args.poppler_path if hasattr(args, 'poppler_path') else None
    pdf_to_png(args.pdf_file, args.output) # poppler_path=poppler_path_arg