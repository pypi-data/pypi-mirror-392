from __future__ import annotations

import argparse
import sys
import genanki
from dataclasses import dataclass
from pathlib import Path

# === 프로그램 버전 ===
VERSION = "0.1.0"

# === 기본 경로 상수 ===
NOTES_DIR = Path("notes")      # notes 디렉토리 루트
OUTPUT_NAME = "deck"           # -> deck.apkg 로 저장할 예정
DECK_NAME = "My Deck"        # 기본 덱 이름


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anki-helper",
        description=(
            "notes 디렉토리 구조를 Anki 덱 계층으로 매핑하여 genanki로 .apkg 덱을 생성합니다.\n"
            "루트 덱 이름은 위치 인자로 받고, notes 디렉토리의 하위 디렉토리는 하위 덱으로 변환됩니다."
        ),
    )

    # --version / -V
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}, Genanki {genanki.__version__}",
        help="프로그램 버전 출력 후 종료",
    )

    # 위치 인자: root_deck_name (최상위 덱 이름)
    parser.add_argument(
        "deck_name",
        metavar="ROOT_DECK",
        default=DECK_NAME,
        help=(
            "최상위 Anki 덱 이름. notes 디렉토리의 구조가 이 덱 아래로 매핑됩니다.\n"
            "예: ROOT_DECK='Software Engineering' 이고 notes/git/basics.json 이면\n"
            "'Software Engineering::git' 덱에 카드가 생성됩니다.\n"
            f"기본값: {DECK_NAME}"
        ),
    )

    # notes 디렉토리
    parser.add_argument(
        "-n",
        "--notes-dir",
        type=Path,
        default=NOTES_DIR,
        help=f"노트 JSON 파일들이 들어 있는 루트 디렉터리 (기본: {NOTES_DIR})",
    )

    # 출력 파일 이름 (확장자 없이)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(OUTPUT_NAME),
        help=(
            "출력 파일 이름 (확장자 없이). 예: -o git_deck → git_deck.apkg 로 저장됩니다. "
            f"기본값: {OUTPUT_NAME}"
        ),
    )

    return parser


def parse_args(argv: list[str] | None = None):
    """
    sys.argv 또는 주어진 argv 리스트를 파싱해서,
    프로그램에서 바로 쓸 수 있는 CLIConfig로 변환한다.
    """
    global NOTES_DIR, OUTPUT_NAME, DECK_NAME
    parser = _build_parser()
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)

    # 출력 경로에 확장자 없으면 .apkg 붙이기
    output: Path = args.output
    if output.suffix == "":
        output = output.with_suffix(".apkg")

    NOTES_DIR = Path(args.notes_dir)
    OUTPUT_NAME = output
    DECK_NAME = args.deck_name
    print("=== 설정된 값 ===")
    print(f"노트 디렉토리: {NOTES_DIR}")
    print(f"{list(NOTES_DIR.rglob('*.json'))}")
    print(f"출력 파일: {OUTPUT_NAME}")
    print(f"덱 이름: {DECK_NAME}")