from __future__ import annotations
from pathlib import Path
from sys import version
import genanki
from .model import get_model_by_name

def read_from_jsonfile(json_path: Path) -> tuple[str, list[dict]]:
    """
    주어진 JSON 파일에서 노트 데이터를 읽어서 genanki.Note 객체 리스트로 반환한다.
    JSON 파일은 AnkiSchema QA v1 형식을 따라야 한다.
    """
    import json

    with json_path.open("r", encoding="utf-8") as f:
        data : dict = json.load(f)

    return data['schema'], data['notes']

def create_notes_from_data(schema: str, notes_data: list[dict]) -> list[genanki.Note]:
    """
    주어진 스키마 이름과 노트 데이터 리스트로부터 genanki.Note 객체 리스트를 생성한다.
    현재는 "qa" 스키마만 지원한다.
    """
    notes: list[genanki.Note] = []
    _schema = schema.split('.')  # "anki-helper.qa.v1" -> "qa"
    schema_short = _schema[1]  # "qa"
    version = _schema[2]  # "v1"

    model = get_model_by_name(schema_short)

    for note_data in notes_data:
        fields: list[str]
        tags: list[str]
        if schema_short == "qa":
            fields, tags = _qa_fields_from_dict(note_data)
        else:
            raise ValueError(f"알 수 없는 스키마: {schema}")
        
        note = genanki.Note(
            model=model,
            fields=fields,
            tags=tags
        )
        notes.append(note)

    return notes

def _qa_fields_from_dict(note_data: dict) -> tuple[list[str], list[str]]:
    fields = [note_data['question'], note_data['answer']]
    tags = note_data.get('tags', [])
    return fields, tags