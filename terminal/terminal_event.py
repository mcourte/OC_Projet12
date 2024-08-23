import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, is_support, is_commercial, is_gestion, is_admin)
from controllers.event_controller import EventBase, Event
from controllers.user_controller import EpicUser
from controllers.contract_controller import Contract
from views.event_view import EventView
from views.data_view import DataView
from terminal.terminal_user import EpicTerminalUser
from terminal.terminal_customer import EpicTerminalCustomer
from views.contract_view import ContractView
from views.user_view import UserView


class EpicTerminalEvent:
    """
    Classe pour gérer les événements depuis l'interface terminal.
    """

    def __init__(self, base, session):
        """
        Initialise la classe EpicTerminalEvent avec l'utilisateur et la base de données.

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
    @is_gestion
    @is_support
    @is_admin
    def update_event(self, session):
        """
        Met à jour un événement en permettant de :
        - Sélectionner un support
        - Sélectionner un contrat
        - Sélectionner un événement à mettre à jour
        - Appliquer les modifications dans la base de données.
        """
        try:
            # Récupérer tous les supports
            supports = session.query(EpicUser).filter_by(role='SUP').all()
            supports = [s.username for s in supports]
            support = UserView.prompt_select_support(supports)
            print(f"Support sélectionné: {support}")

            # Récupérer tous les contrats
            contracts = session.query(Contract).all()
            contract = EventView.prompt_select_contract(contracts)
            print(f"Contrat sélectionné: {contract}")

            # Récupérer tous les événements associés au contrat sélectionné
            events = session.query(Event).filter_by(contract_id=contract.contract_id).all()
            print(f"Nombre d'événements trouvés: {len(events)}")
            if events:
                print(f"Événements associés au contrat sélectionné: {events}")
                event_title = EventView.prompt_select_event(events)
                print(f"Événement sélectionné: {event_title}")

                # Mettre à jour l'événement
                EventBase.update_event(contract, event_title, support)
            else:
                print('Aucun événement trouvé pour le contrat sélectionné.')

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            print(f"Erreur rencontrée: {e}")

    @is_authenticated
    @is_commercial
    @is_admin
    def create_event(self, session):
        """
        Crée un nouvel événement en permettant de :
        - Sélectionner un contrat
        - Saisir les données de l'événement
        - Ajouter l'événement à la base de données
        - Générer un workflow pour le nouvel événement.
        """
        contracts = session.query(Contract).all()
        if contracts:
            contract = EventView.prompt_select_contract(contracts)
            try:
                data = EventView.prompt_data_event()
                EventBase.create_event(contract, data, session)
            except KeyboardInterrupt:
                DataView.display_interupt()
        else:
            DataView.display_nocontracts()

    @is_authenticated
    def list_of_events(self, session):
        """
        Affiche la liste des événements en permettant de :
        - Choisir un commercial
        - Choisir un client
        - Sélectionner un contrat (si confirmé)
        - Sélectionner un support (si confirmé)
        - Lire la base de données et afficher les événements.
        """
        contract_ref = None
        sname = None
        cname = self.controller_user.choice_commercial()
        client = self.controller_customer.choice_customer(session, cname)
        print(f'client : {client}')

        # Sélectionner un contrat
        result = ContractView.prompt_confirm_contract()
        print(f'contract: {result}')
        if result:
            contracts = self.session.query(Event).filter_by(customer_id=client.customer_id).all()
            print(contracts)
            contracts_data = [{"Description": f"{c.description}", "ID": c.contract_id} for c in contracts]
            contract_ref = EventView.prompt_select_contract(contracts_data)

        # Sélectionner un support
        result = UserView.prompt_confirm_support()
        print(f'support: {result}')
        if result:
            supports = self.session.query(EpicUser).filter_by(role='SUP').all()
            supports_name = [c.username for c in supports]
            supports_name.append(EventView.no_support())
            sname = UserView.prompt_select_support(supports_name)
            print(sname)

        # Récupérer l'ID du support sélectionné
        if sname:
            support = self.session.query(EpicUser).filter_by(username=sname).first()
            if support:
                support_id = support.user_id  # Remplacez `user_id` par le nom correct de l'attribut de l'ID du support
                events = self.session.query(Event).filter_by(support_id=support_id).all()
                EventView.display_list_events(events)
            else:
                print('Support non trouvé.')
        else:
            events = self.session.query(Event).all()
            EventView.display_list_events(events)
