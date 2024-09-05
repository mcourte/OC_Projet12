import questionary
import re
from rich.table import Table
from rich import box
import os
import sys
from rich.panel import Panel
from rich.align import Align
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.console_view import console
from views.prompt_view import PromptView
from views.regexformat import regexformat


class CustomerView:
    """
    Classe pour gérer l'affichage et l'interaction avec les clients.
    """

    @classmethod
    def prompt_client(cls, all_customers, **kwargs) -> str:
        """
        Demande à l'utilisateur de sélectionner un client parmi une liste de noms complets.

        :param all_customers: Liste des noms complets des clients.
        :type all_customers: list
        :param kwargs: Arguments supplémentaires pour la fonction `PromptView.prompt_select`.
        :return: Le nom complet du client sélectionné.
        :rtype: str
        """
        return PromptView.prompt_select("Choix du client:", all_customers, **kwargs)

    @classmethod
    def prompt_data_customer(cls, full_name_required=True) -> dict:
        """
        Demande les informations d'un client.

        :param full_name_required: Indique si le nom complet est requis. Par défaut à True.
        :type full_name_required: bool, optionnel
        :return: Un dictionnaire contenant les informations du client.
        :rtype: dict
        :raises KeyboardInterrupt: Si l'utilisateur appuie sur Ctrl+C.
        """
        first_name = questionary.text(
            "Nom :",
            validate=lambda text: True
            if re.match(regexformat['all_nospace'][0], text)
            else regexformat['all_nospace'][1]).ask()

        last_name = questionary.text(
            "Prénom:",
            validate=lambda text: True
            if re.match(regexformat['all_letters'][0], text)
            else regexformat['all_letters'][1]).ask()

        email = questionary.text(
            "Email:",
            validate=lambda text: True
            if re.match(regexformat['email'][0], text)
            else regexformat['email'][1]).ask()

        phone = questionary.text(
            "Téléphone:",
            validate=lambda text: True
            if re.match(regexformat['phone'][0], text)
            else regexformat['phone'][1]).ask()

        company_name = questionary.text(
            "Entreprise:",
            validate=lambda text: True
            if re.match(regexformat['all_space_union'][0], text)
            else regexformat['all_space_union'][1]).ask()

        return {'first_name': first_name, 'last_name': last_name, 'email': email, 'phone': phone,
                'company_name': company_name}

    @classmethod
    def display_list_customers(cls, all_customers, pager=False) -> None:
        """
        Affiche la liste des clients.

        :param all_customers: Liste des instances de client.
        :type all_customers: list
        :param pager: Indique si le pager est utilisé. Par défaut à False.
        :type pager: bool, optionnel
        """
        fmt_date = '%d/%m/%Y'

        table = Table(
            title="Liste des Clients",
            box=box.SQUARE,
            title_justify="center",
            title_style="bold blue"
        )
        table.add_column("Nom complet", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Entreprise", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Téléphone", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Email", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Commercial associé", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Date de création", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Date de modification", justify="center", style="cyan", header_style="bold cyan")
        for c in all_customers:
            creation_time = f"{c.creation_time.strftime(fmt_date)}"
            update_time = f"{c.update_time.strftime(fmt_date)}"
            table.add_row(
                f"{c.first_name} {c.last_name}", c.company_name, c.phone, c.email,
                str(c.commercial.username) if c.commercial else 'Aucun commercial',
                creation_time, update_time
            )

        if pager:
            with console.pager():
                console.print(table)
        else:
            console.print(table)

        # Après l'affichage de la liste, demander à l'utilisateur de continuer
        console.print("\nAppuyez sur Entrée pour continuer...")
        input()

    @classmethod
    def prompt_customers(cls, all_customers) -> str:
        """
        Demande à l'utilisateur de sélectionner un client dans une liste.

        :param all_customers: Liste des instances de clients.
        :type all_customers: list
        :return: Nom complet du client sélectionné ou None si aucun client n'est sélectionné.
        :rtype: str
        """
        choices = [f"{c.first_name} {c.last_name}" for c in all_customers]
        selected_name = questionary.select(
            "Choix du client:",
            choices=choices,
        ).ask()

        if selected_name:
            # Trouver l'instance de client correspondante
            for customer in all_customers:
                if f"{customer.first_name} {customer.last_name}" == selected_name:
                    return customer
        return None

    @classmethod
    def prompt_confirm_commercial(cls, **kwargs) -> bool:
        """
        Demande confirmation pour l'ajout d'un commercial associé à un client.

        :param kwargs: Arguments supplémentaires pour la fonction `questionary.confirm`.
        :return: True si l'utilisateur souhaite ajouter un commercial associé, sinon False.
        :rtype: bool
        """
        return questionary.confirm(
            "Souhaitez-vous ajouter un commercial associé à ce client ?", **kwargs).ask()

    @classmethod
    def display_customer(cls, customer):
        """
        Affiche les informations de profil d'un utilisateur.

        :param e: Instance de l'utilisateur dont les informations doivent être affichées.
        :type e: User
        """
        text = f'ID: {customer.customer_id}\n'
        text += f'Prénom: {customer.first_name}\n'
        text += f'Nom: {customer.last_name}\n'
        text += f'Email: {customer.email}\n' if customer.email else 'Email: \n'
        text += f'Téléphone: {customer.phone}\n'
        text += f'Entreprise: {customer.company_name}\n'
        text += f'Commercial associé: {customer.commercial_id}\n'
        text += f'Date de création: {customer.creation_time}\n'
        text += f'Date de la dernière modification: {customer.update_time}\n'
        p = Panel(
            Align.center(text, vertical='bottom'),
            box=box.ROUNDED,
            style='cyan',
            title_align='center',
            title='Information du client')
        console.print(p)
