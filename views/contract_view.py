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


class ContractView:
    """
    Classe pour gérer l'affichage et l'interaction avec les contrats.
    """

    @classmethod
    def display_list_contracts(cls, all_contracts) -> None:
        """
        Affiche la liste des contrats.

        :param all_contracts: Liste des instances de contrat.
        :type all_contracts: list
        :param pager: Indique si le pager est utilisé. Par défaut à False.
        :type pager: bool, optionnel
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
            try:
                client_name = f"{c.customer.first_name} {c.customer.last_name}".strip()
                remaining_amount = str(c.remaining_amount) if c.remaining_amount is not None else "0"
                commercial_username = str(c.customer.commercial.username) if c.customer and c.customer.commercial else ""
                gestion_id = str(c.gestion_id) if c.gestion_id is not None else ""

                table.add_row(
                    c.description,
                    client_name,
                    str(c.total_amount),
                    remaining_amount,
                    c.state.value,
                    commercial_username,
                    gestion_id
                )
            except AttributeError as e:
                text = f"Erreur d'attribut manquant pour un contrat : {e}"
                console.print(text, style="bold red")
            except Exception as e:
                text = f"Erreur inattendue lors du traitement des contrats : {e}"
                console.print(text, style="bold red")

        console.print(table)

        # Après l'affichage de la liste, demander à l'utilisateur de continuer
        text = "\nAppuyez sur Entrée pour continuer..."
        console.print(text)
        input()

    @classmethod
    def display_contract_info(cls, contract) -> None:
        """
        Affiche les informations d'un contrat spécifique.

        :param contract: Instance du contrat à afficher.
        :type contract: Contract
        """
        title = f"Données du contrat {contract.contract_id}"
        table = Table(title=title, box=box.SQUARE)
        table.add_column("Contract ID")
        table.add_column("Description")
        table.add_column("Client")
        table.add_column("Montant")
        table.add_column("Reste dû")
        table.add_column("Statut")
        table.add_column("Nb évènements")
        table.add_column("Commercial")
        customer_name = f"{contract.customer.first_name} {contract.customer.last_name}"
        table.add_row(
            str(contract.contract_id),
            contract.description,
            customer_name,
            str(contract.total_amount),
            str(contract.remaining_amount),
            contract.state.value,
            str(len(contract.events)),
            contract.customer.commercial.username
        )

        console.print(table)

    @classmethod
    def prompt_data_contract(cls,
                             ref_required=True,
                             mt_required=True, **kwargs) -> dict:
        """
        Demande toutes les données nécessaires pour créer un contrat.

        :param ref_required: Indique si la référence est requise. Par défaut à True.
        :type ref_required: bool, optionnel
        :param mt_required: Indique si le montant est requis. Par défaut à True.
        :type mt_required: bool, optionnel
        :param kwargs: Arguments supplémentaires pour la fonction questionary.text.
        :return: Un dictionnaire contenant les données du contrat.
        :rtype: dict
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
            if re.match(regexformat['all_letters'][0], text)
            else regexformat['all_letters'][1], **kwargs).ask()

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

        :param kwargs: Arguments supplémentaires pour la fonction questionary.text.
        :return: Un dictionnaire contenant la référence et le montant du paiement.
        :rtype: dict
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

    @classmethod
    def prompt_confirm_contract_state(cls, **kwargs) -> bool:
        """
        Demande si les contrats doivent être triés par statut.

        :return: True si les contrats doivent être triés par statut, sinon False.
        :rtype: bool
        """
        return questionary.confirm(
            "Souhaitez-vous trier les contrats par statut ?", **kwargs).ask()

    @classmethod
    def prompt_add_gestion(cls, **kwargs) -> bool:
        """
        Demande si un gestionnaire doit être ajouté au contrat.

        :return: True si un gestionnaire doit être ajouté, sinon False.
        :rtype: bool
        """
        return questionary.confirm(
            "Souhaitez-vous ajouter un gestionnaire à ce contrat ?", **kwargs).ask()

    @classmethod
    def prompt_confirm_contract_paiement(cls, **kwargs) -> bool:
        """
        Demande si les contrats doivent être triés par solde.

        :return: True si les contrats doivent être triés par solde, sinon False.
        :rtype: bool
        """
        return questionary.confirm(
            "Souhaitez-vous trier les contrats par solde ?", **kwargs).ask()

    @classmethod
    def prompt_choose_paiement_state(cls) -> str:
        """
        Demande à l'utilisateur de sélectionner un état de paiement parmi les options disponibles.

        :return: État de paiement sélectionné.
        :rtype: str
        """
        paiement_state = ["Contrats soldés", "Contrats non soldés"]
        return questionary.select(
            "Sélectionnez l'état de paiement:",
            choices=paiement_state
        ).ask()

    @classmethod
    def prompt_confirm_filtered_contract(cls, **kwargs) -> bool:
        """
        Demande si l'utilisateur souhaite voir uniquement les contrats qui lui sont affectés.

        :return: True si l'utilisateur souhaite voir uniquement les contrats qui lui sont affectés, sinon False.
        :rtype: bool
        """
        return questionary.confirm(
            "Souhaitez-vous voir uniquement les contrats qui vous sont affectés ?", **kwargs).ask()

    @classmethod
    def prompt_choose_state(cls) -> str:
        """
        Demande à l'utilisateur de sélectionner un type de contrat parmi les options disponibles.

        :return: Type de contrat sélectionné.
        :rtype: str
        """
        paiement_state = ["Contrats signés", "Contrats non signés"]
        return questionary.select(
            "Sélectionnez le type de contrat :",
            choices=paiement_state
        ).ask()

    @classmethod
    def prompt_confirm_customer(cls, **kwargs) -> bool:
        """
        Demande si l'utilisateur souhaite choisir un client.

        :return: True si l'utilisateur souhaite choisir un client, sinon False.
        :rtype: bool
        """
        return questionary.confirm(
            "Souhaitez-vous choisir un client ?", **kwargs).ask()

    @classmethod
    def menu_update_contract(cls, state):
        """
        Affiche le menu pour la mise à jour d'un contrat en fonction de son état et demande une sélection.

        :param state: L'état actuel du contrat.
        :type state: str
        :return: L'index du choix sélectionné (1 pour "Enregistrer un paiement", 2 pour "Modifier les données du contrat", etc.).
        :rtype: int
        """
        menu_text = [
            'Modifier les données du contrat']
        menu_text.append('Signer le contrat')
        choice = questionary.select("Que voulez-vous faire ?",
                                    choices=menu_text).ask()
        if choice is None:
            raise KeyboardInterrupt
        return menu_text.index(choice) + 1
