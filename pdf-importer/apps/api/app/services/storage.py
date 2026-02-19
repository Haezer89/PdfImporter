from __future__ import annotations

from pathlib import Path

from app.core.config import settings


def ensure_upload_dir() -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def import_pdf_path(import_id: int) -> Path:
    return ensure_upload_dir() / f"{import_id}.pdf"


def ensure_preview_dir() -> Path:
    preview_dir = Path("./data/previews")
    preview_dir.mkdir(parents=True, exist_ok=True)
    return preview_dir


def import_preview_path(import_id: int) -> Path:
    return ensure_preview_dir() / f"{import_id}.png"
