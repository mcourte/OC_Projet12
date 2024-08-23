import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, is_gestion, is_admin)
from controllers.contract_controller import ContractBase
from terminal.terminal_customer import EpicTerminalCustomer
from terminal.terminal_user import EpicTerminalUser
from models.entities import Customer, Contract
from controllers.user_controller import EpicUser
from views.prompt_view import PromptView
from views.contract_view import ContractView
from views.customer_view import CustomerView
from views.event_view import EventView
from views.user_view import UserView
from views.menu_view import MenuView
from views.data_view import DataView


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
        self.controller_customer = EpicTerminalCustomer(self.epic, self.session)

    @is_authenticated
    def list_of_contracts(self, session) -> None:
        """
        Affiche la liste des contrats en permettant de :
        - Sélectionner un commercial
        - Sélectionner un client parmi ceux affectés au commercial
        - Sélectionner un état
        - Lire la base de données et afficher les contrats.
        """
        state = None

        # Sélectionner un commercial
        cname = self.controller_user.choice_commercial()

        # Sélectionner un client parmi ceux affectés au commercial
        customer = self.controller_customer.choice_customer(session, cname)
        contracts = session.query(Contract).all()
        print(f"contracts récupérés: {contracts}")
        print("Type de chaque contrat:", [type(c) for c in contracts])
        if not customer:
            print("Aucun client sélectionné. Retour au menu principal.")
            return

        # Sélectionner un état
        result = PromptView.prompt_confirm_statut()
        if result:
            contracts = session.query(Contract).filter_by(customer_id=customer.customer_id).all()
            try:
                state = ContractView.prompt_select_statut()
                filtered_contracts = [c for c in contracts if c.state == state]
                ContractView.display_list_contracts(filtered_contracts)

            except KeyboardInterrupt:
                state = None

    @is_authenticated
    @is_gestion
    @is_admin
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

            # Appeler la fonction pour créer le contrat
            ContractBase.create_contract(session, data)

            contract_ref = data['ref']
            text = f'Contrat {contract_ref} en attente de signature'
            return text

        except KeyboardInterrupt:
            DataView.display_interupt()

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
                        contract = self.epic.db_contracts.get_contract(ref)
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
                    text = f'Créez les événements du contrat {ref}'
                    contract = self.epic.db_contracts.get_contract(ref)
                    DataView.display_workflow()
        except KeyboardInterrupt:
            DataView.display_interupt()

    @is_authenticated
    @is_gestion
    @is_admin
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
        contracts = session.query(Contract).all()
        ref = EventView.prompt_select_contract(contracts)
        selected_contract = session.query(Contract).filter_by(contract_id=ref.contract_id).first()
        selected_contract_id = selected_contract.contract_id
        # Récupérer tous les gestionnaires
        users = session.query(EpicUser).filter_by(role='GES').all()

        # Demander à l'utilisateur de sélectionner un gestionnaire
        selected_customer_id = UserView.prompt_select_gestion(users)
        if not selected_customer_id:
            print("Erreur : Aucun contrat sélectionné.")
            return

        # Récupérer tous les commerciaux
        gestions = session.query(EpicUser).filter_by(role='GES').all()
        gestions_usernames = [g.username for g in gestions]

        # Demander à l'utilisateur de sélectionner un commercial
        selected_gestion_username = UserView.prompt_gestion(gestions_usernames)
        if not selected_gestion_username:
            print("Erreur : Aucun getionnaire sélectionné.")
            return

        # Récupérer l'ID du commercial sélectionné
        selected_gestion = session.query(EpicUser).filter_by(username=selected_gestion_username).first()
        if not selected_gestion:
            print("Erreur : Le commercial sélectionné n'existe pas.")
            return

        # Mettre à jour le commercial du client
        ContractBase.update_gestion_contract(self.current_user, session, selected_contract_id, selected_gestion.epicuser_id)
        print(f"Le gestionnaire {selected_gestion.username} a été attribué au contrat {selected_contract_id} avec succès.")
        ContractBase.update_contract
