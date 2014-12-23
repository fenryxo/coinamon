# coding: utf-8

from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker


class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Model = declarative_base(cls=Base)

Session = sessionmaker()


@contextmanager
def db_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def bind_engine(engine, **kwd):
    if isinstance(engine, str):
        engine = create_engine('sqlite:///:memory:', **kwd)
    Model.metadata.create_all(engine)
    Session.configure(bind=engine)
    return engine
