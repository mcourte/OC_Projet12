import questionary
import re
from rich.table import Table
from rich import box
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.console_view import console
from views.prompt_view import PromptView
from views.regexformat import regexformat


class UserView:

    @classmethod
    def prompt_confirm_commercial(cls, **kwargs) -> bool:
        """ ask to confirm a selection of a commercial

        Returns:
            bool: True or False
        """
        return questionary.confirm(
            "Souhaitez-vous sélectionner un commercial ?", **kwargs).ask()

    @classmethod
    def prompt_commercial(cls, all_commercials) -> str:
        """ ask to select a commercial in a list

        Args:
            all_commercials (list): list of username

        Returns:
            str: return the username selected
        """
        return questionary.select(
            "Choix du commercial:",
            choices=all_commercials,
        ).ask()

    @classmethod
    def prompt_confirm_support(cls, **kwargs) -> bool:
        """ ask to confirm a support selection

        Returns:
            bool: True or False
        """
        return questionary.confirm(
            "Souhaitez-vous sélectionner un support ?", **kwargs).ask()

    @classmethod
    def prompt_gestion(cls, alls) -> str:
        """ ask to select a manager in the

        Args:
            alls (list): list of manager username

        Returns:
            str: the manager username selected
        """
        return questionary.select(
            "Choix du gestionnaire:",
            choices=alls
        ).ask()

    @classmethod
    def prompt_user(cls, all_users) -> str:
        """ ask to select an employee in a list

        Args:
            all_employees (list): list of employee name

        Returns:
            str: return the employee name selected
        """
        return questionary.select(
            "Sélectionnez un employé:",
            choices=all_users
        ).ask()

    @classmethod
    def prompt_select_support(cls, values) -> str:
        """ ask to select a support in a list

        Args:
            values (list): list of support username

        Returns:
            str: the support username selected
        """
        return PromptView.prompt_select(
            "Choix du support:", values)

    @classmethod
    def prompt_confirm_profil(cls, **kwargs) -> bool:
        """ ask to confirm an update of data

        Returns:
            bool: True or False
        """
        return questionary.confirm(
            "Souhaitez-vous modifier vos données ?", **kwargs).ask()

    @classmethod
    def prompt_data_profil(
            cls, user_raquired=True, password_required=True,
            email_required=True) -> dict:
        """ ask the data for an employee

        Raises:
            KeyboardInterrupt: ctrl+C is enter

        Returns:
            dict: example:
            {'username': username, 'password': password, 'email': email}
        """
        username = questionary.text(
            "Identifiant:",
            validate=lambda text: True
            if re.match(regexformat['alpha_nospace'][0], text)
            else regexformat['alpha_nospace'][1]).ask()
        if user_raquired and username is None:
            raise KeyboardInterrupt

        try:
            password = cls.prompt_password()
        except KeyboardInterrupt:
            if password_required:
                raise KeyboardInterrupt
            else:
                password = None

        email = questionary.text(
            "Email:",
            validate=lambda text: True
            if re.match(regexformat['email'][0], text)
            else regexformat['email'][1]).ask()
        if email_required and email is None:
            raise KeyboardInterrupt

        return {'username': username, 'password': password, 'email': email}

    @classmethod
    def prompt_password(cls, **kwargs) -> str:
        """ ask for a new password with confirm

        Raises:
            KeyboardInterrupt: ctr+C enter

        Returns:
            str: the new password
        """

        password = questionary.password(
            "Mot de passe:",
            validate=lambda text: True
            if re.match(regexformat['password'][0], text)
            else regexformat['password'][1],
            **kwargs).ask()
        if password is None:
            raise KeyboardInterrupt

        result = questionary.password(
            "Confirmez le mot de passe:",
            validate=lambda text: True if text == password
            else "Les mots de passe ne correspondent pas",
            **kwargs).ask()

        if result is None:
            raise KeyboardInterrupt
        return password

    @classmethod
    def prompt_role(cls, all_roles) -> str:
        """ask for a role in a list

        Args:
            all_roles (str): list of role name

        Returns:
            str: the name of the role selected
        """
        role = questionary.select(
            "Role:",
            choices=all_roles,
        ).ask()
        return role

    @classmethod
    def prompt_data_user(cls, all_roles) -> dict:
        """ ask the data for a new employee
        and ask his role

        Args:
            all_roles (list): list of role name

        Returns:
            dict: example
            {'username': username, 'password': password,
            'email': email 'role": "Manager"}
        """
        data = cls.prompt_data_profil()
        data['role'] = cls.prompt_role(all_roles)
        return data

    @classmethod
    def display_list_users(
            cls, all_users, pager=True) -> None:
        """ Display a list of employees

        Args:
            all_employees (list): list of Employee instance
            pager (bool, optional): if pager is needed. Defaults to True.
        """
        table = Table(title="Liste des employés", box=box.SQUARE)
        table.add_column("Département")
        table.add_column("Id")
        table.add_column("Identifiant")
        table.add_column("Email")
        table.add_column("Role")
        table.add_column("Statut")

        for e in all_users:
            table.add_row(
                e.name,
                str(e.id), e.username, e.email, e.role.value, e.state.value)

        if pager:
            with console.pager():
                console.print(table)
        else:
            console.print(table)
