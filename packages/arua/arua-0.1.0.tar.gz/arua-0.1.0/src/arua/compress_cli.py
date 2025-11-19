"""Command-line interface for ARUA compression.

This CLI uses :mod:`arua.compression` to invoke the internal ARUA core
compressor via a simple text-first API. Example usage:

    python -m arua.compress_cli compress  -i input.txt  -o output.arua
    python -m arua.compress_cli decompress -i output.arua -o roundtrip.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compression import compress_text, decompress_text


def _read_input(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write_output_bytes(path: str | None, data: bytes) -> None:
    if path is None or path == "-":
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    else:
        Path(path).write_bytes(data)


def _write_output_text(path: str | None, text: str) -> None:
    if path is None or path == "-":
        sys.stdout.write(text)
        sys.stdout.flush()
    else:
        Path(path).write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ARUA CLI wrapper for core compression")
    parser.add_argument(
        "mode", choices=["compress", "decompress"], help="Operation to perform"
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input file path (default: stdin)",
        default="-",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: stdout)",
        default="-",
    )

    args = parser.parse_args(argv)

    if args.mode == "compress":
        text = _read_input(args.input)
        payload, _meta = compress_text(text)
        _write_output_bytes(args.output, payload)
    else:
        data = (
            Path(args.input).read_bytes()
            if args.input != "-"
            else sys.stdin.buffer.read()
        )
        text, _meta = decompress_text(data)
        if isinstance(text, bytes):
            _write_output_bytes(args.output, text)
        else:
            _write_output_text(args.output, text)

    return 0


if __name__ == "__main__":  # pragma: no cover - manual tool
    raise SystemExit(main())
