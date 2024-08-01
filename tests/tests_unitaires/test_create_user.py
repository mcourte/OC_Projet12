import pytest
from controllers.user_controller import UserController
from models.user import User


@pytest.fixture
def user_controller(session):
    return UserController(session)


# lambda : permet de simuler le comportement sans avoir de BD
def test_create_user_valid_role(user_controller):
    first_name = "Romain"
    last_name = "Martin"
    role = "com"
    password = "password123"

    # Simulez le comportement attendu pour User
    User.get_all_roles = lambda: ["com", "user"]
    User.generate_unique_username = lambda session, first, last: f"{first}.{last}".lower()

    # Appel de la méthode de création d'utilisateur
    try:
        user_controller.create_user(first_name, last_name, role, password)
        assert True
    except Exception as e:
        pytest.fail(f"Exception inattendue : {e}")


def test_create_user_invalid_role(user_controller):
    first_name = "Romain"
    last_name = "Martin"
    role = "commercial"
    password = "password123"
    User.get_all_roles = lambda: ["com", "user"]

    with pytest.raises(ValueError, match=f"Rôle invalide, erreur: {role}"):
        user_controller.create_user(first_name, last_name, role, password)
