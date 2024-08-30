from sqlalchemy.orm import Session
from . import models
from . import schemas
from fastapi import HTTPException

def create_note(db: Session, note: schemas.NoteCreate, owner_id: int) -> models.Note:
    db_note = models.Note(title=note.title, content=note.content, owner_id=owner_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_note_by_id(db: Session, note_id: int) -> models.Note:
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail=f"Note with id {note_id} not found")
    return db_note

def get_notes_by_user(db: Session, user_id: int) -> list[models.Note]:
    return db.query(models.Note).filter(models.Note.owner_id == user_id).all()

def update_note(db: Session, note_id: int, note_update: schemas.NoteUpdate) -> models.Note:
    db_note = get_note_by_id(db, note_id)
    for key, value in note_update.dict(exclude_unset=True).items():
        setattr(db_note, key, value)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int) -> models.Note:
    db_note = get_note_by_id(db, note_id)
    db.delete(db_note)
    db.commit()
    return db_note
