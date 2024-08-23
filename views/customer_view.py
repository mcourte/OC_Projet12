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


class CustomerView:
    """
    Classe pour gérer l'affichage et l'interaction avec les clients.
    """

    @classmethod
    def prompt_confirm_customer(cls, **kwargs) -> bool:
        """
        Demande confirmation pour la sélection d'un client.

        Retourne :
        -----------
        bool : True si l'utilisateur souhaite sélectionner un client, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous sélectionner un client ?", **kwargs).ask()

    @classmethod
    def prompt_client(cls, all_customers, **kwargs) -> str:
        """
        Demande à l'utilisateur de sélectionner un client parmi une liste de noms complets.

        Paramètres :
        ------------
        all_customers (list) : Liste des noms complets des clients.

        Retourne :
        -----------
        str : Le nom complet du client sélectionné.
        """
        return PromptView.prompt_select("Choix du client:", all_customers, **kwargs)

    @classmethod
    def prompt_full_name(cls) -> str:
        """
        Demande à l'utilisateur de saisir un nom complet.

        Retourne :
        -----------
        str : Le nom complet saisi par l'utilisateur.
        """
        return questionary.text(
            "Nom complet:",
            validate=lambda text: True
            if re.match(regexformat['alpha'][0], text)
            else regexformat['alpha'][1]).ask()

    @classmethod
    def prompt_data_customer(cls, full_name_required=True) -> dict:
        """
        Demande les informations d'un client.

        Paramètres :
        ------------
        full_name_required (bool, optionnel) : Indique si le nom complet est requis. Par défaut à True.

        Lève :
        ------
        KeyboardInterrupt : Si l'utilisateur appuie sur Ctrl+C.

        Retourne :
        -----------
        dict : Un dictionnaire contenant les informations du client.
        """
        first_name = questionary.text(
            "Nom :",
            validate=lambda text: True
            if re.match(regexformat['alpha'][0], text)
            else regexformat['alpha'][1]).ask()

        last_name = questionary.text(
            "Prénom:",
            validate=lambda text: True
            if re.match(regexformat['alpha'][0], text)
            else regexformat['alpha'][1]).ask()

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
            if re.match(regexformat['alpha'][0], text)
            else regexformat['alpha'][1]).ask()
        return {'first_name': first_name, 'last_name': last_name, 'email': email, 'phone': phone,
                'company_name': company_name}

    @classmethod
    def display_list_customers(cls, all_customers, pager=True) -> None:
        """
        Affiche la liste des clients.

        Paramètres :
        ------------
        all_customers (list) : Liste des instances de client.
        pager (bool, optionnel) : Indique si le pager est utilisé. Par défaut à True.
        """
        table = Table(title="Liste des clients", box=box.SQUARE)
        table.add_column("Nom complet")
        table.add_column("Commercial")
        for c in all_customers:
            table.add_row(
                f"{c.first_name} {c.last_name}",  # Nom complet du client
                str(c.commercial.username) if c.commercial else 'Aucun commercial'  # Nom d'utilisateur du commercial
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
    def display_customer_info(cls, customer) -> None:
        """
        Affiche les informations d'un client spécifique.

        Paramètres :
        ------------
        customer (Client) : Instance du client à afficher.
        """
        title = "Données du client"
        table = Table(title=title, box=box.SQUARE)
        table.add_column("Nom")
        table.add_column("Prénom")
        table.add_column("Email")
        table.add_column("Téléphone")
        table.add_column("Entreprise")
        table.add_column("Commercial")
        table.add_column("Nb contrats")
        table.add_row(
                      customer.first_name, customer.last_name, customer.email,
                      customer.phone, customer.company_name,
                      str(customer.commercial),
                      str(len(customer.contracts)),
                      )
        console.print(table)
        print("\nAppuyez sur Entrée pour continuer...")
        input()

    @classmethod
    def prompt_customers(cls, all_customers) -> str:
        """
        Demande à l'utilisateur de sélectionner un client dans une liste.

        Args:
            all_customers (list): Liste des instances de clients.

        Returns:
            str: Nom complet du client sélectionné ou None si aucun client n'est sélectionné.
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
