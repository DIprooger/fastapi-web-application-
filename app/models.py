from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .conf import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    notes = relationship("Note", back_populates="owner")


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="notes")
