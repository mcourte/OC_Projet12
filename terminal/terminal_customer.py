import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import is_authenticated, requires_roles
from controllers.user_controller import EpicUserBase, EpicUser
from controllers.customer_controller import CustomerBase
from views.user_view import UserView
from views.customer_view import CustomerView
from models.entities import Customer


class EpicTerminalCustomer:
    """
    Classe pour gérer les clients depuis l'interface terminal.
    """

    def __init__(self, base, session, current_user):
        """
        Initialise la classe EpicTerminalCustomer avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        session (Session) : La session de base de données pour effectuer des requêtes.
        current_user (EpicUser) : L'utilisateur actuellement connecté.
        """
        self.epic = base
        self.session = session
        self.current_user = current_user  # Définir correctement l'utilisateur ici

    def choice_customer(self, session, commercial_username: str) -> str:
        """
        Permet à l'utilisateur de choisir un client parmi ceux affectés au commercial sélectionné.

        Arguments :
        -----------
        session (Session) : Session SQLAlchemy pour interagir avec la base de données.
        commercial_username (str) : Nom d'utilisateur du commercial.

        Retourne :
        -----------
        str : Nom complet du client sélectionné ou None si aucun client n'est sélectionné.
        """
        # Joindre le modèle Customer au modèle User et filtrer par le nom d'utilisateur du commercial
        customers = session.query(Customer).join(Customer.commercial).filter(EpicUser.username == commercial_username).all()

        if not customers:
            print("Aucun client n'est associé à ce commercial.")
            return None

        # Afficher la liste des clients pour sélection
        selected_customer = CustomerView.prompt_customers(customers)

        return selected_customer

    @is_authenticated
    def list_of_customers(self, session) -> None:
        """
        Affiche la liste des contrats en permettant de :
        - Sélectionner un commercial
        - Sélectionner un client parmi ceux affectés au commercial
        - Sélectionner un état
        - Lire la base de données et afficher les contrats.
        """
        customers = session.query(Customer).all()
        if not customers:
            print("Aucun client sélectionné. Retour au menu principal.")
            return
        CustomerView.display_list_customers(customers)

    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_customer_commercial(self, session) -> None:
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

        # Récupérer tous les clients
        customers = session.query(Customer).filter_by(commercial_id=None).all()
        customers_data = [{"name": f"{c.first_name} {c.last_name}", "value": c.customer_id} for c in customers]

        # Demander à l'utilisateur de sélectionner un client
        selected_customer_id = CustomerView.prompt_client(customers_data)
        if not selected_customer_id:
            print("Erreur : Aucun client sélectionné.")
            return

        # Récupérer tous les commerciaux
        commercials = session.query(EpicUser).filter_by(role='COM').all()
        commercial_usernames = [c.username for c in commercials]

        # Demander à l'utilisateur de sélectionner un commercial
        selected_commercial_username = UserView.prompt_commercial(commercial_usernames)
        if not selected_commercial_username:
            print("Erreur : Aucun commercial sélectionné.")
            return

        # Récupérer l'ID du commercial sélectionné
        selected_commercial = session.query(EpicUser).filter_by(username=selected_commercial_username).first()
        if not selected_commercial:
            print("Erreur : Le commercial sélectionné n'existe pas.")
            return

        # Mettre à jour le commercial du client
        CustomerBase.update_commercial_customer(self.current_user, session, selected_customer_id, selected_commercial.epicuser_id)
        print(f"Le commercial {selected_commercial.username} a été attribué au client {selected_customer_id} avec succès.")

    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def create_customer(self, session) -> None:
        """
        Crée un nouveau client en permettant de :
        - Saisir les données du client
        - Sélectionner un gestionnaire aléatoire
        - Envoyer une tâche au gestionnaire pour créer le contrat.
        """
        roles = EpicUserBase.get_roles(self)
        self.roles = roles
        data = CustomerView.prompt_data_customer()
        customer = CustomerBase.create_customer(self.current_user, session, data)
        if CustomerView.prompt_confirm_commercial():
            EpicTerminalCustomer.add_customer_commercial(self, session, customer)

    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def update_customer(self, session):
        """
        Met à jour les informations d'un client en permettant de :
        - Sélectionner un client parmi ceux de la liste de l'utilisateur
        - Afficher les informations du client
        - Saisir les nouvelles données
        - Mettre à jour la base de données
        - Afficher les nouvelles informations du client.
        """
        # Vérifiez si la session est correctement initialisée
        if session is None:
            print("Erreur : La session est non initialisée.")
            return

        # Vérifiez si l'utilisateur actuel est correctement défini
        if self.current_user is None:
            print("Erreur : Utilisateur non connecté.")
            return

        roles = EpicUserBase.get_roles(self)
        self.roles = roles

        # Récupérer tous les clients associés à l'utilisateur actuel
        customers = session.query(Customer).filter_by(commercial_id=self.current_user.epicuser_id).all()
        customers_data = [{"name": f"{c.first_name} {c.last_name}", "value": c.customer_id} for c in customers]

        # Vérifiez s'il y a des clients associés
        if not customers_data:
            print("Aucun client trouvé pour ce commercial.")
            return

        selected_customer_id = CustomerView.prompt_client(customers_data)

        # Vérifiez si l'ID du client sélectionné est valide
        if selected_customer_id is None:
            print("Erreur : Aucune sélection de client.")
            return

        # Rechercher le client par ID
        customer = session.query(Customer).filter_by(customer_id=selected_customer_id).one_or_none()
        if customer:
            # Utilisation des attributs de l'objet client
            title = f"Données du client {customer}"
            # Afficher ou manipuler les données du client
            print(title)
        else:
            print("Aucun client trouvé avec cet ID.")
            return  # Sortir si le client n'existe pas

        # Mettre à jour le client avec les nouvelles données
        CustomerBase.update_customer(self.current_user, session, selected_customer_id)

    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def add_customer_commercial(self, session, customer) -> None:
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

        # Récupérer tous les commerciaux
        commercials = session.query(EpicUser).filter_by(role='COM').all()
        commercial_usernames = [c.username for c in commercials]

        # Demander à l'utilisateur de sélectionner un commercial
        selected_commercial_username = UserView.prompt_commercial(commercial_usernames)
        if not selected_commercial_username:
            print("Erreur : Aucun commercial sélectionné.")
            return

        # Récupérer l'ID du commercial sélectionné
        selected_commercial = session.query(EpicUser).filter_by(username=selected_commercial_username).first()
        if not selected_commercial:
            print("Erreur : Le commercial sélectionné n'existe pas.")
            return

        # Mettre à jour le commercial du client
        CustomerBase.update_commercial_customer(self.current_user, session, customer.customer_id, selected_commercial.epicuser_id)
        print(f"Le commercial {selected_commercial.username} a été attribué au client {customer} avec succès.")
