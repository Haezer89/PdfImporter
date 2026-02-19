from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import ImportRecord, ModelDefinition
from app.schemas import Message, ModelCreate, ModelOut, ModelUpdate

router = APIRouter(prefix="/api/models", tags=["models"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ModelOut)
def create_model(payload: ModelCreate, db: Session = Depends(get_db)):
    row = ModelDefinition(name=payload.name, json_schema=json.dumps(payload.json_schema, ensure_ascii=False))
    db.add(row)
    db.commit()
    db.refresh(row)
    return ModelOut(id=row.id, name=row.name, json_schema=payload.json_schema, created_at=row.created_at)


@router.get("", response_model=list[ModelOut])
def list_models(db: Session = Depends(get_db)):
    rows = db.query(ModelDefinition).order_by(ModelDefinition.created_at.desc()).all()
    return [
        ModelOut(id=r.id, name=r.name, json_schema=json.loads(r.json_schema), created_at=r.created_at)
        for r in rows
    ]


@router.put("/{model_id}", response_model=ModelOut)
def update_model(model_id: int, payload: ModelUpdate, db: Session = Depends(get_db)):
    row = db.query(ModelDefinition).filter(ModelDefinition.id == model_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="model not found")

    row.name = payload.name
    row.json_schema = json.dumps(payload.json_schema, ensure_ascii=False)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ModelOut(id=row.id, name=row.name, json_schema=payload.json_schema, created_at=row.created_at)


@router.delete("/{model_id}", response_model=Message)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    row = db.query(ModelDefinition).filter(ModelDefinition.id == model_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="model not found")

    linked_imports = db.query(ImportRecord.id).filter(ImportRecord.model_id == model_id).first()
    if linked_imports:
        raise HTTPException(
            status_code=409,
            detail="model has imports and cannot be deleted",
        )

    db.delete(row)
    db.commit()
    return Message(message="deleted")
