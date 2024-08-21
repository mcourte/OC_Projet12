import random
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import is_authenticated, is_commercial, is_gestion, is_admin
from views.user_view import UserView
from views.customer_view import CustomerView
from terminal.terminal_user import EpicTerminalUser


class EpicTerminalCustomer:
    """
    Classe pour gérer les clients depuis l'interface terminal.
    """

    def __init__(self, user, base):
        """
        Initialise la classe EpicTerminalCustomer avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        user (EpicUser) : L'utilisateur actuellement connecté.
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        """
        self.user = user
        self.epic = base
        self.controller_user = EpicTerminalUser(self.user, self.epic)

    def choice_customer(self, commercial) -> str:
        """
        Permet de choisir un client en confirmant la sélection.

        Arguments :
        -----------
        commercial (str) : Nom d'utilisateur du commercial.

        Retourne :
        -----------
        str : Nom complet du client sélectionné.
        """
        customer = None
        # Sélectionner un client
        result = CustomerView.prompt_confirm_customer()
        if result:
            users = self.epic.db_users.get_all_commercials()
            users_name = [c.username for c in users]
            customer = CustomerView.prompt_data_customer(users_name)
        return customer

    @is_authenticated
    def list_of_customers(self) -> None:
        """
        Affiche la liste des clients en permettant de :
        - Choisir un commercial
        - Lire la base de données et afficher les données.
        """
        cname = self.controller_user.choice_commercial()
        customers = self.epic.db_customers.get_customer(cname)
        CustomerView.display_list_customers(customers)

    @is_authenticated
    @is_gestion
    @is_admin
    def update_customer_commercial(self) -> None:
        """
        Met à jour le commercial attribué à un client en permettant de :
        - Choisir un client
        - Choisir un commercial
        - Mettre à jour la base de données.
        """
        customers = self.epic.db_customers.get_all_customers()
        customers = [c.last_name for c in customers]
        customer = CustomerView.prompt_client(customers)
        commercials = self.epic.db_users.get_all_commercials()
        commercials = [c.username for c in commercials]
        username = UserView.prompt_commercial(commercials)
        self.epic.db_customers.update_customer(customer, username)

    @is_authenticated
    @is_commercial
    @is_admin
    def create_customer(self) -> None:
        """
        Crée un nouveau client en permettant de :
        - Saisir les données du client
        - Sélectionner un gestionnaire aléatoire
        - Envoyer une tâche au gestionnaire pour créer le contrat.
        """
        data = CustomerView.prompt_data_customer()
        self.epic.db_customers.create_customer(self.user.username, data)
        gestions = self.epic.db_users.get_all_gestions()
        username = random.choice(gestions)
        text = 'Créer le contrat du client ' + data['first_name'] + ' ' + data['last_name']

    @is_authenticated
    @is_commercial
    @is_admin
    def update_customer(self):
        """
        Met à jour les informations d'un client en permettant de :
        - Sélectionner un client parmi ceux de la liste de l'utilisateur
        - Afficher les informations du client
        - Saisir les nouvelles données
        - Mettre à jour la base de données
        - Afficher les nouvelles informations du client.
        """
        customers = self.epic.db_users.get_customer(
            commercial_name=self.user.username)
        customers = [c.last_name for c in customers]
        customer_name = CustomerView.prompt_client(customers)
        customer = self.epic.db_customers.get_customer(customer_name)
        CustomerView.display_customer_info(customer)
        data = CustomerView.prompt_data_customer(full_name_required=False)
        customer_name = self.epic.db_customers.update_customer(customer_name, data)
        print(f'Client mis à jour : {customer_name}')
        customer = self.epic.db_customers.get_customer(customer_name)
        CustomerView.display_customer_info(customer)
