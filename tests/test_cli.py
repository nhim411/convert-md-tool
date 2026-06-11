"""
Tests for the command-line interface (app/cli.py).

Run with:   pytest tests/test_cli.py
Or direct:  python tests/test_cli.py   (falls back to a minimal runner)
"""

import json
import os
import sys

import pytest

# Make the app package importable, same convention as main.py / tests.
APP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import cli  # noqa: E402
from converter import AIOptions, ConversionResult  # noqa: E402


# ---------------------------------------------------------------------------
# resolve_formats
# ---------------------------------------------------------------------------

def test_resolve_formats_returns_none_when_empty():
    assert cli.resolve_formats(None) is None
    assert cli.resolve_formats([]) is None


def test_resolve_formats_maps_aliases_to_canonical_keys():
    result = cli.resolve_formats(["pdf", "word", "xlsx"])
    assert result == ["PDF", "Word", "Excel"]


def test_resolve_formats_deduplicates_and_trims():
    result = cli.resolve_formats([" docx ", "word", "doc"])
    assert result == ["Word"]


def test_resolve_formats_ignores_blank_tokens():
    assert cli.resolve_formats(["", "  "]) is None


def test_resolve_formats_raises_on_unknown_token():
    with pytest.raises(ValueError):
        cli.resolve_formats(["spreadsheet"])


# ---------------------------------------------------------------------------
# resolve_api_key
# ---------------------------------------------------------------------------

def test_resolve_api_key_prefers_cli_value(monkeypatch):
    monkeypatch.setenv(cli.API_KEY_ENV, "env-key")
    assert cli.resolve_api_key("flag-key") == "flag-key"


def test_resolve_api_key_falls_back_to_env(monkeypatch):
    monkeypatch.setenv(cli.API_KEY_ENV, "env-key")
    assert cli.resolve_api_key(None) == "env-key"


def test_resolve_api_key_empty_when_unset(monkeypatch):
    monkeypatch.delenv(cli.API_KEY_ENV, raising=False)
    assert cli.resolve_api_key(None) == ""


# ---------------------------------------------------------------------------
# build_ai_options
# ---------------------------------------------------------------------------

def test_build_ai_options_maps_all_flags(monkeypatch):
    monkeypatch.delenv(cli.API_KEY_ENV, raising=False)
    parser = cli.build_parser()
    args = parser.parse_args([
        "in.pdf",
        "--extract-images", "--ocr", "--chunk", "--excel-clean", "--summary",
        "--api-key", "k", "--base-url", "http://x/v1", "--model", "m",
    ])
    opts = cli.build_ai_options(args)
    assert isinstance(opts, AIOptions)
    assert opts.extract_images and opts.ocr_enabled and opts.chunk_enabled
    assert opts.excel_clean_enabled and opts.summary_enabled
    assert opts.api_key == "k"
    assert opts.base_url == "http://x/v1"
    assert opts.model == "m"


def test_build_ai_options_defaults_are_off(monkeypatch):
    monkeypatch.delenv(cli.API_KEY_ENV, raising=False)
    parser = cli.build_parser()
    args = parser.parse_args(["in.pdf"])
    opts = cli.build_ai_options(args)
    assert not any([
        opts.extract_images, opts.ocr_enabled, opts.chunk_enabled,
        opts.excel_clean_enabled, opts.summary_enabled,
    ])
    assert opts.api_key == ""


# ---------------------------------------------------------------------------
# parser defaults
# ---------------------------------------------------------------------------

def test_parser_defaults():
    args = cli.build_parser().parse_args(["thing"])
    assert args.input == "thing"
    assert args.output is None
    assert args.recursive is False
    assert args.overwrite is False
    assert args.as_json is False
    assert args.quiet is False


def test_parser_missing_input_exits():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args([])


# ---------------------------------------------------------------------------
# formatting helpers
# ---------------------------------------------------------------------------

def test_format_line_ok_with_images():
    r = ConversionResult("a.pdf", "a.pdf.md", True, images_extracted=3)
    line = cli._format_line(r)
    assert "[OK]" in line and "+3" in line


