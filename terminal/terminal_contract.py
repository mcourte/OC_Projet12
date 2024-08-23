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
from views.prompt_view import PromptView
from views.contract_view import ContractView
from views.customer_view import CustomerView
from views.event_view import EventView
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
                        print(data)
                        contract_base_instance = ContractBase(session)  # Passer la session ici
                        paiement = contract_base_instance.add_paiement(selected_contract.contract_id, data)
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
