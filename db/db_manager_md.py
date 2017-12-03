'''
Created on Nov 10, 2017

@author: mtiwari
'''
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.orm import scoped_session, sessionmaker

def create_my_engine():
    return create_engine('mysql://finuser:bankrupt@localhost/fin')
    #return create_engine('sqlite:////Users/mtiwari/src/python-noobs/Finances/sqlite/1.db')

@contextmanager
def db_session():
    """ Creates a context with an open SQLAlchemy session.
    """
    engine = create_my_engine()
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    yield db_session
    db_session.close()
    connection.close()