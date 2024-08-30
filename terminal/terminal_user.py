import os
import sys
import sqlalchemy.orm
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import is_authenticated, requires_roles, sentry_activate
from views.user_view import UserView
from views.data_view import DataView
from views.console_view import console
from controllers.user_controller import EpicUserBase, EpicUser


class EpicTerminalUser:
    """
    Classe pour gérer les utilisateurs depuis l'interface terminal.
    """

    def __init__(self, base, session, current_user=None):
        """
        Initialise la classe EpicTerminalUser avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        user (EpicUser) : L'utilisateur actuellement connecté.
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        """
        self.epic = base
        self.session = session
        self.current_user = current_user

    @sentry_activate
    @is_authenticated
    def show_profil(self, session) -> None:
        if self.current_user is None:
            text = "Erreur : Aucun utilisateur connecté."
            console.print(text, style="bold red")
            return
        user = session.query(EpicUser).filter_by(username=self.current_user.username).first()
        if user:
            DataView.display_profil(user)
        else:
            text = "Utilisateur non trouvé dans la base de données."
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    def update_profil(self, session):
        """
        Permet de mettre à jour le profil de l'utilisateur.
        """
        result = UserView.prompt_confirm_profil()
        if result:
            # Afficher le profil actuel de l'utilisateur
            DataView.display_profil(self.current_user)

            # Demander les nouvelles données de profil (retourne maintenant un tuple)
            new_first_name, new_last_name, new_password = UserView.prompt_update_user(self.current_user)
            print(f"profil : {new_first_name}, {new_last_name}, {new_password}")
            print(f"type profil : {type((new_first_name, new_last_name, new_password))}")
            print(f"self.current_user : {type(self.current_user)}")
            print(f"session: {session}")
            print(f"type session: {type(session)}")

            try:
                # Vérifiez que self.current_user est bien un objet EpicUser et pas un dict
                if not isinstance(self.current_user, EpicUser):
                    print("Erreur : l'utilisateur actuel n'est pas un objet EpicUser.")
                    return

                # Vérifiez que session est bien une instance de SQLAlchemy scoped_session
                if not isinstance(session, sqlalchemy.orm.scoping.scoped_session):
                    raise ValueError("La session passée n'est pas une instance de SQLAlchemy scoped_session.")

                # Obtenez une instance réelle de la session
                actual_session = session()

                # Mettre à jour les informations de l'utilisateur
                if new_first_name:
                    self.current_user.first_name = new_first_name
                if new_last_name:
                    self.current_user.last_name = new_last_name
                if new_password:
                    self.current_user.set_password(new_password)

                # Sauvegarder les changements dans la session
                actual_session.commit()

                # Afficher le profil mis à jour
                DataView.display_profil(self.current_user)
                DataView.display_data_update()
            except Exception as e:
                print(f"Erreur lors de la mise à jour du profil : {str(e)}")
                session.rollback()

    @sentry_activate
    @is_authenticated
    def list_of_users(self, session) -> None:
        """
        Affiche la liste de tous les utilisateurs de la base de données.

        - Lit les données des utilisateurs dans la base de données.
        - Affiche la liste des utilisateurs.
        """

        users = self.session.query(EpicUser).all()
        UserView.display_list_users(users)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
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

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def inactivate_user(self, session) -> None:
        """
        Désactive un utilisateur.

        - Demande de sélectionner un utilisateur.
        - Met à jour la base de données pour désactiver l'utilisateur sélectionné.
        """
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return

        users = session.query(EpicUser).all()
        user_usernames = [e.username for e in users]
        username = UserView.prompt_user(user_usernames)

        # Utiliser l'instance de EpicUserBase pour appeler set_inactivate
        epic_user_base = EpicUserBase(session)
        epic_user_base.set_activate_inactivate(session, username)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
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
