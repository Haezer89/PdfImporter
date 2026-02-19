from __future__ import annotations

import logging

import fitz
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import ImportRecord, ModelDefinition
from app.schemas import ImportOut, Message
from app.services.pipeline import process_import
from app.services.storage import import_pdf_path, import_preview_path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/imports", tags=["imports"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_preview_image(pdf_path, preview_path, page: int = 1, zoom: float = 1.4, cache: bool = True) -> bytes:
    with fitz.open(pdf_path) as doc:
        if page > doc.page_count:
            raise HTTPException(status_code=404, detail="page not found")
        pix = doc.load_page(page - 1).get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        png = pix.tobytes("png")
        if cache:
            preview_path.write_bytes(png)
        return png


@router.post("", response_model=ImportOut)
async def create_import(
    model_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="file must be a pdf")

    model = db.query(ModelDefinition).filter(ModelDefinition.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="model not found")

    rec = ImportRecord(model_id=model.id, filename=file.filename, status="processing")
    db.add(rec)
    db.commit()
    db.refresh(rec)

    target = import_pdf_path(rec.id)
    content = await file.read()
    target.write_bytes(content)
    preview_path = import_preview_path(rec.id)
    try:
        generate_preview_image(target, preview_path, page=1, zoom=1.4)
    except Exception:
        logger.exception("failed preview generation id=%s", rec.id)

    try:
        text, extracted_json = process_import(rec, model, target)
        rec.ocr_text = text
        rec.extracted_json = extracted_json
        rec.status = "done"
        rec.error = None
    except Exception as exc:
        logger.exception("failed import id=%s", rec.id)
        rec.status = "failed"
        rec.error = str(exc)

    db.add(rec)
    db.commit()
    db.refresh(rec)
    return ImportOut.from_row(rec)


@router.get("", response_model=list[ImportOut])
def list_imports(db: Session = Depends(get_db)):
    rows = db.query(ImportRecord).order_by(ImportRecord.created_at.desc()).all()
    return [ImportOut.from_row(r) for r in rows]


@router.get("/{import_id}", response_model=ImportOut)
def get_import(import_id: int, db: Session = Depends(get_db)):
    row = db.query(ImportRecord).filter(ImportRecord.id == import_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="import not found")
    return ImportOut.from_row(row)


@router.get("/{import_id}/file")
def get_import_file(import_id: int, db: Session = Depends(get_db)):
    row = db.query(ImportRecord).filter(ImportRecord.id == import_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="import not found")

    file_path = import_pdf_path(import_id)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"},
    )


@router.get("/{import_id}/preview")
def get_import_preview(
    import_id: int,
    page: int = Query(default=1, ge=1),
    zoom: float = Query(default=1.4, ge=0.7, le=3.0),
    db: Session = Depends(get_db),
):
    row = db.query(ImportRecord).filter(ImportRecord.id == import_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="import not found")

    file_path = import_pdf_path(import_id)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="file not found")
    preview_path = import_preview_path(import_id)

    if page == 1 and preview_path.exists():
        return FileResponse(path=preview_path, media_type="image/png")

    png = generate_preview_image(file_path, preview_path, page=page, zoom=zoom, cache=(page == 1))
    return Response(content=png, media_type="image/png")


@router.delete("/{import_id}", response_model=Message)
def delete_import(import_id: int, db: Session = Depends(get_db)):
    row = db.query(ImportRecord).filter(ImportRecord.id == import_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="import not found")

    file_path = import_pdf_path(import_id)
    if file_path.exists():
        file_path.unlink()
    preview_path = import_preview_path(import_id)
    if preview_path.exists():
        preview_path.unlink()

    db.delete(row)
    db.commit()
    return Message(message="deleted")
