import io
import sys
import pytest
import os
from unittest.mock import patch
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.error_view import ErrorView


@patch('views.error_view.error_console')
def test_display_error_login(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_error_login()

    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout

    assert output == 'ERROR : Utilisateur ou mot de passe inconnu'


@patch('views.error_view.error_console')
def test_display_token_expired(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_token_expired()

    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout

    assert output == 'ERROR : Token expiré ! Veuillez vous reconnecter.\nCommande : python epicevent.py login'


@patch('views.error_view.error_console')
def test_display_token_invalid(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_token_invalid()

    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout

    assert output == 'ERROR : Token invalide ! Veuillez vous reconnecter.'


@patch('views.error_view.error_console')
def test_display_not_commercial(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_not_commercial()

    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout

    assert output == 'ERROR : Accès refusé, rôle commercial requis.'


@patch('views.error_view.error_console')
def test_display_not_manager(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_not_manager()

    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout

    assert output == 'ERROR : Accès refusé, rôle manager requis.'


@patch('views.error_view.error_console')
def test_display_not_support(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_not_support()

    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout

    assert output == 'ERROR : Accès refusé, rôle support requis.'


@patch('views.error_view.error_console')
def test_display_error_exception(mock_console):
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    mock_console.print = lambda msg: sys.stdout.write(msg + '\n')
    ErrorView.display_error_exception('Test exception message')

    output = sys.stdout.getvalue().strip().split('\n')
    sys.stdout = original_stdout

    assert output == ['Une erreur est survenue dans le traitement', 'Test exception message']
