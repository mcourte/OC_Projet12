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
        """
        Demande une confirmation pour sélectionner un commercial.

        Args:
            **kwargs: Arguments supplémentaires pour la fonction `questionary.confirm`.

        Returns:
            bool: `True` si l'utilisateur confirme la sélection, sinon `False`.
        """
        return questionary.confirm(
            "Souhaitez-vous sélectionner un commercial ?", **kwargs).ask()

    @classmethod
    def prompt_commercial(cls, all_commercials) -> str:
        """
        Demande à l'utilisateur de sélectionner un commercial dans une liste.

        Args:
            all_commercials (list): Liste des noms d'utilisateur des commerciaux.

        Returns:
            str: Nom d'utilisateur du commercial sélectionné.
        """
        return questionary.select(
            "Choix du commercial:",
            choices=all_commercials,
        ).ask()

    @classmethod
    def prompt_confirm_support(cls, **kwargs) -> bool:
        """
        Demande une confirmation pour sélectionner un support.

        Args:
            **kwargs: Arguments supplémentaires pour la fonction `questionary.confirm`.

        Returns:
            bool: `True` si l'utilisateur confirme la sélection, sinon `False`.
        """
        return questionary.confirm(
            "Souhaitez-vous sélectionner un support ?", **kwargs).ask()

    @classmethod
    def prompt_gestion(cls, alls) -> str:
        """
        Demande à l'utilisateur de sélectionner un gestionnaire dans une liste.

        Args:
            alls (list): Liste des noms d'utilisateur des gestionnaires.

        Returns:
            str: Nom d'utilisateur du gestionnaire sélectionné.
        """
        return questionary.select(
            "Choix du gestionnaire:",
            choices=alls
        ).ask()

    @classmethod
    def prompt_user(cls, all_users) -> str:
        """
        Demande à l'utilisateur de sélectionner un employé dans une liste.

        Args:
            all_users (list): Liste des noms d'employés.

        Returns:
            str: Nom de l'employé sélectionné.
        """
        return questionary.select(
            "Sélectionnez un employé:",
            choices=all_users
        ).ask()

    @classmethod
    def prompt_select_support(cls, values) -> str:
        """
        Demande à l'utilisateur de sélectionner un support dans une liste.

        Args:
            values (list): Liste des noms d'utilisateur des supports.

        Returns:
            str: Nom d'utilisateur du support sélectionné.
        """
        return PromptView.prompt_select(
            "Choix du support:", values)

    @classmethod
    def prompt_confirm_profil(cls, **kwargs) -> bool:
        """
        Demande une confirmation pour modifier les données de l'utilisateur.

        Args:
            **kwargs: Arguments supplémentaires pour la fonction `questionary.confirm`.

        Returns:
            bool: `True` si l'utilisateur confirme la modification, sinon `False`.
        """
        return questionary.confirm(
            "Souhaitez-vous modifier vos données ?", **kwargs).ask()

    @classmethod
    def prompt_data_profil(
            cls, user_raquired=True, password_required=True,
            email_required=True) -> dict:
        """
        Demande les données pour un employé.

        Args:
            user_raquired (bool, optional): Si le nom d'utilisateur est requis. Defaults to True.
            password_required (bool, optional): Si le mot de passe est requis. Defaults to True.
            email_required (bool, optional): Si l'email est requis. Defaults to True.

        Raises:
            KeyboardInterrupt: Si l'utilisateur interrompt la saisie avec Ctrl+C.

        Returns:
            dict: Dictionnaire avec les données saisies, par exemple :
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
        """
        Demande un nouveau mot de passe et sa confirmation.

        Args:
            **kwargs: Arguments supplémentaires pour la fonction `questionary.password`.

        Raises:
            KeyboardInterrupt: Si l'utilisateur interrompt la saisie avec Ctrl+C.

        Returns:
            str: Le nouveau mot de passe saisi.
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
        """
        Demande à l'utilisateur de sélectionner un rôle dans une liste.

        Args:
            all_roles (list): Liste des noms de rôles.

        Returns:
            str: Nom du rôle sélectionné.
        """
        role = questionary.select(
            "Role:",
            choices=all_roles,
        ).ask()
        return role

    @classmethod
    def prompt_data_user(cls, all_roles) -> dict:
        """
        Demande les données pour un nouvel employé et son rôle.

        Args:
            all_roles (list): Liste des noms de rôles disponibles.

        Returns:
            dict: Dictionnaire avec les données saisies, par exemple :
            {'username': username, 'password': password,
            'email': email, 'role': "Manager"}
        """
        data = cls.prompt_data_profil()
        data['role'] = cls.prompt_role(all_roles)
        return data

    @classmethod
    def display_list_users(
            cls, all_users, pager=True) -> None:
        """
        Affiche une liste des employés.

        Args:
            all_users (list): Liste des instances d'employés.
            pager (bool, optional): Si la pagination est nécessaire. Defaults to True.
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
