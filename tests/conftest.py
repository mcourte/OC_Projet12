import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import jwt
from datetime import datetime, timedelta
import os
import tempfile

# Valeurs par défaut pour les variables d'environnement
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
TOKEN_DELTA = os.getenv('TOKEN_DELTA', '3600')  # Exemple : 1 heure par défaut

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
        'sub': 'auser',
        'role': 'ADM'
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

@pytest.fixture
def temp_file():
    # Création d'un fichier temporaire
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    # Nettoyage du fichier temporaire après le test
    if os.path.exists(path):
        os.remove(path)
