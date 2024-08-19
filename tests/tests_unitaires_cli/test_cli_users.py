import pytest
from click.testing import CliRunner
import os
import sys
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from cli.user_cli import add_user, list_users
from controllers.user_controller import EpicUserBase
from models.entities import Base

# Création d'une base de données en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=db_engine)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def mock_user_base():
    with patch('controllers.user_controller.EpicUserBase') as mock:
        mock_instance = mock.return_value
        mock_instance.authenticate.return_value = True
        yield mock_instance


@pytest.fixture
def temp_file():
    import tempfile
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_add_user_with_temp_file(mock_user_base, temp_file):
    runner = CliRunner()

    # Écrire une configuration fictive ou des données dans le fichier temporaire
    with open(temp_file, 'w') as f:
        f.write('temporary test data')

    # Simuler la création d'un utilisateur
    mock_user_base.create_user.return_value = type('User', (object,), {'username': 'jdoe'})
    result = runner.invoke(add_user, ['John', 'Doe', 'Admin', 'password', '--config', temp_file])

    assert result.exit_code == 0
    assert 'Utilisateur tuser ajouté avec succès' in result.output

    # Vérifier le contenu du fichier temporaire (si applicable)
    with open(temp_file, 'r') as f:
        content = f.read()
        assert 'temporary test data' in content


def test_add_user_failure_with_temp_file(mock_user_base, temp_file):
    runner = CliRunner()

    # Écrire une configuration fictive ou des données dans le fichier temporaire
    with open(temp_file, 'w') as f:
        f.write('some failure config')

    mock_user_base.return_value.create_user.side_effect = ValueError("Error")
    result = runner.invoke(add_user, ['John', 'Doe', 'Admin', 'password', '--config', temp_file])

    assert result.exit_code == 0
    assert 'Error' in result.output


def test_list_users_with_temp_file(mock_user_base, temp_file):
    runner = CliRunner()

    # Simuler le retour des utilisateurs
    mock_user_base.return_value.get_all_users.return_value = [
        type('User', (object,), {'first_name': 'John', 'last_name': 'Doe',
                                 'username': 'jdoe', 'email': 'jdoe@epic.com'})
    ]

    # Simuler l'écriture de la liste des utilisateurs dans un fichier temporaire
    result = runner.invoke(list_users, ['--output', temp_file])

    assert result.exit_code == 0

    # Vérifier le contenu du fichier temporaire pour s'assurer qu'il contient les utilisateurs listés
    with open(temp_file, 'r') as f:
        output = f.read()
        assert 'John Doe (jdoe) - jdoe@epic.com' in output
