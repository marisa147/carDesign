from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from caragent_api.main import app


def export_openapi(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    output_path.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export the carAgent API OpenAPI schema.")
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Path to write the OpenAPI JSON artifact.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    export_openapi(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
