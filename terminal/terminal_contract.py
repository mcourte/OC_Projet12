# Import généraux
import os
import sys
from typing import Optional
from sqlalchemy.orm import Session
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

# Import Controllers
from controllers.decorator import (is_authenticated, requires_roles, sentry_activate)
from controllers.contract_controller import ContractBase
from controllers.user_controller import EpicUserBase

# Import Modèles
from models.entities import Customer, Contract, Commercial, EpicUser, Gestion

# Import Terminaux
from terminal.terminal_customer import EpicTerminalCustomer
from terminal.terminal_user import EpicTerminalUser

# Import Views
from views.contract_view import ContractView
from views.customer_view import CustomerView
from views.event_view import EventView
from views.user_view import UserView
from views.data_view import DataView
from views.console_view import console


class EpicTerminalContract:
    """
    Classe pour gérer les contrats depuis l'interface terminal.

    Cette classe fournit des méthodes pour afficher, créer, mettre à jour les contrats,
    ainsi que pour attribuer des gestionnaires aux contrats et ajouter des paiements.
    """

    def __init__(self, base, session):
        """
        Initialise la classe EpicTerminalContract avec l'utilisateur et la base de données.

        :param base: L'objet EpicDatabase pour accéder aux opérations de la base de données.
        :param session: La session SQLAlchemy utilisée pour interagir avec la base de données.
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
        Affiche la liste des contrats en permettant de filtrer par :
        - Commercial
        - Client
        - État du contrat
        - État du paiement

        Les contrats sont affichés en fonction des filtres appliqués.
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
            ContractView.display_list_contracts(contracts)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def create_contract(self, session) -> None:
        """
        Crée un nouveau contrat en permettant de :
        - Sélectionner un client
        - Saisir les données du contrat
        - Ajouter le contrat à la base de données

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        session = session()
        if not self.current_user:
            text = "Erreur : Utilisateur non connecté ou non valide."
            console.print(text, style="bold red")
            return

        try:
            # Vérifiez que session est bien une instance de SQLAlchemy Session
            if not isinstance(session, Session):
                raise ValueError("La session passée n'est pas une instance de SQLAlchemy Session.")

            # Récupérer les clients
            customers = session.query(Customer).all()
            customer_data = [{"name": f"{c.first_name} {c.last_name} {c.customer_id}", "value": c.customer_id} for c in customers]
            customer_id = CustomerView.prompt_client(customer_data)

            # Obtenir les données du contrat
            data = ContractView.prompt_data_contract()
            data['customer_id'] = str(customer_id)
            commercial = session.query(Customer).filter_by(customer_id=customer_id).first()
            if commercial:
                data['commercial_id'] = commercial.commercial_id
            if self.current_user.role == 'GES' and isinstance(self.current_user, Gestion):
                data['gestion_id'] = self.current_user.epicuser_id
                # Créer le contrat
                ContractBase.create_contract(session, data)
            else:
                ContractBase.create_contract(session, data)
                if ContractView.prompt_add_gestion():
                    EpicTerminalContract.update_contract_gestion(self, session)

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            text = f"Erreur rencontrée: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'COM', 'Admin', 'Gestion', 'Commercial')
    def update_contract(self, session):
        """
        Met à jour un contrat existant en permettant de :
        - Sélectionner un contrat à mettre à jour
        - Modifier les informations du contrat
        - Marquer le contrat comme signé

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        try:
            if not self.current_user:
                raise ValueError("Utilisateur non connecté ou non valide.")

            session = session()
            contracts = session.query(Contract).all()

            if self.current_user.role == 'COM' and isinstance(self.current_user, Commercial):
                contracts = [contract for contract in contracts if contract in self.current_user.contracts]
            selected_contract = EventView.prompt_select_contract(contracts)
            if not selected_contract:
                raise ValueError("Contrat sélectionné invalide")

            contract_id = selected_contract.contract_id
            contract = session.query(Contract).filter_by(contract_id=contract_id).first()
            if not contract:
                raise ValueError("Contrat introuvable")

            choice = ContractView.menu_update_contract(contract)

            match choice:
                case 1:
                    data = ContractView.prompt_data_contract()
                    data['remaining_amount'] = data.get('total_amount')
                    ContractBase.update_contract(contract_id, data, session)
                    ContractView.display_contract_info(contract)
                case 2:
                    ContractBase.signed(contract_id, session)

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            text = f"Erreur rencontrée: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_contract_gestion(self, session) -> None:
        """
        Met à jour le gestionnaire attribué à un contrat en permettant de :
        - Sélectionner un contrat sans gestionnaire
        - Sélectionner un gestionnaire
        - Attribuer le gestionnaire sélectionné au contrat

        Cette méthode met à jour le gestionnaire pour un contrat en fonction des sélections faites.
        """

        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return

        # Récupérer tous les contrats sans gestionnaire
        contracts = session.query(Contract).filter_by(gestion_id=None).all()
        ref = EventView.prompt_select_contract(contracts)
        selected_contract = session.query(Contract).filter_by(contract_id=ref.contract_id).first()
        selected_contract_id = selected_contract.contract_id

        # Récupérer tous les gestionnaires
        gestionnaires = session.query(EpicUser).filter_by(role='GES').all()

        # Demander à l'utilisateur de sélectionner un gestionaire
        selected_gestion_username = UserView.prompt_select_gestion(gestionnaires)

        # Récupérer l'ID du gestionnaire sélectionné
        selected_gestion = session.query(EpicUser).filter_by(username=selected_gestion_username).first()
        if not selected_gestion:
            text = "Erreur : Le gestionnaire sélectionné n'existe pas."
            console.print(text, style="bold red")
            return
        # Mettre à jour le gestionnaire du contrat
        ContractBase.update_gestion_contract(session, selected_contract_id, selected_gestion.epicuser_id)
        text = f"Le gestionnaire {selected_gestion.username} a été attribué au contrat {selected_contract_id} avec succès."
        console.print(text, style="cyan")
        ContractBase.update_contract

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_contract_choose(self, session, contract) -> None:
        """
        Met à jour le gestionnaire attribué à un contrat spécifique en permettant de :
        - Sélectionner un gestionnaire
        - Attribuer le gestionnaire sélectionné au contrat donné

        Cette méthode met à jour le gestionnaire pour un contrat spécifique en fonction des sélections faites.
        """
        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return
        # Récupérer tous les gestionnaires
        gestionnaires = session.query(EpicUser).filter_by(role='GES').all()

        # Demander à l'utilisateur de sélectionner un gestionaire
        selected_gestion_username = UserView.prompt_select_gestion(gestionnaires)

        # Récupérer l'ID du gestionnaire sélectionné
        selected_gestion = session.query(EpicUser).filter_by(username=selected_gestion_username).first()
        if not selected_gestion:
            text = "Erreur : Le gestionnaire sélectionné n'existe pas."
            console.print(text, style="bold red")
            return

        # Mettre à jour le gestionnaire du contrat
        ContractBase.update_gestion_contract(self.current_user, session, contract.contract_id, selected_gestion.epicuser_id)
        text = f"Le gestionnaire {selected_gestion.username} a été attribué au contrat {contract} avec succès."
        console.print(text, style="cyan")
        ContractBase.update_contract

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def add_paiement_contract(self, session):
        """
        Ajoute un paiement à un contrat en permettant de :
        - Sélectionner un contrat
        - Saisir les informations de paiement

        Cette méthode ajoute les détails du paiement à un contrat spécifique.
        """
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
