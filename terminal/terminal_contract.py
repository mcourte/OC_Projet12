import os
import sys


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, is_commercial, is_gestion, is_admin)
from terminal.terminal_customer import EpicTerminalCustomer
from terminal.terminal_user import EpicTerminalUser

from views.console_view import console
from views.prompt_view import PromptView
from views.regexformat import regexformat
from views.contract_view import ContractView
from views.customer_view import CustomerView
from views.menu_view import MenuView
from views.data_view import DataView


class EpicTerminalContract():

    def __init__(self, user, base):
        self.user = user
        self.epic = base
        self.controller_user = EpicTerminalUser(self.user, self.epic)
        self.controller_customer = EpicTerminalCustomer(self.user, self.epic)

    @is_authenticated
    def list_of_contracts(self) -> None:
        """
            - offers to select a commercial
            - offers to select a client
            - offers to select a stat
            - read database and display data
        """
        state = None
        cname = self.controller_user.choice_commercial()
        customer = self.controller_customer.choice_customer(cname)
        # select a state
        result = PromptView.prompt_confirm_statut()
        if result:
            states = self.epic.db_contracts.get_all_contracts()
            try:
                state = ContractView.prompt_select_statut(states)
            except KeyboardInterrupt:
                state = None
        # display list
        ContractView.display_list_contracts(
            self.epic.db_contracts.get_all_contracts())

    @is_authenticated
    @is_gestion
    @is_admin
    def create_contract(self) -> None:
        """
            - ask to select a client
            - ask data of contract
            - update database
            - generate a task waiting to be signed
        """
        clients = self.epic.db_customers.get_clients()
        enames = [c.first_name for c in clients]
        ename = CustomerView.prompt_client(enames)
        try:
            data = ContractView.prompt_data_contract()
            self.epic.db_contracts.create(ename, data)
            contract_ref = data['ref']
            text = f'Contrat {contract_ref} en attente de signature'
        except KeyboardInterrupt:
            DataView.display_interupt()

    @is_authenticated
    @is_gestion
    @is_commercial
    def update_contract(self):
        """
            - ask to select a contract in a list of active contract
            - ask which operation todo
                - you can add a paiement then:
                    - ask data for paiement
                    - create paiement in database
                - you can modify the data then:
                    - display the data of actuel contract
                    - ask for new data
                    - update database
                    - display new data
                - you can signed a contrat
                - you can cancel a contract
        """
        contracts = self.epic.db_contracts.get_active_contracts()
        refs = [c.ref for c in contracts]
        ref = ContractView.prompt_select_contract(refs)
        print(ref)
        state = self.epic.db_contracts.state_signed(ref)
        try:
            choice = MenuView.menu_update_contract(state)
            match choice:
                case 1:
                    try:
                        data = ContractView.prompt_data_paiement()
                        self.epic.db_contracts.add_paiement(ref, data)
                    except KeyboardInterrupt:
                        DataView.display_interupt()
                case 2:
                    try:
                        contract = self.epic.db_contracts.get(ref)
                        ContractView.display_contract_info(contract)
                        data = ContractView.prompt_data_contract(
                            ref_required=False, mt_required=False)
                        newref = self.epic.db_contracts.update(ref, data)
                        contract = self.epic.db_contracts.get(newref)
                        ContractView.display_contract_info(contract)
                    except KeyboardInterrupt:
                        DataView.display_interupt()
                case 3:
                    self.epic.db_contracts.signed(ref)
                    text = f'Creer les évènements du contrat {ref}'
                    contract = self.epic.db_contracts.get(ref)
                    DataView.display_workflow()
        except KeyboardInterrupt:
            DataView.display_interupt()
