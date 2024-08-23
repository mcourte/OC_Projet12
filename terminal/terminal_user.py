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
from controllers.user_controller import EpicUserBase, EpicUser


class EpicTerminalUser:
    """
    Classe pour gérer les utilisateurs depuis l'interface terminal.
    """

    def __init__(self, base, session):
        """
        Initialise la classe EpicTerminalUser avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        user (EpicUser) : L'utilisateur actuellement connecté.
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        """
        self.epic = base
        self.session = session
        self.current_user = None

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
            commercials = self.session.query(EpicUser).filter_by(role='COM').all()
            commercials_name = [c.username for c in commercials]
            cname = UserView.prompt_commercial(commercials_name)
        return cname

    def show_profil(self, session) -> None:
        """
        Affiche le profil de l'utilisateur actuellement connecté.
        """
        if not self.current_user:
            print("Utilisateur non authentifié (show_profil).")
            return

        print(f"Utilisateur authentifié : {self.current_user.username}")

        # Recherche de l'utilisateur dans la base de données
        user = session.query(EpicUser).filter_by(username=self.current_user.username).first()

        if user:
            print(f"Profil de l'utilisateur trouvé : {user.username}")
            DataView.display_profil(user)
        else:
            print("Utilisateur non trouvé dans la base de données.")

    @is_authenticated
    def update_profil(self, session):
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
            DataView.display_profil(self.current_user)
            profil = UserView.prompt_data_profil(False, False, False)
            EpicUserBase.update_user(self.current_user, profil)
            DataView.display_profil(self.current_user)
            DataView.display_data_update()

    @is_authenticated
    @is_gestion
    @is_admin
    def list_of_users(self, session) -> None:
        """
        Affiche la liste de tous les utilisateurs de la base de données.

        - Lit les données des utilisateurs dans la base de données.
        - Affiche la liste des utilisateurs.
        """
        users = self.session.query(EpicUser).all()
        UserView.display_list_users(users)

    @is_authenticated
    @is_admin
    @is_gestion
    def create_user(self, session) -> None:
        """
        Crée un nouvel utilisateur en utilisant la session fournie.
        """
        roles = EpicUserBase.get_roles(self)
        self.roles = roles
        try:
            data_role = UserView.prompt_data_role()
            data_profil = UserView.prompt_data_user()
            data_password = UserView.prompt_password()

            if isinstance(data_profil, dict) and isinstance(data_role, dict) and isinstance(data_password, dict):
                data_profil.update(data_password)
                data_profil.update(data_role)
                epic = EpicUserBase.create_user(session, data_profil)  # Passez la session ici
                self.epic = epic
            else:
                print("data_profil et data_role doivent être des dictionnaires.")
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
    def inactivate_user(self, session) -> None:
        """
        Désactive un utilisateur.

        - Demande de sélectionner un utilisateur.
        - Met à jour la base de données pour désactiver l'utilisateur sélectionné.
        """
        if session is None:
            print("Erreur : La session est non initialisée.")
            return

        users = self.session.query(EpicUser).all()
        user_usernames = [e.username for e in users]
        username = UserView.prompt_user(user_usernames)
        EpicUserBase.set_inactivate(self.current_user, username)

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
