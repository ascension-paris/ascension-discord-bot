from sqlalchemy import Column, Integer, String, Table, create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

db = create_engine('sqlite:///sqlite3.db')


class Suggestion(Base):
    __tablename__ = "suggestion"
    id = Column(Integer(), primary_key=True)
    content = Column(String(100), nullable=False)

Base.metadata.create_all(db)