from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_USER_POS")
password = os.getenv("DB_PASSWORD_POS")
db = os.getenv("DB_NAME_POS")
local_machine_port_host = "localhost:5443"
docker_port_host = "postgres:5432"

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{docker_port_host}/{db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
