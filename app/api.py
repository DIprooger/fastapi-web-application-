import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from . import user
from . import notes
from . import schemas
from . import conf
from . import auth

app = FastAPI()

def get_db() -> Session:
    db = conf.SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict:
    user_instance = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user_instance:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user_instance.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(get_db)
) -> schemas.User:
    db_user = user.get_user_by_email(db, email=user_data.email)
    if not db_user:
        return user.create_user(db=db, user=user_data)
    raise HTTPException(status_code=400, detail="Email already registered")

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> schemas.User:
    db_user = user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db)
) -> schemas.User:
    db_user = user.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> schemas.User:
    db_user = user.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def check_spelling(text: str) -> None:
    url = "https://speller.yandex.net/services/spellservice.json/checkText"
    params = {"text": text}
    response = requests.get(url, params=params)
    result = response.json()
    if result:
        errors = [
            f"Error: {error['word']} → {', '.join(error['s'])}" for error in result
        ]
        raise HTTPException(status_code=422, detail=f"Error: {'; '.join(errors)}")

@app.post("/notes/", response_model=schemas.NoteInDB)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
) -> schemas.NoteInDB:
    check_spelling(note.title)
    check_spelling(note.content)
    return notes.create_note(db=db, note=note, owner_id=current_user.id)

@app.get("/notes/", response_model=schemas.NoteListResponse)
def read_notes(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
) -> schemas.NoteListResponse:
    notes_list = notes.get_notes_by_user(db, user_id=current_user.id)
    return {"notes": notes_list}

@app.get("/notes/{note_id}", response_model=schemas.NoteInDB)
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
) -> schemas.NoteInDB:
    note = notes.get_note_by_id(db, note_id=note_id)
    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=schemas.NoteInDB)
def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
) -> schemas.NoteInDB:
    check_spelling(note_update.title)
    check_spelling(note_update.content)
    note = notes.update_note(db, note_id=note_id, note_update=note_update)
    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found or not authorized")
    return note

@app.delete("/notes/{note_id}", response_model=schemas.NoteInDB)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
) -> schemas.NoteInDB:
    note = notes.delete_note(db, note_id=note_id)
    if note is None or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found or not authorized")
    return note

