from __future__ import annotations

import json
import logging

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

INVOICE_EXTRACTION_RULES = """
Task focus: invoices, including German-language invoices.

Use common German invoice labels and synonyms when mapping fields:
- invoice_number: Rechnungsnummer, Belegnummer, Dokumentnummer
- invoice_date: Rechnungsdatum, Datum
- due_date: Faelligkeitsdatum, zahlbar bis
- total/gross_total: Gesamtbetrag, Bruttobetrag, Rechnungsbetrag
- net_total: Nettobetrag, Zwischensumme
- tax/vat_amount: USt, MwSt, Mehrwertsteuer
- currency: EUR, USD, CHF (or symbols EUR, $, CHF)
- vendor_name: Lieferant, Aussteller, Rechnungsteller
- customer_name: Kunde, Rechnungsempfaenger

Normalization rules:
- Convert German number formats to JSON numbers (e.g. "1.234,56" -> 1234.56).
- Prefer ISO dates YYYY-MM-DD when possible (e.g. 31.12.2025 -> 2025-12-31).
- Return null only when value is genuinely missing/unknown.
- Never invent invoice values that are not present in text.
"""


def _fallback_from_schema(json_schema: dict) -> dict:
    properties = json_schema.get("properties", {})
    result = {}
    for key, spec in properties.items():
        t = spec.get("type") if isinstance(spec, dict) else None
        if t in {"number", "integer"}:
            result[key] = 0
        elif t == "boolean":
            result[key] = False
        elif t == "array":
            result[key] = []
        elif t == "object":
            result[key] = {}
        else:
            result[key] = ""
    return result


def extract_with_llm(text: str, json_schema: dict) -> dict:
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY is missing, using schema fallback output")
        return _fallback_from_schema(json_schema)

    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = (
        "You extract structured data from OCR text and output strict JSON only. "
        "Do not include markdown, comments, or extra keys outside the requested schema."
    )
    schema_keys = list((json_schema or {}).get("properties", {}).keys())
    user_prompt = (
        "Extract data from the provided text and fit it to this JSON schema.\n\n"
        f"Required output keys come from schema properties: {schema_keys}\n\n"
        f"{INVOICE_EXTRACTION_RULES}\n\n"
        f"JSON Schema:\n{json.dumps(json_schema, ensure_ascii=False)}\n\n"
        f"Text:\n{text[:120000]}"
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("LLM returned empty content")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"LLM output was not valid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("LLM output must be a JSON object")
    return parsed