def test_format_line_skipped():
    r = ConversionResult("a.pdf", "a.pdf.md", True, skipped=True, error_message="đã tồn tại")
    assert "[BỎ QUA]" in cli._format_line(r)


def test_format_line_error():
    r = ConversionResult("a.pdf", None, False, error_message="boom")
    line = cli._format_line(r)
    assert "[LỖI]" in line and "boom" in line


def test_result_to_dict_roundtrip():
    r = ConversionResult("a.pdf", "a.pdf.md", True, images_extracted=2)
    d = cli._result_to_dict(r)
    assert d["source_path"] == "a.pdf"
    assert d["success"] is True
    assert d["images_extracted"] == 2


# ---------------------------------------------------------------------------
# run_cli — usage errors
# ---------------------------------------------------------------------------

def test_run_cli_missing_input_returns_usage_error(capsys):
    code = cli.run_cli(["/no/such/path/xyz.pdf"])
    assert code == cli.EXIT_USAGE
    assert "không tìm thấy" in capsys.readouterr().err.lower()


def test_run_cli_invalid_format_returns_usage_error(tmp_path, capsys):
    f = tmp_path / "x.txt"
    f.write_text("hi", encoding="utf-8")
    code = cli.run_cli([str(f), "--formats", "bogus"])
    assert code == cli.EXIT_USAGE
    assert "không hợp lệ" in capsys.readouterr().err.lower()


# ---------------------------------------------------------------------------
# run_cli — real conversion (uses markitdown on a plain text file)
# ---------------------------------------------------------------------------

def test_run_cli_single_file_success(tmp_path, capsys):
    src = tmp_path / "note.txt"
    src.write_text("Hello world from CLI test.", encoding="utf-8")
    out = tmp_path / "out"

    code = cli.run_cli([str(src), "-o", str(out)])

    assert code == cli.EXIT_SUCCESS
    produced = out / "note.txt.md"
    assert produced.exists()
    assert "Tóm tắt" in capsys.readouterr().out


def test_run_cli_folder_with_format_filter(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.csv").write_text("c1,c2\n1,2\n", encoding="utf-8")
    out = tmp_path / "out"

    code = cli.run_cli([str(tmp_path), "--formats", "text", "-o", str(out)])

    assert code == cli.EXIT_SUCCESS
    assert (out / "a.txt.md").exists()
    assert (out / "b.csv.md").exists()


def test_run_cli_json_output(tmp_path, capsys):
    src = tmp_path / "note.txt"
    src.write_text("json please", encoding="utf-8")

    code = cli.run_cli([str(src), "-o", str(tmp_path / "o"), "--json"])

    assert code == cli.EXIT_SUCCESS
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list) and payload[0]["success"] is True


def test_run_cli_quiet_suppresses_per_file_lines(tmp_path, capsys):
    src = tmp_path / "note.txt"
    src.write_text("quiet", encoding="utf-8")

    code = cli.run_cli([str(src), "-o", str(tmp_path / "o"), "--quiet"])

    out = capsys.readouterr().out
    assert code == cli.EXIT_SUCCESS
    assert "[OK]" not in out          # per-file line suppressed
    assert "Tóm tắt" in out           # summary still shown


def test_run_cli_empty_folder_reports_nothing(tmp_path, capsys):
    code = cli.run_cli([str(tmp_path)])
    assert code == cli.EXIT_SUCCESS
    assert "Không tìm thấy" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# run_cli — failure path (monkeypatched converter for determinism)
# ---------------------------------------------------------------------------

def test_run_cli_returns_failure_when_conversion_fails(tmp_path, monkeypatch):
    src = tmp_path / "broken.txt"
    src.write_text("x", encoding="utf-8")

    def fake_convert_file(self, source_path, output_dir=None, overwrite=False):
        return ConversionResult(source_path, None, False, "simulated failure")

    monkeypatch.setattr(cli.MarkdownConverter, "convert_file", fake_convert_file)
    code = cli.run_cli([str(src)])
    assert code == cli.EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
