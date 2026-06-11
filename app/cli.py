"""
Markdown Converter - Command Line Interface
A headless entry point that wraps MarkdownConverter for terminal / script use.

Usage examples:
    python app/cli.py document.pdf
    python app/cli.py ./docs --recursive --formats pdf,word -o ./out
    python app/cli.py report.xlsx --excel-clean --summary --api-key sk-...
    MD_API_KEY=sk-... python app/cli.py file.pdf --ocr --json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add app directory to path BEFORE importing local modules (mirrors main.py).
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from converter import MarkdownConverter, AIOptions, ConversionResult  # noqa: E402

# Exit codes (avoid magic numbers per coding-style rules).
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2

# Environment variable used to supply the API key without exposing it on the
# command line / shell history (per security guidelines).
API_KEY_ENV = "MD_API_KEY"

# Maps user-friendly CLI tokens to MarkdownConverter.SUPPORTED_FORMATS keys.
FORMAT_ALIASES = {
    "pdf": "PDF",
    "word": "Word",
    "docx": "Word",
    "doc": "Word",
    "powerpoint": "PowerPoint",
    "pptx": "PowerPoint",
    "ppt": "PowerPoint",
    "excel": "Excel",
    "xlsx": "Excel",
    "xls": "Excel",
    "images": "Images",
    "image": "Images",
    "img": "Images",
    "text": "Text",
    "txt": "Text",
}


def resolve_formats(tokens: Optional[List[str]]) -> Optional[List[str]]:
    """Translate CLI format tokens into SUPPORTED_FORMATS keys.

    Returns None when no filter is requested (meaning: all formats).
    Raises ValueError on an unknown token so the caller can fail fast.
    """
    if not tokens:
        return None

    resolved: List[str] = []
    for raw in tokens:
        token = raw.strip().lower()
        if not token:
            continue
        if token not in FORMAT_ALIASES:
            valid = ", ".join(sorted(set(FORMAT_ALIASES.keys())))
            raise ValueError(f"Định dạng không hợp lệ: '{raw}'. Hợp lệ: {valid}")
        key = FORMAT_ALIASES[token]
        if key not in resolved:
            resolved.append(key)
    return resolved or None


def resolve_api_key(cli_value: Optional[str]) -> str:
    """Prefer the explicit flag, then fall back to the environment variable."""
    if cli_value:
        return cli_value
    return os.environ.get(API_KEY_ENV, "")


def build_ai_options(args: argparse.Namespace) -> AIOptions:
    """Construct AIOptions from parsed CLI arguments."""
    return AIOptions(
        extract_images=args.extract_images,
        ocr_enabled=args.ocr,
        chunk_enabled=args.chunk,
        excel_clean_enabled=args.excel_clean,
        summary_enabled=args.summary,
        base_url=args.base_url,
        api_key=resolve_api_key(args.api_key),
        model=args.model,
    )


def build_parser() -> argparse.ArgumentParser:
    """Define the command-line interface."""
    parser = argparse.ArgumentParser(
        prog="md-convert",
        description="Chuyển đổi tài liệu Office/PDF sang Markdown (markitdown).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", help="Đường dẫn tới file hoặc thư mục cần chuyển đổi")
    parser.add_argument("-o", "--output", default=None,
                        help="Thư mục xuất (mặc định: cùng vị trí với file gốc)")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Quét cả thư mục con (chỉ áp dụng cho thư mục)")
    parser.add_argument("--max-depth", type=int, default=None,
                        help="Giới hạn độ sâu khi quét đệ quy")
    parser.add_argument("-f", "--formats", default=None,
                        help="Lọc định dạng, phân tách bằng dấu phẩy "
                             "(pdf,word,powerpoint,excel,images,text)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Ghi đè file .md đã tồn tại")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="In kết quả dưới dạng JSON")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Chỉ in lỗi và tóm tắt cuối")

    ai = parser.add_argument_group("AI options")
    ai.add_argument("--extract-images", action="store_true",
                    help="Trích xuất hình ảnh từ PDF/DOCX/PPTX")
    ai.add_argument("--ocr", action="store_true",
                    help="Bật OCR mô tả ảnh (cần API key)")
    ai.add_argument("--chunk", action="store_true",
                    help="Tạo file .jsonl phân mảnh cho RAG")
    ai.add_argument("--excel-clean", action="store_true",
                    help="Làm sạch file Excel (gỡ merge cell) trước khi chuyển đổi")
    ai.add_argument("--summary", action="store_true",
                    help="Sinh tóm tắt + từ khóa bằng AI (cần API key)")
    ai.add_argument("--api-key", default=None,
                    help=f"API key (hoặc đặt biến môi trường {API_KEY_ENV})")
    ai.add_argument("--base-url", default="https://api.openai.com/v1",
                    help="Base URL tương thích OpenAI")
    ai.add_argument("--model", default="gpt-4o-mini", help="Tên model")

    return parser


def _format_line(result: ConversionResult) -> str:
    """Render a single conversion result as a human-readable line."""
    if result.skipped:
        return f"[BỎ QUA] {result.source_path} ({result.error_message})"
    if result.success:
        extra = ""
        if result.images_extracted:
            extra = f" (+{result.images_extracted} ảnh)"
        return f"[OK]      {result.source_path} -> {result.output_path}{extra}"
    return f"[LỖI]     {result.source_path}: {result.error_message}"


def _result_to_dict(result: ConversionResult) -> dict:
    """Serialize a ConversionResult for --json output."""
    return {
        "source_path": result.source_path,
        "output_path": result.output_path,
        "success": result.success,
        "skipped": result.skipped,
        "error_message": result.error_message,
        "images_extracted": result.images_extracted,
        "images_described": result.images_described,
    }


def _emit_results(results: List[ConversionResult], args: argparse.Namespace) -> None:
    """Print per-file output and a final summary."""
    if args.as_json:
        payload = [_result_to_dict(r) for r in results]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if not args.quiet:
        for result in results:
            print(_format_line(result))

    succeeded = sum(1 for r in results if r.success and not r.skipped)
    skipped = sum(1 for r in results if r.skipped)
    failed = sum(1 for r in results if not r.success)
    print(f"Tóm tắt: {succeeded} thành công, {skipped} bỏ qua, {failed} lỗi "
          f"(tổng {len(results)} tệp).")


def run_cli(argv: Optional[List[str]] = None) -> int:
    """Entry point usable from tests and from __main__.

    Returns an exit code: 0 on full success, 1 if any file failed,
    2 on invalid usage.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        allowed_formats = resolve_formats(
            args.formats.split(",") if args.formats else None
        )
    except ValueError as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return EXIT_USAGE

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Lỗi: không tìm thấy '{args.input}'", file=sys.stderr)
        return EXIT_USAGE

    converter = MarkdownConverter()
    converter.set_ai_options(build_ai_options(args))

    if input_path.is_dir():
        results = converter.convert_folder(
            str(input_path),
            recursive=args.recursive,
            max_depth=args.max_depth,
            allowed_formats=allowed_formats,
            output_dir=args.output,
            overwrite=args.overwrite,
        )
    else:
        results = [converter.convert_file(
            str(input_path),
            output_dir=args.output,
            overwrite=args.overwrite,
        )]

    if not results:
        print("Không tìm thấy tệp nào phù hợp để chuyển đổi.", file=sys.stderr)
        return EXIT_SUCCESS

    _emit_results(results, args)

    has_failure = any(not r.success for r in results)
    return EXIT_FAILURE if has_failure else EXIT_SUCCESS


def main() -> None:
    """Console entry point."""
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
