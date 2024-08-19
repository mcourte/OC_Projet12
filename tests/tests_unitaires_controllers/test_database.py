import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Sauvegarder la valeur actuelle de DATABASE_URL
original_database_url = os.getenv('DATABASE_URL')

# Définir l'URL pour les tests
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:password@localhost:5432/app_db'


@pytest.fixture(scope='module', autouse=True)
def restore_database_url():
    yield
    if original_database_url:
        os.environ['DATABASE_URL'] = original_database_url
    else:
        del os.environ['DATABASE_URL']


def test_database_connection():
    try:
        engine = create_engine(os.getenv('DATABASE_URL'))
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        result = session.execute(text('SELECT 1'))
        assert result.fetchone() is not None

        session.close()
        engine.dispose()

        assert True

    except Exception as e:
        pytest.fail(f"Erreur: {e}")
