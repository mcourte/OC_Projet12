import re
import questionary
from datetime import datetime
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
from views.regexformat import regexformat
from controllers.contract_controller import Contract


class EventView:
    """
    Classe pour gérer l'affichage et les interactions concernant les évènements.
    """

    @classmethod
    def display_list_events(cls, all_events, pager=False) -> None:
        """
        Affiche la liste des évènements.

        Paramètres :
        ------------
        all_events (list) : Liste d'instances d'évènements à afficher.
        pager (bool, optionnel) : Indique si la pagination est utilisée. Par défaut à False.
        """
        table = Table(
            title="Liste des Evènements",
            box=box.SQUARE,
            title_justify="center",
            title_style="bold blue"
        )
        table.add_column("Ref. Contrat", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Titre", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Lieu", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Nb. participants", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Date de Début", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Date de Fin", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Commercial", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Support", justify="center", style="cyan", header_style="bold cyan")

        for e in all_events:
            if e.support:
                str_support = str(e.support_id)
            else:
                str_support = ''
            fmt_date = '%d/%m/%Y'
            debut_dates = f'du {e.date_started.strftime(fmt_date)}'
            end_dates = f'\nau {e.date_ended.strftime(fmt_date)}'
            table.add_row(
                str(e.event_id),
                e.title,
                e.location,
                str(e.attendees),
                debut_dates,
                end_dates,
                str(e.customer_id),
                str_support)

        if pager:
            with console.pager():
                console.print(table)
        else:
            console.print(table)
        # Après l'affichage de la liste, demander à l'utilisateur de continuer
        console.print("\nAppuyez sur Entrée pour continuer...")
        input()

    @classmethod
    def prompt_data_event(cls, **kwargs):
        """
        Demande les informations nécessaires pour créer ou modifier un évènement.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la validation.

        Retourne :
        -----------
        dict : Dictionnaire contenant les données de l'évènement.
        """
        title = questionary.text(
            "Titre:",
            validate=lambda text: True
            if re.match(r"^[a-zA-Z ']+$", text)
            else "Seuls des caractères alpha sont autorisés",
            **kwargs).ask()
        if title is None:
            raise KeyboardInterrupt

        description = questionary.text(
            "Description:",
            validate=lambda text: True
            if re.match(r"^[a-zA-Z ]+$", text)
            else "Seuls des caractères alpha sont autorisés",
            **kwargs).ask()

        location = questionary.text(
            "Lieu:",
            validate=lambda text: True
            if re.match(r"^[a-zA-Z ]+$", text)
            else "Seuls des caractères alpha sont autorisés",
            **kwargs).ask()

        nb = questionary.text(
            "Nb participants:",
            validate=lambda text: True
            if re.match(r"^[0-9]+$", text) and int(text) > 0 and int(text) <= 5000
            else "Nombre compris entre 0 et 5000",
            **kwargs).ask()

        fmt_date = '%d/%m/%Y'
        start = questionary.text(
            "Date de début:",
            validate=lambda text: True
            if re.match(regexformat['date'][0], text)
            else regexformat['date'][1], **kwargs).ask()

        if start:
            end = questionary.text(
                "Date de fin:",
                validate=lambda text: True
                if re.match(regexformat['date'][0], text) and datetime.strptime(
                    text, fmt_date) >= datetime.strptime(start, fmt_date)
                else regexformat['date'][1] + " et >= date de début",
                **kwargs).ask()
        else:
            end = None

        return {'title': title, 'description': description,
                'location': location, 'attendees': nb,
                'date_started': start, 'date_ended': end}

    @classmethod
    def prompt_select_event(cls, all_events):
        """
        Demande à l'utilisateur de sélectionner un évènement parmi une liste de valeurs.

        Paramètres :
        ------------
        all_events (list) : Liste des instances d'évènements.

        Retourne :
        -----------
        str : La référence de l'évènement sélectionné.
        """
        text = (f"Evènements disponibles: {all_events}")
        console.print(text, justify="center", style="bold blue")
        choices = [f"{event.event_id} {event.title}" for event in all_events]

        selected_choice = questionary.select(
            "Choix de l'évènement:",
            choices=choices,
        ).ask()

        if selected_choice:
            for event in all_events:
                if f"{event.event_id} {event.title}" == selected_choice:
                    return event
        return None

    @classmethod
    def prompt_select_contract(cls, all_contracts) -> Contract:
        """
        Demande à l'utilisateur de sélectionner un contrat dans une liste.

        Paramètres :
        ------------
        all_contracts (list) : Liste des instances de contrats.

        Retourne :
        -----------
        Contract : Instance du contrat sélectionné ou None si aucun contrat n'est sélectionné.
        """
        text = (f"Contrats disponibles: {all_contracts}")
        console.print(text, justify="center", style="bold blue")
        choices = [f"{contract.contract_id} {contract.description}" for contract in all_contracts]

        selected_choice = questionary.select(
            "Choix du contrat:",
            choices=choices,
        ).ask()

        if selected_choice:
            for contract in all_contracts:
                if f"{contract.contract_id} {contract.description}" == selected_choice:
                    return contract
        return None

    @classmethod
    def prompt_select_statut(cls) -> str:
        """
        Demande à l'utilisateur de sélectionner un statut parmi les états définis.

        Retourne :
        -----------
        str : État sélectionné ou None si aucun état n'est sélectionné.
        """
        statuts = cls.CONTRACT_STATES
        choices = [f"{code} {description}" for code, description in statuts]

        selected_choice = questionary.select(
            "Choix du statut:",
            choices=choices,
        ).ask()

        if selected_choice:
            code = selected_choice.split()[0]
            return code
        return None

    @classmethod
    def prompt_add_support(cls, **kwargs) -> bool:
        """
        Demande si un support doit être ajouté à l'évènement.

        Retourne :
        -----------
        bool : True si un support doit être ajouté, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous ajouter un support à cet évènement ?", **kwargs).ask()

    @classmethod
    def prompt_filtered_events_gestion(cls, **kwargs) -> bool:
        """
        Demande si la liste des évènements doit inclure tous les évènements ou uniquement ceux sans support associé.

        Retourne :
        -----------
        bool : True si tous les évènements doivent être affichés, sinon False pour uniquement ceux sans support.
        """
        return questionary.confirm(
            "Souhaitez-vous voir la totalité des évènements (Y) ou "
            "uniquement ceux qui n'ont pas de support associés (n)  ?", **kwargs).ask()

    @classmethod
    def prompt_filtered_events_support(cls, **kwargs) -> bool:
        """
        Demande si la liste des évènements doit inclure tous les évènements ou uniquement ceux associés à l'utilisateur.

        Retourne :
        -----------
        bool : True si tous les évènements doivent être affichés, sinon False pour uniquement ceux associés.
        """
        return questionary.confirm(
            "Souhaitez-vous voir la totalité des évènements (Y) ou "
            "uniquement ceux qui vous sont associés (n)  ?", **kwargs).ask()
