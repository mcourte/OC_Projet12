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
    """
    Classe pour gérer l'affichage et les interactions concernant les utilisateurs.
    """

    @classmethod
    def prompt_commercial(cls, all_commercials) -> str:
        """
        Demande à l'utilisateur de sélectionner un commercial parmi une liste.

        Paramètres :
        ------------
        all_commercials (list) : Liste des noms d'utilisateur des commerciaux.

        Retourne :
        -----------
        str : Nom d'utilisateur du commercial sélectionné.
        """
        return questionary.select(
            "Choix du commercial:",
            choices=all_commercials,
        ).ask()

    @classmethod
    def prompt_user(cls, all_users) -> str:
        """
        Demande à l'utilisateur de sélectionner un employé parmi une liste.

        Paramètres :
        ------------
        all_users (list) : Liste des noms d'employés.

        Retourne :
        -----------
        str : Nom de l'employé sélectionné.
        """
        return questionary.select(
            "Sélectionnez un employé:",
            choices=all_users
        ).ask()

    @classmethod
    def prompt_select_support(cls, values) -> str:
        """
        Demande à l'utilisateur de sélectionner un support parmi une liste.

        Paramètres :
        ------------
        values (list) : Liste des noms d'utilisateur des supports.

        Retourne :
        -----------
        str : Nom d'utilisateur du support sélectionné.
        """
        return PromptView.prompt_select(
            "Choix du support:", values)

    @classmethod
    def prompt_confirm_profil(cls, **kwargs) -> bool:
        """
        Demande une confirmation à l'utilisateur pour modifier ses données.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la fonction `questionary.confirm`.

        Retourne :
        -----------
        bool : `True` si l'utilisateur confirme la modification, sinon `False`.
        """
        return questionary.confirm(
            "Souhaitez-vous modifier vos données ?", **kwargs).ask()

    @classmethod
    def prompt_data_profil(
            cls, first_name=True, last_name=True) -> dict:
        """
        Demande les informations de profil pour un employé.

        Paramètres :
        ------------
        first_name (bool, optional) : Si le prénom est requis. Defaults to True.
        last_name (bool, optional) : Si le nom est requis. Defaults to True.

        Lève :
        -------
        KeyboardInterrupt : Si l'utilisateur interrompt la saisie avec Ctrl+C.

        Retourne :
        -----------
        dict : Dictionnaire avec les données saisies, par exemple :
        {'first_name': first_name, 'last_name': last_name}
        """
        # Valide les formats regex (supposant qu'ils sont définis quelque part)

        first_name = questionary.text(
            "Prénom:",
            validate=lambda text: True
            if re.match(regexformat['all_nospace'][0], text)
            else regexformat['all_nospace'][1]).ask()
        if first_name is None:
            raise KeyboardInterrupt

        last_name = questionary.text(
            "Nom:",
            validate=lambda text: True
            if re.match(regexformat['all_letters'][0], text)
            else regexformat['all_letters'][1]).ask()
        if last_name is None:
            raise KeyboardInterrupt

        return {
            'first_name': first_name,
            'last_name': last_name,
        }

    @classmethod
    def prompt_password(cls, **kwargs) -> str:
        """
        Demande un nouveau mot de passe et sa confirmation.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la fonction `questionary.password`.

        Lève :
        -------
        KeyboardInterrupt : Si l'utilisateur interrompt la saisie avec Ctrl+C.

        Retourne :
        -----------
        str : Le nouveau mot de passe saisi.
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
        return {'password': password}

    @classmethod
    def prompt_role(cls) -> str:
        """
        Demande à l'utilisateur de sélectionner un rôle parmi une liste.

        Retourne :
        -----------
        str : Nom du rôle sélectionné.
        """
        all_roles = ['Admin', 'Commercial', 'Gestion', 'Support']
        role = questionary.select(
            "Role:",
            choices=all_roles,
        ).ask()
        return role

    @classmethod
    def prompt_data_user(cls) -> dict:
        """
        Demande les informations nécessaires pour ajouter un nouvel employé.

        Retourne :
        -----------
        dict : Dictionnaire avec les données saisies pour le nouvel employé.
        """
        data = cls.prompt_data_profil()
        return data

    @classmethod
    def prompt_data_role(cls) -> dict:
        """
        Demande le rôle pour un nouvel employé.

        Retourne :
        -----------
        dict : Dictionnaire avec les données saisies, par exemple :
        {'role': "Manager"}
        """
        data_role = cls.prompt_role()
        return {'role': data_role}

    @classmethod
    def display_list_users(cls, all_users, pager=False) -> None:
        """
        Affiche une liste des employés.

        Paramètres :
        ------------
        all_users (list) : Liste des instances d'employés.
        pager (bool, optional) : Si la pagination est nécessaire. Defaults to True.

        Retourne :
        -----------
        None
        """
        table = Table(
            title="Liste des employés d'EpicEvent",
            box=box.SQUARE,
            title_justify="center",
            title_style="bold blue"
        )
        table.add_column("Nom", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Prénom", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Id", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Identifiant", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Email", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Role", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Statut", justify="center", style="cyan", header_style="bold cyan")

        for e in all_users:
            table.add_row(
                e.last_name, e.first_name,
                str(e.epicuser_id), e.username, e.email, e.role.value, e.state.value
            )

        if pager:
            with console.pager():
                console.print(table)
        else:
            console.print(table)
        # Après l'affichage de la liste, demander à l'utilisateur de continuer
        print("\nAppuyez sur Entrée pour continuer...")
        input()

    @classmethod
    def prompt_update_user(cls, user):
        """
        Affiche une vue pour mettre à jour les informations d'un utilisateur.

        Paramètres :
        ------------
        user : Instance de l'utilisateur à mettre à jour.

        Retourne :
        -----------
        tuple : Tuple contenant les nouvelles informations pour l'utilisateur.
        """
        # Demande des informations à mettre à jour

        new_first_name = questionary.text(
            "Nouveau Prénom (laisser vide pour ne pas changer):"
        ).ask()

        new_last_name = questionary.text(
            "Nouveau Nom (laisser vide pour ne pas changer):"
        ).ask()
        new_password = questionary.text(
            "Nouveau mot de passe (laisser vide pour ne pas changer):"
        ).ask()
        return new_first_name, new_last_name, new_password

    @classmethod
    def prompt_select_gestion(cls, all_gestions):
        """
        Demande à l'utilisateur de sélectionner un gestionnaire parmi une liste.

        Paramètres :
        ------------
        all_gestions (list) : Liste des instances de gestionnaires.

        Retourne :
        -----------
        Instance de gestionnaire : Instance du gestionnaire sélectionné ou None si aucun gestionnaire n'est sélectionné.
        """
        print(f"Gestionnaires disponibles : {all_gestions}")
        choices = [f"{gestion.first_name} {gestion.last_name}" for gestion in all_gestions]

        selected_choice = questionary.select(
            "Choix du gestionnaire:",
            choices=choices,
        ).ask()

        if selected_choice:
            for gestion in all_gestions:
                if f"{gestion.first_name} {gestion.last_name}" == selected_choice:
                    return gestion
        return None
