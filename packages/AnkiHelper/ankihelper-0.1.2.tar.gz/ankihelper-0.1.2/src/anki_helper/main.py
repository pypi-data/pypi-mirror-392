from sys import argv
from .json_reader import read_from_jsonfile, create_notes_from_data
from .builder import build_qa_deck, save_deck_to_file
from . import config



def main(argv: list[str] | None =None):
    config.parse_args(argv)

    notes = []

    for path in list(config.NOTES_DIR.rglob("*.json")):
        print(f"노트 파일 처리 중: {path}")
        schema, notes_data = read_from_jsonfile(path)
        notes += create_notes_from_data(schema, notes_data)

    if notes == []:
        raise ValueError("노트가 하나도 없습니다. notes 디렉토리와 JSON 파일을 확인하세요.")

    deck = build_qa_deck(
        name=config.DECK_NAME,
        notes=notes
    )
    save_deck_to_file(deck, config.OUTPUT_NAME)

if __name__ == "__main__":
    main(argv)
    
