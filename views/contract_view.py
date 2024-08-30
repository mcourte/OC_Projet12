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


class ContractView:
    """
    Classe pour gérer l'affichage et l'interaction avec les contrats.
    """

    @classmethod
    def display_list_contracts(cls, all_contracts, pager=False) -> None:
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
            try:
                client_name = f"{c.customer.first_name} {c.customer.last_name}".strip()
                remaining_amount = str(c.remaining_amount) if c.remaining_amount is not None else "0"
                commercial_username = str(c.customer.commercial.username) if c.customer and c.customer.commercial else ""
                gestion_id = str(c.gestion_id) if c.gestion_id is not None else ""

                # Affichage des informations pour le débogage
                print(f"Description: {c.description}, Client: {client_name}, Montant: {c.total_amount}, "
                      "Reste dû: {remaining_amount}, Statut: {c.state.value}, Commercial: {commercial_username},"
                      " Gestionnaire_id: {gestion_id}")

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
                print(f"Erreur d'attribut manquant pour un contrat : {e}")
            except Exception as e:
                print(f"Erreur inattendue lors du traitement des contrats : {e}")

        if pager:
            with console.pager():
                console.print(table)
        else:
            console.print(table)

        # Après l'affichage de la liste, demander à l'utilisateur de continuer
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

    @classmethod
    def prompt_confirm_contract_state(cls, **kwargs) -> bool:
        """
        Demande si un contrat doit être sélectionné.

        Retourne :
        -----------
        bool : True si un contrat doit être sélectionné, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous trier les contrats par statut?", **kwargs).ask()

    @classmethod
    def prompt_add_gestion(cls, **kwargs) -> bool:
        """
        Demande si un contrat doit être sélectionné.

        Retourne :
        -----------
        bool : True si un contrat doit être sélectionné, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous ajouter un gestionnaire à ce contrat ?", **kwargs).ask()

    @classmethod
    def prompt_confirm_contract_paiement(cls, **kwargs) -> bool:
        """
        Demande si un contrat doit être sélectionné.

        Retourne :
        -----------
        bool : True si un contrat doit être sélectionné, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous trier les contrats par solde?", **kwargs).ask()

    @classmethod
    def prompt_choose_paiement_state(cls) -> str:
        """
        Demande à l'utilisateur de sélectionner un employé dans une liste.

        Args:
            all_users (list): Liste des noms d'employés.

        Returns:
            str: Nom de l'employé sélectionné.
        """
        paiement_state = ["Contrats soldés", "Contrats non soldés"]
        return questionary.select(
            "Sélectionnez l'état de paiement:",
            choices=paiement_state
        ).ask()

    @classmethod
    def prompt_confirm_filtered_contract(cls, **kwargs) -> bool:
        """
        Demande si un contrat doit être sélectionné.

        Retourne :
        -----------
        bool : True si un contrat doit être sélectionné, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous voir uniquement les contrats qui vous sont affectés?", **kwargs).ask()

    @classmethod
    def prompt_choose_state(cls) -> str:
        """
        Demande à l'utilisateur de sélectionner un employé dans une liste.

        Args:
            all_users (list): Liste des noms d'employés.

        Returns:
            str: Nom de l'employé sélectionné.
        """
        paiement_state = ["Contrats signés", "Contrats non signés"]
        return questionary.select(
            "Sélectionnez le type de contrat :",
            choices=paiement_state
        ).ask()

    @classmethod
    def prompt_confirm_customer(cls, **kwargs) -> bool:
        """
        Demande si un contrat doit être sélectionné.

        Retourne :
        -----------
        bool : True si un contrat doit être sélectionné, sinon False.
        """
        return questionary.confirm(
            "Souhaitez-vous choisir un client?", **kwargs).ask()

    @classmethod
    def menu_update_contract(cls, state):
        """
        Affiche le menu pour la mise à jour d'un contrat en fonction de son état et demande une sélection.

        Args:
            state (str): L'état actuel du contrat.

        Returns:
            int: L'index du choix sélectionné (1 pour "Enregistrer un paiement",
            2 pour "Modifier les données du contrat", etc.).
        """
        menu_text = [
            'Modifier les données du contrat']
        menu_text.append('Signer le contrat')
        choice = questionary.select("Que voulez-vous faire ?",
                                    choices=menu_text).ask()
        if choice is None:
            raise KeyboardInterrupt
        return menu_text.index(choice) + 1
