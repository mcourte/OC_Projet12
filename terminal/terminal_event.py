import random
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, is_support, is_commercial, is_gestion, is_admin)
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

    def __init__(self, user, base):
        """
        Initialise la classe EpicTerminalEvent avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        user (EpicUser) : L'utilisateur actuellement connecté.
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        """
        self.user = user
        self.epic = base
        self.controller_user = EpicTerminalUser(self.user, self.epic)
        self.controller_customer = EpicTerminalCustomer(self.user, self.epic)

    @is_authenticated
    @is_gestion
    @is_support
    @is_admin
    def update_event(self):
        """
        Met à jour un événement en permettant de :
        - Sélectionner un support
        - Sélectionner un contrat
        - Sélectionner un événement à mettre à jour
        - Appliquer les modifications dans la base de données.
        """
        try:
            supports = self.epic.db_users.get_supports()
            supports = [s.username for s in supports]
            support = UserView.prompt_select_support(supports)
            contracts = self.epic.db_contracts.get_active_contracts()
            contracts = [c.ref for c in contracts]
            contract = ContractView.prompt_select_contract(contracts)
            events = self.epic.db_events.get_events(
                contract_ref=contract, state_code='U',
                support_name=EventView.no_support())
            events = [e.title for e in events]
            if events:
                event_title = EventView.prompt_select_event(events)
                self.epic.db_events.update(contract, event_title, support)
                DataView.display_workflow()
            else:
                EventView.no_event()
        except KeyboardInterrupt:
            DataView.display_interupt()

    @is_authenticated
    @is_commercial
    @is_admin
    def create_event(self):
        """
        Crée un nouvel événement en permettant de :
        - Sélectionner un contrat
        - Saisir les données de l'événement
        - Ajouter l'événement à la base de données
        - Générer un workflow pour le nouvel événement.
        """
        contracts = self.epic.db_contracts.get_contract(
            commercial_name=self.user.username, state_value='S')
        if contracts:
            contracts = [c.ref for c in contracts]
            contract = ContractView.prompt_select_contract(contracts)
            try:
                data = EventView.prompt_data_event()
                self.epic.db_events.create(contract, data)
                # Création du workflow
                DataView.display_workflow()
                gestions = self.epic.db_users.get_gestions()
                gestion = random.choice(gestions)
            except KeyboardInterrupt:
                DataView.display_interupt()
        else:
            DataView.display_nocontracts()

    @is_authenticated
    def list_of_events(self):
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
        client = self.controller_customer.choice_customer(cname)
        # Sélectionner un contrat
        result = ContractView.prompt_confirm_contract()
        if result:
            contracts = self.epic.db_contracts.get_contracts(
                cname, client)
            contracts_ref = [c.ref for c in contracts]
            contract_ref = ContractView.prompt_select_contract(contracts_ref)
        # Sélectionner un support
        result = UserView.prompt_confirm_support()
        if result:
            supports = self.epic.db_users.get_supports()
            supports_name = [c.username for c in supports]
            supports_name.append(EventView.no_support())
            sname = UserView.prompt_select_support(supports_name)
        # Afficher la liste
        events = self.epic.db_events.get_event(
            cname, client, contract_ref, sname)
        EventView.display_list_events(events)
