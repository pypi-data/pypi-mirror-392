import genanki
from .template import QA_TEMPLATE
QA_MODEL_ID = 1607392319

QA = genanki.Model(
    QA_MODEL_ID,
    "QA Minimal",
    **QA_TEMPLATE
)

_MODELS = {
    "qa": QA,
}

def get_model_by_name(name: str) -> genanki.Model:
    if name in _MODELS:
        return _MODELS[name]
    else:
        raise ValueError(f"알 수 없는 모델 이름: {name}")