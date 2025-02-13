from typing import TYPE_CHECKING
from datetime import datetime
from omnigram.config import config
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase

if TYPE_CHECKING:
    from typing import Generator
    from sqlalchemy.orm.session import Session

engine = create_engine(f"sqlite:///{config.database.name}.db", echo=True)


class Base(DeclarativeBase):
    pass


SyncSession: "sessionmaker[Session]" = sessionmaker(bind=engine)


class MessageModel(DeclarativeBase):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    user_id = Column(Integer, nullable=True)
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.now())
    deleted = Column(Boolean, default=False)


Base.metadata.create_all(engine)


def get_session() -> "Generator[Session]":
    with SyncSession() as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            print(e)
        finally:
            session.close()
