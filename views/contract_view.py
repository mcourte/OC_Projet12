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
from views.regexformat import regexformat
from controllers.contract_controller import Contract
from controllers.user_controller import EpicUser


class ContractView:
    """
    Classe pour gérer l'affichage et l'interaction avec les contrats.
    """

    @classmethod
    def display_list_contracts(cls, all_contracts, session, pager=False) -> None:
        """
        Affiche la liste des contrats.

        Paramètres :
        ------------
        all_contracts (list) : Liste des instances de contrat.
        pager (bool, optionnel) : Indique si le pager est utilisé. Par défaut à True.
        """
        table = Table(
            title="Liste des Contrats",
            box=box.SQUARE,
            title_justify="center",
            title_style="bold blue"
        )
        table.add_column("Description", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Client", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Montant", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Reste dû", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Statut", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Commercial", justify="center", style="cyan", header_style="bold cyan")
        table.add_column("Gestionnaire_id", justify="center", style="cyan", header_style="bold cyan")
        for c in all_contracts:
            client_name = f"{c.customer.first_name} {c.customer.last_name}".strip()
            table.add_row(
                c.description, client_name,
                str(c.total_amount), str(c.remaining_amount or "0"),
                c.state.value,
                c.customer.commercial.username,
                str(c.gestion_id)
            )
        if pager:
            with console.pager():
                console.print(table)
        else:
            console.print(table)
        print("\nAppuyez sur Entrée pour continuer...")
        input()

    @classmethod
    def display_contract_info(cls, contract) -> None:
        """
        Affiche les informations d'un contrat spécifique.

        Paramètres :
        ------------
        contract (Contract) : Instance du contrat à afficher.
        """
        title = f"Données du contrat {contract.ref}"
        table = Table(title=title, box=box.SQUARE)
        table.add_column("Référence")
        table.add_column("Description")
        table.add_column("Client")
        table.add_column("Montant")
        table.add_column("Reste dû")
        table.add_column("Statut")
        table.add_column("Nb évènements")
        table.add_column("Commercial")
        table.add_row(
            contract.ref, contract.description, contract.customer.first_name, contract.customer.last_name,
            str(contract.total_amount), str(contract.remaining_amount),
            contract.state.value, str(len(contract.events)),
            contract.customer.commercial.username
        )
        console.print(table)

    @classmethod
    def prompt_confirm_contract(cls, **kwargs) -> bool:
        """
        Demande si un contrat doit être sélectionné.

        Retourne :
        -----------
        bool : True si un contrat doit être sélectionné, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous sélectionner un contrat ?", **kwargs).ask()

    @classmethod
    def prompt_confirm_close_contract(cls, **kwargs) -> bool:
        """
        Demande si un contrat doit être clôturé.

        Retourne :
        -----------
        bool : True si le contrat doit être clôturé, sinon False.
        """
        return questionary.confirm(
            "Demander une clôture du contrat ?", **kwargs).ask()

    @staticmethod
    def prompt_select_statut() -> str:
        """
        Demande à l'utilisateur de sélectionner un statut parmi les états définis dans Contract.

        Returns:
            str: État sélectionné ou None si aucun état n'est sélectionné.
        """
        # Accéder directement aux états définis dans la classe Contract
        statuts = Contract.CONTRACT_STATES
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
    def prompt_data_contract(cls,
                             ref_required=True,
                             mt_required=True, **kwargs) -> dict:
        """
        Demande toutes les données nécessaires pour créer un contrat.

        Paramètres :
        ------------
        ref_required (bool, optionnel) : Indique si la référence est requise. Par défaut à True.
        mt_required (bool, optionnel) : Indique si le montant est requis. Par défaut à True.
        **kwargs : Arguments supplémentaires pour la fonction questionary.text.

        Retourne :
        -----------
        dict : Un dictionnaire contenant les données du contrat.
        """
        error_text = regexformat['3cn'][1]
        ref = questionary.text(
            "Référence:",
            validate=lambda text: True
            if re.match(regexformat['3cn'][0], text) and len(text) >= 3
            else error_text, **kwargs).ask()
        if ref_required and ref is None:
            raise KeyboardInterrupt

        description = questionary.text(
            "Description:",
            validate=lambda text: True
            if re.match(regexformat['alphanum'][0], text)
            else regexformat['alphanum'][1], **kwargs).ask()

        total_amount = questionary.text(
            "Montant:",
            validate=lambda text: True
            if re.match(regexformat['numposmax'][0], text)
            else regexformat['numposmax'][1],
            **kwargs).ask()
        if mt_required and total_amount is None:
            raise KeyboardInterrupt

        return {'ref': ref, 'description': description,
                'total_amount': total_amount}

    @classmethod
    def prompt_data_paiement(cls, **kwargs) -> dict:
        """
        Demande les données nécessaires pour un paiement.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la fonction questionary.text.

        Retourne :
        -----------
        dict : Un dictionnaire contenant la référence et le montant du paiement.
        """
        ref = questionary.text(
            "Référence:",
            validate=lambda text: True
            if re.match(regexformat['3cn'][0], text) and len(text) >= 3
            else regexformat['3cn'][1], **kwargs).ask()
        if ref is None:
            raise KeyboardInterrupt
        amount = questionary.text(
            "Montant:",
            validate=lambda text: True
            if re.match(regexformat['numposmax'][0], text)
            else regexformat['numposmax'][1],
            **kwargs).ask()
        if amount is None:
            raise KeyboardInterrupt
        return {'paiement_id': ref, 'amount': amount}
