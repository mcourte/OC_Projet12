import os
import sys
import pytest
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
print(parent_dir)
from models.entities import EpicUser
from controllers.user_controller import EpicUserBase


@pytest.fixture
def login_user(session):
    admin_user = EpicUser(
        first_name="Admin",
        last_name="User",
        username="adminuser",
        role="ADM",
        password="password123",
        email="adminuser@epic.com"
    )
    admin_user.set_password("password123")
    session.add(admin_user)
    session.commit()

    EpicUserBase.authenticated_user = admin_user

    yield admin_user

    EpicUserBase.authenticated_user = None


@pytest.fixture
def unique_username():
    return lambda first_name, last_name: f"{first_name[0]}{last_name}"


@pytest.fixture
def unique_email():
    return lambda first_name, last_name: f"{first_name[0]}{last_name}@epic.com"


def test_password_validation():
    user = EpicUser(first_name="Magali", last_name="Courté", username="mcourte")
    password = "password"
    user.set_password(password)
    assert user.check_password(password), "Le mot de passe devrait être valide"


def test_password_functions():
    user = EpicUser(first_name="Magali", last_name="Courté", username="mcourte")
    password = "password"
    user.set_password(password)
    assert user.check_password(password), "Le mot de passe devrait être valide"


def test_user_password():
    user = EpicUser(first_name="Magali", last_name="Courté", username="mcourte")
    user.set_password("password")

    assert user.check_password("password"), "Le mot de passe devrait être valide"
