from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Question(Base):
    """Represents a question in the database."""
    __tablename__ = 'question'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=False, nullable=False)
    phone_number = Column(String(120), unique=False, nullable=False)
    question = Column(String(120))
