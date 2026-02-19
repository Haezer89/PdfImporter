from __future__ import annotations

import json
import logging
from pathlib import Path

from jsonschema import validate

from app.models import ImportRecord, ModelDefinition
from app.services.llm import extract_with_llm
from app.services.ocr import extract_pdf_text

logger = logging.getLogger(__name__)


def process_import(record: ImportRecord, model: ModelDefinition, file_path: Path) -> tuple[str, str]:
    logger.info("processing import id=%s", record.id)
    text = extract_pdf_text(file_path)
    extracted = extract_with_llm(text=text, json_schema=json.loads(model.json_schema))
    validate(instance=extracted, schema=json.loads(model.json_schema))
    return text, json.dumps(extracted, ensure_ascii=False)
