import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import jwt
from datetime import datetime, timedelta
import os


SECRET_KEY = os.getenv('SECRET_KEY')
TOKEN_DELTA = os.getenv('TOKEN_DELTA')


Base = declarative_base()


@pytest.fixture(scope='session')
def engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


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
