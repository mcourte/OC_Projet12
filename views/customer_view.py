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
        return PromptView.prompt_select(
                "Choix du client:", all_customers, **kwargs)

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
        all_customers (list) : Liste des instances de clients.
        pager (bool, optionnel) : Indique si le pager est utilisé. Par défaut à True.
        """
        table = Table(title="Liste des clients", box=box.SQUARE)
        table.add_column("Nom")
        table.add_column("Prénom")
        table.add_column("Email")
        table.add_column("Téléphone")
        table.add_column("Entreprise")
        table.add_column("Commercial")
        table.add_column("Nb contrats")
        for c in all_customers:
            table.add_row(
                c.first_name, c.last_name, c.email, c.phone, c.company_name,
                str(c.commercial), str(len(c.contracts)))

        if pager:
            with console.pager():
                console.print(table)
        else:
            console.print(table)

    @classmethod
    def display_customer_info(cls, customer) -> None:
        """
        Affiche les informations d'un client spécifique.

        Paramètres :
        ------------
        customer (Client) : Instance du client à afficher.
        """
        title = f"Données du client {customer.first_name} {customer.last_name}"
        table = Table(title=title, box=box.SQUARE)
        table.add_column("Nom")
        table.add_column("Prénom")
        table.add_column("Email")
        table.add_column("Téléphone")
        table.add_column("Entreprise")
        table.add_column("Commercial")
        table.add_column("Nb contrats actifs")
        table.add_column("Nb contrats")
        table.add_row(
                customer.first_name, customer.last_name, customer.email,
                customer.phone, customer.company_name,
                str(customer.commercial), str(len(customer.actif_contracts)),
                str(len(customer.contracts)),
                )
        console.print(table)
