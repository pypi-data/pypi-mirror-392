from .model import QA
from pathlib import Path
import random
import genanki

def save_deck_to_file(deck: genanki.Deck, output_path: Path) -> None:
    """
    주어진 덱을 .apkg 파일로 저장한다.
    """
    package = genanki.Package(deck)
    package.write_to_file(output_path)

def build_qa_deck(name: str, notes: list[genanki.Note]) -> genanki.Deck:
    """
    주어진 덱 ID와 이름으로 QA 덱을 생성한다.
    """
    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(
        deck_id,
        name
    )
    for note in notes:
        deck.add_note(note)

    return deck