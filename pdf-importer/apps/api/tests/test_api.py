from pathlib import Path

import fitz
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_model():
    payload = {
        "name": "Invoice",
        "json_schema": {
            "type": "object",
            "properties": {"invoice_number": {"type": "string"}},
            "required": ["invoice_number"],
            "additionalProperties": True,
        },
    }
    response = client.post("/api/models", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] > 0
    assert body["name"] == "Invoice"


def test_create_import():
    model_resp = client.post(
        "/api/models",
        json={
            "name": "Simple",
            "json_schema": {
                "type": "object",
                "properties": {"invoice_number": {"type": "string"}},
                "required": [],
                "additionalProperties": True,
            },
        },
    )
    model_id = model_resp.json()["id"]

    pdf_path = Path("tmp_test.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Invoice 123")
    doc.save(pdf_path)
    doc.close()

    with pdf_path.open("rb") as f:
        response = client.post(
            "/api/imports",
            data={"model_id": str(model_id)},
            files={"file": ("tmp_test.pdf", f, "application/pdf")},
        )

    pdf_path.unlink(missing_ok=True)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] > 0
    assert body["status"] in {"done", "failed"}


def test_update_and_delete_model():
    created = client.post(
        "/api/models",
        json={
            "name": "ToUpdate",
            "json_schema": {
                "type": "object",
                "properties": {"invoice_number": {"type": "string"}},
                "required": [],
                "additionalProperties": True,
            },
        },
    )
    model_id = created.json()["id"]

    updated = client.put(
        f"/api/models/{model_id}",
        json={
            "name": "Updated",
            "json_schema": {
                "type": "object",
                "properties": {"total": {"type": "number"}},
                "required": [],
                "additionalProperties": True,
            },
        },
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated"

    deleted = client.delete(f"/api/models/{model_id}")
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "deleted"


def test_delete_import():
    model_resp = client.post(
        "/api/models",
        json={
            "name": "DeleteImportModel",
            "json_schema": {
                "type": "object",
                "properties": {"invoice_number": {"type": "string"}},
                "required": [],
                "additionalProperties": True,
            },
        },
    )
    model_id = model_resp.json()["id"]

    pdf_path = Path("tmp_test_delete.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Invoice 999")
    doc.save(pdf_path)
    doc.close()

    with pdf_path.open("rb") as f:
        created = client.post(
            "/api/imports",
            data={"model_id": str(model_id)},
            files={"file": ("tmp_test_delete.pdf", f, "application/pdf")},
        )
    pdf_path.unlink(missing_ok=True)

    import_id = created.json()["id"]
    deleted = client.delete(f"/api/imports/{import_id}")
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "deleted"

    check = client.get(f"/api/imports/{import_id}")
    assert check.status_code == 404
