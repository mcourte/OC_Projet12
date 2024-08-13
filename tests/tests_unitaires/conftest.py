import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, Base


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


@pytest.fixture(scope='function')
def valid_token():
    """Fixture pour un token JWT valide."""
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'sub': 'test_user',
        'role': 'ADM'
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
