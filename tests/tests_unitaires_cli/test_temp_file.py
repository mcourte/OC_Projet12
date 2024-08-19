import tempfile
import os
import pytest


@pytest.fixture
def temp_file():
    # Création d'un fichier temporaire
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    # Nettoyage du fichier temporaire après le test
    if os.path.exists(path):
        os.remove(path)


def test_cli_with_temp_file(temp_file):
    # Utilisez temp_file dans le test CLI
    with open(temp_file, 'w') as f:
        f.write('test data')

    # Assurez-vous que le fichier est utilisé correctement
    with open(temp_file, 'r') as f:
        assert f.read() == 'test data'
