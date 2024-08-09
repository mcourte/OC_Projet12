import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Base


@pytest.fixture(scope='session')
def engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.drop_all(engine)  # Supprimer toutes les tables existantes
    Base.metadata.create_all(engine)  # Recréer toutes les tables
    yield engine
    Base.metadata.drop_all(engine)  # Nettoyer après les tests


@pytest.fixture(scope='function')
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    yield session
    session.remove()
    transaction.rollback()
    connection.close()
