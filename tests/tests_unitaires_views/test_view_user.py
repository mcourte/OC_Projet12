import pytest
from unittest.mock import patch, MagicMock
from views.user_view import UserView
from views.data_view import DataView
from enum import Enum


class RoleEnum(Enum):
    ADM = 'Admin'
    COM = 'Commercial'
    SUP = 'Support'
    GES = 'Gestion'


class StateEnum(Enum):
    A = 'Actif'
    I = 'Inactif'


# Simulation des données pour les tests
class MockUser:
    def __init__(self, last_name, first_name, epicuser_id, username, email, role, state):
        self.last_name = last_name
        self.first_name = first_name
        self.epicuser_id = epicuser_id
        self.username = username
        self.email = email
        self.role = RoleEnum(role)
        self.state = StateEnum(state)


class MockRole:
    def __init__(self, value):
        self.value = value


class MockState:
    def __init__(self, value):
        self.value = value


users = [
    MockUser('John', 'Doe', 1, 'jdoe', 'jdoe@epic.com', RoleEnum('Admin'), StateEnum('Actif')),
    MockUser('Jane', 'Doe', 2, 'jdoe1', 'jdoe1@epic.com', RoleEnum('Commercial'), StateEnum('Actif')),
]


class MockSupport:
    def __init__(self, username):
        self.username = username


# Tests unitaires
@pytest.fixture
def setup_commercials():
    return ['commercial1', 'commercial2', 'commercial3']


@patch('questionary.select')
def test_prompt_commercial(mock_select, setup_commercials):
    mock_select.return_value.ask.return_value = 'commercial2'
    selected_commercial = UserView.prompt_commercial(setup_commercials)
    assert selected_commercial == 'commercial2'


@patch('questionary.select')
def test_prompt_user(mock_select):
    mock_select.return_value.ask.return_value = 'user1'
    all_users = ['user1', 'user2', 'user3']
    selected_user = UserView.prompt_user(all_users)
    assert selected_user == 'user1'


@patch('questionary.select')
def test_prompt_select_support(mock_select):
    mock_select.return_value.ask.return_value = 'support1'
    supports = [MockSupport('support1'), MockSupport('support2')]
    selected_support = UserView.prompt_select_support(supports)
    assert selected_support == 'support1'


@patch('questionary.confirm')
def test_prompt_confirm_profil(mock_confirm):
    mock_confirm.return_value.ask.return_value = True
    confirmation = UserView.prompt_confirm_profil()
    assert confirmation is True


@patch('questionary.password')
def test_prompt_password(mock_password):
    mock_password.return_value.ask.return_value = 'newpassword'
    result = UserView.prompt_password()
    assert result == {'password': 'newpassword'}


@patch('questionary.select')
def test_prompt_role(mock_select):
    mock_select.return_value.ask.return_value = 'Admin'
    role = UserView.prompt_role()
    assert role == 'Admin'


def test_display_list_users(mocker):
    mock_print = mocker.patch("rich.console.Console.print")
    mock_user = MagicMock()
    mock_user.first_name = "Jane"
    mock_user.last_name = "Doe"
    mock_user.epicuser_id = 1
    mock_user.username = "jdoe"
    mock_user.email = "jane.doe@example.com"
    mock_user.role.value = "Admin"
    mock_user.state.value = "Active"

    UserView.display_list_users([mock_user])

    # Vérifiez que print a été appelé une fois
    mock_print.assert_called_once()


@patch('questionary.text')
def test_prompt_update_user(mock_text):
    mock_text.return_value.ask.side_effect = ['John', 'Doe', 'newpassword']
    new_first_name, new_last_name, new_password = UserView.prompt_update_user(None)
    assert new_first_name == 'John'
    assert new_last_name == 'Doe'
    assert new_password == 'newpassword'


@patch('questionary.select')
def test_prompt_select_gestion(mock_select):
    mock_select.return_value.ask.return_value = 'jdoe'
    gestions = [MockUser('John', 'Doe', 1, 'jdoe', 'jdoe@epic.com', RoleEnum('Gestion'), StateEnum('Actif')),
                MockUser('Jane', 'Doe', 2, 'jdoe1', 'jdoe1@epic.com', RoleEnum('Gestion'), StateEnum('Actif'))]
    selected_gestion = UserView.prompt_select_gestion(gestions)
    assert selected_gestion == 'jdoe'


@patch('questionary.select')
def test_prompt_select_users(self, mock_select):
    # Liste factice d'utilisateurs
    mock_users = [
        MagicMock(first_name='John', last_name='Doe'),
        MagicMock(first_name='Jane', last_name='Smith')
    ]

    # Définir la réponse de questionary
    mock_select.return_value.ask.return_value = "John - Doe"

    # Appeler la méthode
    selected_user = DataView.prompt_select_users(mock_users)

    # Vérifier que l'utilisateur correct a été sélectionné
    self.assertEqual(selected_user.first_name, 'John')
    self.assertEqual(selected_user.last_name, 'Doe')

    # Vérifier que questionary.select a bien été appelé
    mock_select.assert_called_once()
