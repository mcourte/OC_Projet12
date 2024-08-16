import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
print(parent_dir)
from models.entities import EpicUser


def test_password_validation():
    user = EpicUser(first_name="Magali", last_name="Courté", username="mcourte")
    password = "password"
    user.set_password(password)
    assert user.check_password(password), "Le mot de passe devrait être valide"


def test_password_functions():
    user = EpicUser(first_name="Magali", last_name="Courté", username="mcourte")
    password = "password"
    user.set_password(password)
    # Simulez l'enregistrement et la récupération depuis la base de données
    # user.password est maintenant un hachage, simulez la récupération
    assert user.check_password(password), "Le mot de passe devrait être valide"


def test_user_password():
    # Simulez la session de base de données
    user = EpicUser(first_name="Magali", last_name="Courté", username="mcourte")
    user.set_password("password")

    # Simulez l'enregistrement et la récupération
    assert user.check_password("password"), "Le mot de passe devrait être valide"
