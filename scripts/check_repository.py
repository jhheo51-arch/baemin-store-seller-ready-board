from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "docs/PRD.md",
    "SELLER-READY-BOARD-PORTFOLIO.pdf",
    "SELLER-READY-BOARD-OPERATIONS.xlsx",
    "BAEMIN-STORE-OPERATIONS-PORTFOLIO.html",
    "assets/project-overview.png",
)
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split(" ", 1)[0]
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = unquote(target.split("#", 1)[0])
    return (source.parent / target).resolve()


def check_required_files(errors: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"필수 파일이 없거나 비어 있습니다: {relative_path}")


def check_markdown_links(errors: list[str]) -> None:
    for markdown in ROOT.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(text):
            target = local_target(markdown, raw_target)
            if target is not None and not target.exists():
                source = markdown.relative_to(ROOT).as_posix()
                errors.append(f"끊어진 내부 링크: {source} -> {raw_target}")


def check_csv_files(errors: list[str]) -> None:
    for csv_path in (ROOT / "data").glob("*.csv"):
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        relative_path = csv_path.relative_to(ROOT).as_posix()
        if not reader.fieldnames:
            errors.append(f"열 이름이 없는 CSV입니다: {relative_path}")
        if not rows:
            errors.append(f"데이터 행이 없는 CSV입니다: {relative_path}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_markdown_links(errors)
    check_csv_files(errors)

    if errors:
        print("저장소 검사 실패")
        for error in errors:
            print(f"- {error}")
        return 1

    print("저장소 검사 통과")
    print("필수 결과물, 내부 링크, CSV 구조를 확인했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
