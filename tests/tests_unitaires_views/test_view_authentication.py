import pytest
from unittest.mock import patch, MagicMock
import os
import io
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.authentication_view import AuthenticationView


# Test de `display_welcome`
def test_display_welcome():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    AuthenticationView.display_welcome('testuser')
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert "Bienvenue testuser sur EpicEvent" in output


# Test de `display_waiting_databasecreation`
def test_display_waiting_databasecreation():
    mock_function = MagicMock()

    with patch('views.authentication_view.console.status') as mock_status:
        mock_status_instance = MagicMock()
        mock_status.return_value.__enter__.return_value = mock_status_instance

        original_stdout = sys.stdout
        sys.stdout = io.StringIO()

        AuthenticationView.display_waiting_databasecreation(mock_function, ('arg1', 'arg2'))
        output = sys.stdout.getvalue().strip()
        sys.stdout = original_stdout

        mock_function.assert_called_once_with('arg1', 'arg2')

        print(f"DEBUG OUTPUT: {output}")

        assert "Création de la base de données ..." in output


# Test de `display_login`
def test_display_login():
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    sys.stdin = io.StringIO('testuser\ntestpass\n')
    sys.stdout = io.StringIO()

    username, password = AuthenticationView.display_login()

    output = sys.stdout.getvalue().strip()
    sys.stdin = original_stdin
    sys.stdout = original_stdout

    assert username == 'testuser'
    assert password == 'testpass'
    assert 'Identifiant:' in output
    assert 'Mot de passe:' in output


# Test de `display_database_connection`
def test_display_database_connection():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    AuthenticationView.display_database_connection('TestDB')
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'La base TestDB est opérationnelle'


# Test de `prompt_baseinit`
@patch('views.authentication_view.questionary.text')
@patch('views.authentication_view.questionary.password')
def test_prompt_baseinit(mock_password, mock_text):
    mock_text.return_value.ask.side_effect = ['testdb', 'admin', '5432']
    mock_password.return_value.ask.side_effect = ['password']

    result = AuthenticationView.prompt_baseinit()

    assert result == ('testdb', 'admin', 'password', '5432')


# Test de `prompt_manager`
@patch('views.authentication_view.questionary.text')
@patch('views.authentication_view.questionary.password')
def test_prompt_manager(mock_password, mock_text):
    mock_text.return_value.ask.side_effect = ['manager']
    mock_password.return_value.ask.side_effect = ['password', 'password']

    result = AuthenticationView.prompt_manager()

    assert result == ('manager', 'password')


# Test de `prompt_confirm_testdata`
@patch('views.authentication_view.questionary.confirm')
def test_prompt_confirm_testdata(mock_confirm):
    mock_confirm.return_value.ask.return_value = True

    result = AuthenticationView.prompt_confirm_testdata()

    assert result is True
