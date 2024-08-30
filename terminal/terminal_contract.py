import os
import sys
from typing import Optional
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, requires_roles, sentry_activate)
from controllers.contract_controller import ContractBase
from terminal.terminal_customer import EpicTerminalCustomer
from terminal.terminal_user import EpicTerminalUser
from models.entities import Customer, Contract, Commercial, EpicUser
from controllers.user_controller import EpicUserBase
from views.contract_view import ContractView
from views.customer_view import CustomerView
from views.event_view import EventView
from views.user_view import UserView
from views.data_view import DataView
from views.console_view import console


class EpicTerminalContract:
    """
    Classe pour gérer les contrats depuis l'interface terminal.
    """

    def __init__(self, base, session):
        """
        Initialise la classe EpicTerminalContract avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        user (EpicUser) : L'utilisateur actuellement connecté.
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        """
        self.epic = base
        self.session = session
        self.current_user = None
        self.controller_user = EpicTerminalUser(self.epic, self.session)
        self.controller_customer = EpicTerminalCustomer(self.epic, self.session, self.current_user)

    @sentry_activate
    @is_authenticated
    def list_of_contracts(self, session) -> None:
        """
        Affiche la liste des contrats en permettant de :
        - Sélectionner un commercial
        - Sélectionner un client parmi ceux affectés au commercial
        - Sélectionner un état
        - Lire la base de données et afficher les contrats.
        """
        roles = EpicUserBase.get_roles(self)
        self.roles = roles
        filter_by_user: Optional[int] = None
        filter_by_customer: Optional[int] = None
        filter_by_statut: Optional[str] = None
        filter_by_paiement: Optional[str] = None

        if self.current_user.role == 'COM':
            if isinstance(self.current_user, Commercial):
                # Filtrer par utilisateur (commercial)
                if ContractView.prompt_confirm_filtered_contract():
                    filter_by_user = self.current_user.epicuser_id

                # Filtrer par client
                if ContractView.prompt_confirm_customer():
                    customers = session.query(Customer).filter_by(commercial_id=self.current_user.epicuser_id).all()
                    if customers:
                        select_customer = CustomerView.prompt_client([customer.name for customer in customers])
                        selected_customer = next((customer for customer in customers if customer.name == select_customer), None)
                        if selected_customer:
                            filter_by_customer = selected_customer.customer_id
                    else:
                        text = "Aucun client trouvé pour ce commercial."
                        console.print(text, style="red")
                        return

                # Filtrer par statut de contrat
                if ContractView.prompt_confirm_contract_state():
                    contract_state = ContractView.prompt_choose_state()
                    if contract_state:
                        if contract_state == "Contrats non signés":
                            filter_by_statut = 'C'
                        else:
                            filter_by_statut = 'S'

                # Filtrer par état de paiement
                if ContractView.prompt_confirm_contract_paiement():
                    paiement_state = ContractView.prompt_choose_paiement_state()
                    if paiement_state:
                        if paiement_state == "Contrats non soldés":
                            filter_by_paiement = 'N'
                        else:
                            filter_by_paiement = 'P'

                # Construire la requête de filtrage des contrats
                query = session.query(Contract)

                if filter_by_user:
                    query = query.filter_by(commercial_id=filter_by_user)
                if filter_by_customer:
                    query = query.filter_by(customer_id=filter_by_customer)
                if filter_by_statut:
                    query = query.filter_by(state=filter_by_statut)
                if filter_by_paiement:
                    query = query.filter_by(paiement_state=filter_by_paiement)

                # Exécuter la requête et afficher les résultats
                contracts = query.all()
                ContractView.display_list_contracts(contracts)
        else:
            # Afficher tous les contrats si l'utilisateur n'est pas un commercial
            contracts = session.query(Contract).all()
            ContractView.display_list_contracts(contracts, session)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def create_contract(self, session) -> None:
        """
        Crée un nouveau contrat en permettant de :
        - Sélectionner un client
        - Saisir les données du contrat
        - Mettre à jour la base de données
        - Générer une tâche en attente de signature.
        """

        clients = self.session.query(Customer).all()

        # Assurez-vous que 'client_data' contient des identifiants corrects
        client_data = [{"name": f"{c.first_name} {c.last_name} {c.customer_id}", "value": c.customer_id}
                       for c in clients]

        # Récupérer l'identifiant du client sélectionné
        client_id = CustomerView.prompt_client(client_data)

        try:
            data = ContractView.prompt_data_contract()

            # Ajouter l'identifiant du client sélectionné au dictionnaire data
            data['customer_id'] = client_id
            client = session.query(Customer).filter_by(customer_id=client_id).first()
            commercial_id = client.commercial_id
            data['commercial_id'] = commercial_id
            # Appeler la fonction pour créer le contrat
            contract = ContractBase.create_contract(session, data)
            if ContractView.prompt_add_gestion():
                EpicTerminalContract.update_contract_choose(self, session, contract)
            contract_ref = data['description']
            text = f'Contrat {contract_ref} en attente de signature'
            return text

        except KeyboardInterrupt:
            DataView.display_interupt()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'COM', 'Admin', 'Gestion', 'Commercial')
    def update_contract(self, session):
        # Vérifiez si self.current_user est défini
        if not self.current_user:
            text = "Erreur : Utilisateur non connecté ou non valide."
            console.print(text, style="bold red")
            return

        # Récupérer tous les contrats
        contracts = session.query(Contract).all()

        # Filtrage des contrats pour les commerciaux
        if self.current_user.role == 'COM':
            if isinstance(self.current_user, Commercial):
                commercial = self.current_user
                contracts = [contract for contract in contracts if contract in commercial.contracts]

        selected_contract = EventView.prompt_select_contract(contracts)

        if not selected_contract:
            raise ValueError("Contrat sélectionné invalide")

        contract_id = selected_contract.contract_id
        contract = session.query(Contract).filter_by(contract_id=contract_id).first()
        if not contract:
            raise ValueError("Contrat introuvable")

        try:
            choice = ContractView.menu_update_contract(contract)
            match choice:
                case 1:
                    try:
                        ContractView.display_contract_info(contract)
                        data = ContractView.prompt_data_contract()
                        ContractBase.update_contract(contract_id, data, session)
                        ContractView.display_contract_info(contract)
                    except KeyboardInterrupt:
                        DataView.display_interupt()
                case 2:
                    try:
                        ContractBase.signed(session, contract_id)
                        DataView.display_workflow()
                    except KeyboardInterrupt:
                        DataView.display_interupt()
        except KeyboardInterrupt:
            DataView.display_interupt()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_contract_gestion(self, session) -> None:
        """
        Met à jour le commercial attribué à un client.

        Cette fonction permet de :
        - Sélectionner un client.
        - Sélectionner un commercial.
        - Attribuer le commercial sélectionné au client sélectionné.
        - Mettre à jour la base de données.
        """
        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return
        # Récupérer tous les contrat
        contracts = session.query(Contract).filter_by(gestion_id=None).all()
        ref = EventView.prompt_select_contract(contracts)
        selected_contract = session.query(Contract).filter_by(contract_id=ref.contract_id).first()
        selected_contract_id = selected_contract.contract_id
        # Récupérer tous les gestionnaires
        users = session.query(EpicUser).filter_by(role='GES').all()

        # Demander à l'utilisateur de sélectionner un gestionnaire
        selected_gestion = UserView.prompt_select_gestion(users)
        if not selected_gestion:
            text = "Erreur : Aucun contrat sélectionné."
            console.print(text, style="bold red")
            return

        # Mettre à jour le commercial du client
        ContractBase.update_gestion_contract(self.current_user, session, selected_contract_id, selected_gestion.epicuser_id)
        text = f"Le gestionnaire {selected_gestion.username} a été attribué au contrat {selected_contract_id} avec succès."
        console.print(text, style="cyan")
        ContractBase.update_contract

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_contract_choose(self, session, contract) -> None:
        """
        Met à jour le commercial attribué à un client.

        Cette fonction permet de :
        - Sélectionner un client.
        - Sélectionner un commercial.
        - Attribuer le commercial sélectionné au client sélectionné.
        - Mettre à jour la base de données.
        """
        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return
        # Récupérer tous les gestionnaires
        users = session.query(EpicUser).filter_by(role='GES').all()

        # Demander à l'utilisateur de sélectionner un gestionnaire
        selected_gestion = UserView.prompt_select_gestion(users)
        if not selected_gestion:
            text = "Erreur : Aucun contrat sélectionné."
            console.print(text, style="bold red")
            return
        # Mettre à jour le commercial du client
        ContractBase.update_gestion_contract(self.current_user, session, contract.contract_id, selected_gestion.epicuser_id)
        text = f"Le gestionnaire {selected_gestion.username} a été attribué au contrat {contract} avec succès."
        console.print(text, style="cyan")
        ContractBase.update_contract

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def add_paiement_contract(self, session):
        contracts = session.query(Contract).all()
        ref = EventView.prompt_select_contract(contracts)

        selected_contract = session.query(Contract).filter_by(contract_id=ref.contract_id).first()
        if not selected_contract:
            raise ValueError("Contrat introuvable")

        try:
            data = ContractView.prompt_data_paiement()
            contract_base_instance = ContractBase(self, session)
            # Corriger l'ordre des arguments ici
            contract_base_instance.add_paiement(session, selected_contract.contract_id, data)
        except ValueError as e:
            text = f"Erreur: {e}"
            console.print(text, style="bold red")
        except KeyboardInterrupt:
            DataView.display_interupt()
