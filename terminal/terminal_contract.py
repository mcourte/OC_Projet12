import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, requires_roles)
from controllers.contract_controller import ContractBase
from terminal.terminal_customer import EpicTerminalCustomer
from terminal.terminal_user import EpicTerminalUser
from models.entities import Customer, Contract
from controllers.user_controller import EpicUser
from views.contract_view import ContractView
from views.customer_view import CustomerView
from views.event_view import EventView
from views.user_view import UserView
from views.menu_view import MenuView
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

    @is_authenticated
    def list_of_contracts(self, session) -> None:
        """
        Affiche la liste des contrats en permettant de :
        - Sélectionner un commercial
        - Sélectionner un client parmi ceux affectés au commercial
        - Sélectionner un état
        - Lire la base de données et afficher les contrats.
        """

        contracts = session.query(Contract).all()
        ContractView.display_list_contracts(contracts, session)

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
            ContractBase.create_contract(session, data)

            contract_ref = data['description']
            text = f'Contrat {contract_ref} en attente de signature'
            return text

        except KeyboardInterrupt:
            DataView.display_interupt()

    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_contract(self, session):
        contracts = session.query(Contract).all()
        ref = EventView.prompt_select_contract(contracts)
        selected_contract = session.query(Contract).filter_by(contract_id=ref.contract_id).first()

        if not selected_contract:
            raise ValueError("Contrat introuvable")

        try:
            choice = MenuView.menu_update_contract(selected_contract)
            match choice:
                case 1:
                    try:
                        data = ContractView.prompt_data_paiement()
                        contract_base_instance = ContractBase(session)
                        contract_base_instance.add_paiement(selected_contract.contract_id, data)
                    except ValueError as e:
                        print(f"Erreur: {e}")

                case 2:
                    try:
                        contract = session.query(Contract).filter_by(contract_id=ref).all()
                        ContractView.display_contract_info(contract)
                        data = ContractView.prompt_data_contract(
                            ref_required=False, mt_required=False)
                        newref = self.epic.db_contracts.update_contract(ref, data)
                        contract = self.epic.db_contracts.get_contract(newref)
                        ContractView.display_contract_info(contract)
                    except KeyboardInterrupt:
                        DataView.display_interupt()
                case 3:
                    self.epic.db_contracts.signed(ref)
                    contract = self.epic.db_contracts.get_contract(ref)
                    DataView.display_workflow()
        except KeyboardInterrupt:
            DataView.display_interupt()

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
            print("Erreur : La session est non initialisée.")
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
            print("Erreur : Aucun contrat sélectionné.")
            return

        # Mettre à jour le commercial du client
        ContractBase.update_gestion_contract(self.current_user, session, selected_contract_id, selected_gestion.epicuser_id)
        print(f"Le gestionnaire {selected_gestion.username} a été attribué au contrat {selected_contract_id} avec succès.")
        ContractBase.update_contract

    @is_authenticated
    def list_of_contracts_filtered(self, session):
        """
        Affiche la liste des événements en permettant de :
        - Choisir un commercial (facultatif)
        - Choisir un client (facultatif)
        - Sélectionner un contrat (si confirmé)
        - Sélectionner un support (si confirmé)
        - Lire la base de données et afficher les événements.
        """
        try:
            # Choisir un commercial (facultatif)
            contracts = session.query(Contract).all()
            commercials = session.query(EpicUser).filter_by(role='COM').all()
            if UserView.prompt_confirm_commercial():
                commercial = UserView.prompt_select_commercial(commercials)
                if commercial:
                    filter_by_commercial = commercial.epicuser_id
                    # Si un commercial est sélectionné, choisir un client
                    if CustomerView.prompt_confirm_customer():
                        customers = session.query(Customer).filter_by(commercial_id=commercial.epicuser_id).all()
                        selected_customer = CustomerView.prompt_customers(customers)
                        text = (f'Client sélectionné : {selected_customer}')
                        console.print(text, justify="cente", style="bold blue")
                        # Initialiser les filtres
                        filter_by_client = selected_customer.customer_id
                    else:
                        filter_by_client = None
            else:
                filter_by_commercial = None
                if CustomerView.prompt_confirm_customer():
                    customers = session.query(Customer).all()
                    selected_customer = CustomerView.prompt_customers(customers)
                    text = (f'Client sélectionné : {selected_customer}')
                    console.print(text, justify="cente", style="bold blue")
                    # Initialiser les filtres
                    filter_by_client = selected_customer.customer_id
                else:
                    filter_by_client = None

            filter_by_statut = None

            # Sélectionner un contrat si confirmé
            if ContractView.prompt_confirm_contract_state(contracts):
                selected_statut = ContractView.prompt_select_statut()
                filter_by_statut = selected_statut
            else:
                filter_by_statut = None

            # Construire la requête de filtrage des événements
            query = session.query(Contract)

            if filter_by_commercial:
                query = query.filter_by(commercial_id=filter_by_commercial)
            if filter_by_client:
                query = query.filter_by(customer_id=filter_by_client)
            if filter_by_statut:
                query = query.filter_by(state=filter_by_statut)
            else:
                query = query

            # Exécuter la requête et afficher les résultats
            contracts = query.all()
            ContractView.display_list_contracts(contracts)

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            print(f"Erreur rencontrée : {e}")
