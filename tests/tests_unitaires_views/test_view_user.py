import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import EpicUser, Admin
from views.console_view import console
from views.user_view import UserView  # Assurez-vous que le chemin est correct
from rich.table import Table
import questionary
from config_init import Base


# Configuration de la base de données en mémoire pour les tests
@pytest.fixture(scope='module')
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Création d'utilisateurs actifs
    admin = Admin(first_name="Admin", last_name="User", password="password", email="auser@epic.com",
                  username="auser", state="A", role="ADM")
    commercial = EpicUser(first_name="Commercial", last_name="User", password="password", email="cuser@epic.com",
                          username="cuser", state="A", role="COM")
    session.add(admin)
    session.add(commercial)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def all_users(db_session):
    return db_session.query(EpicUser).all()


@pytest.fixture
def all_commercials(db_session):
    return db_session.query(EpicUser).filter_by(role='COM').all()


@pytest.fixture
def all_gestions(db_session):
    return db_session.query(EpicUser).filter_by(role='GES').all()


def test_prompt_commercial(monkeypatch, all_commercials):
    def mock_select(prompt, choices):
        return choices[0].username  # Assurez-vous que choices contient des objets avec l'attribut username

    monkeypatch.setattr(questionary, 'select', mock_select)

    result = UserView.prompt_commercial([user.username for user in all_commercials])
    assert result == all_commercials[0].username


def test_prompt_user(monkeypatch, all_users):
    def mock_select(prompt, choices):
        return choices[0].username  # Assurez-vous que choices contient des objets avec l'attribut username

    monkeypatch.setattr(questionary, 'select', mock_select)

    result = UserView.prompt_user([user.username for user in all_users])
    assert result == all_users[0].username


def test_prompt_select_support(monkeypatch, all_users):
    def mock_select(prompt, choices):
        return choices[0]  # Assurez-vous que choices contient des valeurs valides pour le test

    monkeypatch.setattr(questionary, 'select', mock_select)

    result = UserView.prompt_select_support(all_users)
    assert result == all_users[0].username


def test_prompt_confirm_profil(monkeypatch):
    def mock_confirm(prompt, **kwargs):
        return True  # Return a boolean value

    monkeypatch.setattr(questionary, 'confirm', mock_confirm)

    result = UserView.prompt_confirm_profil()
    assert result is True


def test_prompt_data_profil(monkeypatch):
    def mock_text(prompt, validate):
        if prompt == "Prénom:":
            return "John"
        elif prompt == "Nom:":
            return "Doe"

    monkeypatch.setattr(questionary, 'text', mock_text)

    result = UserView.prompt_data_profil()
    assert result == {'first_name': 'John', 'last_name': 'Doe'}


def test_prompt_password(monkeypatch):
    def mock_password(prompt, validate):
        if prompt == "Mot de passe:":
            return "password123"
        elif prompt == "Confirmez le mot de passe:":
            return "password123"

    monkeypatch.setattr(questionary, 'password', mock_password)

    result = UserView.prompt_password()
    assert result['password'] == 'password123'


def test_prompt_role(monkeypatch):
    def mock_select(prompt, choices):
        return 'Admin'  # Ensure the mock returns a valid role

    monkeypatch.setattr(questionary, 'select', mock_select)

    result = UserView.prompt_role()
    assert result == 'Admin'


def test_display_list_users(monkeypatch, all_users):
    def mock_print(table):
        assert isinstance(table, Table)  # Ensure the mock captures the table object

    monkeypatch.setattr(console, 'print', mock_print)

    UserView.display_list_users(all_users)


def test_prompt_update_user(monkeypatch):
    def mock_text(prompt):
        if "Nouveau Prénom" in prompt:
            return "Jane"
        elif "Nouveau Nom" in prompt:
            return "Smith"
        elif "Nouveau mot de passe" in prompt:
            return "newpassword"

    monkeypatch.setattr(questionary, 'text', mock_text)

    user = EpicUser(first_name="John", last_name="Doe", username="jdoe", email="jdoe@example.com")
    new_first_name, new_last_name, new_password = UserView.prompt_update_user(user)

    assert new_first_name == "Jane"
    assert new_last_name == "Smith"
    assert new_password == "newpassword"


def test_prompt_select_gestion(monkeypatch, all_gestions):
    def mock_select(prompt, choices):
        if choices:
            return choices[0]  # Ensure there are choices available

    monkeypatch.setattr(questionary, 'select', mock_select)

    result = UserView.prompt_select_gestion(all_gestions)
    if all_gestions:
        assert result == all_gestions[0].username
    else:
        assert result is None


def test_prompt_select_users(monkeypatch, all_users):
    def mock_select(prompt, choices):
        return choices[0]  # Ensure the mock returns a valid user object

    monkeypatch.setattr(questionary, 'select', mock_select)

    result = UserView.prompt_select_users(all_users)
    assert result == all_users[0]
