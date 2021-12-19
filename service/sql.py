from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy import create_engine
from contextlib import  contextmanager
from threading import Lock

# it will auto create database if not exists
engine = create_engine('sqlite:///market.db')

# a base class to give table model to extends
Base: DeclarativeMeta = declarative_base(bind=engine)

# to build session
session_maker = sessionmaker(bind=engine)


# session should have concurrency facitilies, 
# but due to assuming it doesn't have, 
# so we add lock here
@contextmanager
def DBSession(commit: bool = True, lock: Lock = None):
    if lock:
        lock.acquire()
    session: Session = session_maker()
    yield session
    if commit:
        session.commit()
    session.close()
    if lock:
        lock.release()

# create tables if not exists
def create_tables():
    Base.metadata.create_all(engine)