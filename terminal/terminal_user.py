import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import is_authenticated, is_gestion, is_admin
from views.user_view import UserView
from views.data_view import DataView


class EpicTerminalUser:
    """
    Classe pour gérer les utilisateurs depuis l'interface terminal.
    """

    def __init__(self, user, base):
        """
        Initialise la classe EpicTerminalUser avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        user (EpicUser) : L'utilisateur actuellement connecté.
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        """
        self.user = user
        self.epic = base

    def choice_commercial(self) -> str:
        """
        Permet de choisir un commercial parmi ceux disponibles.

        - Demande de confirmer une sélection.
        - Lit la liste des commerciaux dans la base de données.
        - Demande de choisir un commercial.

        Retourne :
        -----------
        str : Le nom d'utilisateur du commercial sélectionné.
        """
        cname = None
        result = UserView.prompt_confirm_commercial()
        if result:
            commercials = self.epic.db_users.get_commercials()
            commercials_name = [c.username for c in commercials]
            cname = UserView.prompt_commercial(commercials_name)
        return cname

    @is_authenticated
    def show_profil(self) -> None:
        """
        Affiche le profil de l'utilisateur actuellement connecté.
        """
        DataView.display_profil(self.user)

    @is_authenticated
    def update_profil(self):
        """
        Permet de mettre à jour le profil de l'utilisateur.

        - Demande une confirmation pour mettre à jour les données.
        - Affiche les données du profil actuel.
        - Demande les nouvelles données.
        - Met à jour la base de données avec les nouvelles données.
        - Affiche les nouvelles données mises à jour.
        """
        result = UserView.prompt_confirm_profil()
        if result:
            DataView.display_profil(self.user)
            profil = UserView.prompt_data_profil(False, False, False)
            self.epic.db_users.update_user(self.user, profil)
            DataView.display_profil(self.user)
            DataView.display_data_update()

    @is_authenticated
    @is_gestion
    @is_admin
    def list_of_users(self) -> None:
        """
        Affiche la liste de tous les utilisateurs de la base de données.

        - Lit les données des utilisateurs dans la base de données.
        - Affiche la liste des utilisateurs.
        """
        users = self.epic.db_users.get_all_users()
        UserView.display_list_users(users)

    @is_authenticated
    @is_gestion
    @is_admin
    def create_new_user(self) -> None:
        """
        Crée un nouvel utilisateur.

        - Demande les données de l'employé.
        - Met à jour la base de données avec les nouvelles données d'utilisateur.
        """
        roles = self.epic.db_users.get_roles()
        try:
            data = UserView.prompt_data_user(roles)
            self.epic.db_users.create_user(data)
        except KeyboardInterrupt:
            DataView.display_interupt()

    @is_authenticated
    @is_gestion
    @is_admin
    def update_user_password(self) -> None:
        """
        Met à jour le mot de passe d'un utilisateur.

        - Demande de sélectionner un utilisateur.
        - Demande le nouveau mot de passe.
        - Met à jour la base de données avec le nouveau mot de passe.
        """
        users = self.epic.db_users.get_all_users()
        users_usernames = [e.username for e in users]
        username = UserView.prompt_user(users_usernames)
        password = UserView.prompt_password()
        self.epic.db_users.update_user(username, password=password)

    @is_authenticated
    @is_gestion
    @is_admin
    def inactivate_user(self) -> None:
        """
        Désactive un utilisateur.

        - Demande de sélectionner un utilisateur.
        - Met à jour la base de données pour désactiver l'utilisateur sélectionné.
        """
        users = self.epic.db_users.get_all_users()
        user_usernames = [e.username for e in users]
        username = UserView.prompt_user(user_usernames)
        self.epic.db_users.inactivate(username, self.user)

    @is_authenticated
    @is_gestion
    @is_admin
    def find_by_username(self):
        """
        Trouve un utilisateur par son nom d'utilisateur.

        - Lit la liste des utilisateurs de la base de données.
        - Demande de sélectionner un utilisateur.

        Retourne :
        -----------
        str : Le nom d'utilisateur sélectionné.
        """
        users = self.epic.db_users.get_all_users()
        user_usernames = [e.username for e in users]
        username = UserView.prompt_user(user_usernames)
        return username
