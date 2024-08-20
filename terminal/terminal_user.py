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


class EpicTerminalUser():

    def __init__(self, user, base):
        self.user = user
        self.epic = base

    def choice_commercial(self) -> str:
        """
            - ask to confirm a selection
            - read the list in database
            - ask to choose a commercial

        Returns:
            str: commercial username
        """
        # select a commercial
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
        read data of the current user and display it
        """
        DataView.display_profil(self.user)

    @is_authenticated
    def update_profil(self):
        """
            - ask confirm to update data
            - show profil data
            - ask new data
            - update database
            - display new data
        """
        result = UserView.prompt_confirm_profil()
        if result:
            DataView.display_profil(self.user)
            profil = UserView.prompt_data_profil(False, False, False)
            self.epic.db_users.update_profil(self.user, profil)
            DataView.display_profil(self.user)
            DataView.display_data_update()

    @is_authenticated
    @is_gestion
    @is_admin
    def list_of_employees(self) -> None:
        """
        read database of employees and display it
        """
        users = self.epic.db_users.get_users()
        UserView.display_list_users(users)

    @is_authenticated
    @is_gestion
    @is_admin
    def create_new_user(self) -> None:
        """
            - prompt data of employee
            - update database
        """
        roles = self.epic.db_users.get_roles()
        try:
            data = UserView.prompt_data_user(roles)
            self.epic.epic_users.create_user(data)
        except KeyboardInterrupt:
            DataView.display_interupt()

    @is_authenticated
    @is_gestion
    @is_admin
    def update_user_password(self) -> None:
        """
            - ask to select an employee
            - ask the new password
            - update database
        """
        users = self.epic.db_users.get_users()
        users_usernames = [e.username for e in users]
        username = UserView.prompt_user(users_usernames)
        password = UserView.prompt_password()
        self.epic.db_users.update_user(username, password=password)

    @is_authenticated
    @is_gestion
    @is_admin
    def inactivate_user(self) -> None:
        """
            - ask to select an employee
            - update database
        """
        users = self.epic.db_users.get_users()
        user_usernames = [e.username for e in users]
        username = UserView.prompt_user(user_usernames)
        self.epic.db_users.inactivate(username, self.user)
