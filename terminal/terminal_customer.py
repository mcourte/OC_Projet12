import random

import os
import sys


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import is_authenticated, is_commercial, is_gestion, is_support, is_admin
from views.user_view import UserView
from views.customer_view import CustomerView
from terminal.terminal_user import EpicTerminalUser


class EpicTerminalCustomer():

    def __init__(self, user, base):
        self.user = user
        self.epic = base
        self.controller_employee = EpicTerminalUser(self.user, self.epic)

    def choice_client(self, commercial) -> str:
        """
            - ask to confirm a client selection
            - read database
            - ask to select a client

        Args:
            commercial_name (str): commercial username

        Returns:
            str: client full_name
        """
        customer = None
        # select a client
        result = CustomerView.prompt_confirm_customer()
        if result:
            users = self.epic.db_users.get_commercials(commercial)
            users_name = [c.username for c in users]
            customer = CustomerView.prompt_data_customer(users_name)
        return customer

    @is_authenticated
    def list_of_customers(self) -> None:
        """
            - offers to choose a commercial
            - read database and display data
        """
        cname = self.controller_users.choice_commercial()
        customers = self.epic.db_customers.get_customers(cname)
        CustomerView.display_list_customers(customers)

    @is_authenticated
    @is_gestion
    @is_admin
    def update_customer_commercial(self) -> None:
        """
            - ask to choose a client
            - ask to choose a commercial
            - update database
        """
        clients = self.epic.db_customers.get_clients()
        clients = [c.last_name for c in clients]
        client = CustomerView.prompt_client(clients)
        commercials = self.epic.db_users.get_commercials()
        commercials = [c.username for c in commercials]
        ename = UserView.prompt_commercial(commercials)
        self.epic.db_customers.update_commercial(client, ename)

    @is_authenticated
    @is_commercial
    @is_admin
    def create_customer(self) -> None:
        """
            - ask data of client
            - select a random manager
            - send a task to the manager for creating the contract
        """
        data = CustomerView.prompt_data_customer()
        self.epic.db_customers.create(self.user.username, data)
        gestions = self.epic.db_users.get_gestions()
        e = random.choice(gestions)
        text = 'Creer le contrat du client ' + data['first_name' + ' ' + 'last_name']

    @is_authenticated
    @is_commercial
    @is_admin
    def update_customer(self):
        """
            - ask a select of a client in the clients of user list
            - display client information
            - ask for the new data
            - update databse
            - display new client information
        """
        customers = self.epic.db_users.get_customer(
            commercial_name=self.user.username)
        customers = [c.full_name for c in customers]
        customer_name = CustomerView.prompt_client(customers)
        customer = self.epic.db_customers.get(customer_name)
        CustomerView.display_customer_info(customer)
        data = CustomerView.prompt_data_customer(full_name_required=False)
        customer_name = self.epic.db_customers.update(customer_name, data)
        print(f'get {customer_name}')
        customer = self.epic.db_customers.get(customer_name)
        CustomerView.display_customer_info(customer)
