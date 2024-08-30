from sqlalchemy.orm import Session
from . import models
from . import schemas
from . import auth
from fastapi import HTTPException

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> models.User:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"Note with id {user_id} not found")
    return db_user


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> models.User:
    db_user = get_user(db, user_id)
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> models.User:
    db_user = get_user(db, user_id)
    db.delete(db_user)
    db.commit()
    return db_user

