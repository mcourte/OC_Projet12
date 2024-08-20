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


class EpicTerminalEvent():

    def __init__(self, user, base):
        self.user = user
        self.epic = base
        self.controller_user = EpicTerminalUser(self.user, self.epic)
        self.controller_customer = EpicTerminalCustomer(self.user, self.epic)

    @is_authenticated
    @is_gestion
    @is_support
    @is_admin
    def update_event(self):
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
        contracts = self.epic.db_contracts.get_contract(
            commercial_name=self.user.username, state_value='S')
        if contracts:
            contracts = [c.ref for c in contracts]
            contract = ContractView.prompt_select_contract(contracts)
            try:
                data = EventView.prompt_data_event()
                self.epic.db_events.create(contract, data)
                # workflow creation
                DataView.display_workflow()
                gestions = self.epic.db_users.get_gestions()
                gestion = random.choice(gestions)
            except KeyboardInterrupt:
                DataView.display_interupt()
        else:
            DataView.display_nocontracts()

    @is_authenticated
    def list_of_events(self):
        contract_ref = None
        sname = None
        cname = self.controller_user.choice_commercial()
        client = self.controller_customer.choice_customer(cname)
        # select a contract
        result = ContractView.prompt_confirm_contract()
        if result:
            contracts = self.epic.db_contracts.get_contracts(
                cname, client)
            contracts_ref = [c.ref for c in contracts]
            contract_ref = ContractView.prompt_select_contract(contracts_ref)
        # select a support
        result = UserView.prompt_confirm_support()
        if result:
            supports = self.epic.db_users.get_supports()
            supports_name = [c.username for c in supports]
            supports_name.append(EventView.no_support())
            sname = UserView.prompt_select_support(supports_name)
        # display list
        events = self.epic.db_events.get_event(
            cname, client, contract_ref, sname)
        EventView.display_list_events(events)
