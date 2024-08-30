# Import générauw
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


# Import Controllers
from controllers.decorator import is_authenticated, requires_roles, sentry_activate
from controllers.user_controller import EpicUserBase, EpicUser
from controllers.customer_controller import CustomerBase

# Import Modèles
from models.entities import Customer, Commercial

# Import Views
from views.user_view import UserView
from views.customer_view import CustomerView
from views.console_view import console


class EpicTerminalCustomer:
    """
    Classe pour gérer les clients depuis l'interface terminal.

    Cette classe fournit des méthodes pour afficher, créer, mettre à jour les clients,
    et gérer leur attribution aux commerciaux.
    """

    def __init__(self, base, session, current_user):
        """
        Initialise la classe EpicTerminalCustomer avec l'utilisateur et la base de données.

        :param base: L'objet EpicDatabase pour accéder aux opérations de la base de données.
        :param session: La session SQLAlchemy pour effectuer des requêtes.
        :param current_user: L'utilisateur actuellement connecté.
        """
        self.epic = base
        self.session = session
        self.current_user = current_user  # Définir correctement l'utilisateur ici

    def choice_customer(self, session, commercial_username: str) -> str:
        """
        Permet à l'utilisateur de choisir un client parmi ceux affectés au commercial sélectionné.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        :param commercial_username: Nom d'utilisateur du commercial.

        :return: Nom complet du client sélectionné ou None si aucun client n'est sélectionné.
        """
        # Joindre le modèle Customer au modèle User et filtrer par le nom d'utilisateur du commercial
        customers = session.query(Customer).join(Customer.commercial).filter(EpicUser.username == commercial_username).all()

        if not customers:
            text = "Aucun client n'est associé à ce commercial."
            console.print(text, style="bold red")
            return None

        # Afficher la liste des clients pour sélection
        selected_customer = CustomerView.prompt_customers(customers)

        return selected_customer

    @sentry_activate
    @is_authenticated
    def list_of_customers(self, session) -> None:
        """
        Affiche la liste des clients en permettant de :
        - Sélectionner un commercial
        - Sélectionner un client parmi ceux affectés au commercial
        - Sélectionner un état
        - Lire la base de données et afficher les clients.

        Cette méthode récupère tous les clients et les affiche.
        """
        customers = session.query(Customer).all()
        if not customers:
            text = "Aucun client existant. Retour au menu principal."
            console.print(text, style="red")
            return
        CustomerView.display_list_customers(customers)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion', 'COM', 'Commercial')
    def update_customer_commercial(self, session) -> None:
        """
        Met à jour le commercial attribué à un client.

        Cette méthode permet de :
        - Sélectionner un client.
        - Sélectionner un commercial.
        - Attribuer le commercial sélectionné au client sélectionné.
        - Mettre à jour la base de données.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return

        # Récupérer tous les clients sans commercial
        customers = session.query(Customer).filter_by(commercial_id=None).all()
        customers_data = [{"name": f"{c.first_name} {c.last_name}", "value": c.customer_id} for c in customers]

        # Demander à l'utilisateur de sélectionner un client
        selected_customer_id = CustomerView.prompt_client(customers_data)
        if not selected_customer_id:
            text = "Erreur : Aucun client sélectionné."
            console.print(text, style="red")
            return

        # Récupérer tous les commerciaux
        commercials = session.query(EpicUser).filter_by(role='COM').all()
        commercial_usernames = [c.username for c in commercials]

        # Demander à l'utilisateur de sélectionner un commercial
        selected_commercial_username = UserView.prompt_commercial(commercial_usernames)
        if not selected_commercial_username:
            text = "Erreur : Aucun commercial sélectionné."
            console.print(text, style="bold red")
            return

        # Récupérer l'ID du commercial sélectionné
        selected_commercial = session.query(EpicUser).filter_by(username=selected_commercial_username).first()
        if not selected_commercial:
            text = "Erreur : Le commercial sélectionné n'existe pas."
            console.print(text, style="bold red")
            return

        # Mettre à jour le commercial du client
        CustomerBase.update_commercial_customer(self.current_user, session, selected_customer_id, selected_commercial.epicuser_id)
        text = f"Le commercial {selected_commercial.username} a été attribué au client {selected_customer_id} avec succès."
        console.print(text, style="cyan")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def create_customer(self, session) -> None:
        """
        Crée un nouveau client en permettant de :
        - Saisir les données du client
        - Sélectionner un gestionnaire aléatoire
        - Envoyer une tâche au gestionnaire pour créer le contrat.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        if not self.current_user:
            text = "Erreur : Utilisateur non connecté ou non valide."
            console.print(text, style="bold red")
            return

        roles = EpicUserBase.get_roles(self)
        self.roles = roles
        data = CustomerView.prompt_data_customer()
        if self.current_user.role == 'COM':
            if isinstance(self.current_user, Commercial):
                data['commercial_id'] = self.current_user.epicuser_id
                customer = CustomerBase.create_customer(self.current_user, session, data)
        else:
            if CustomerView.prompt_confirm_commercial():
                EpicTerminalCustomer.add_customer_commercial(self, session, customer)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def update_customer(self, session):
        """
        Met à jour les informations d'un client en permettant de :
        - Sélectionner un client parmi ceux associés à l'utilisateur
        - Afficher les informations du client
        - Saisir les nouvelles données
        - Mettre à jour la base de données
        - Afficher les nouvelles informations du client.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return

        # Vérifiez si l'utilisateur actuel est correctement défini
        if self.current_user is None:
            text = "Erreur : Utilisateur non connecté."
            console.print(text, style="bold red")
            return

        roles = EpicUserBase.get_roles(self)
        self.roles = roles

        # Récupérer tous les clients associés à l'utilisateur actuel
        customers = session.query(Customer).filter_by(commercial_id=self.current_user.epicuser_id).all()
        customers_data = [{"name": f"{c.first_name} {c.last_name}", "value": c.customer_id} for c in customers]

        # Vérifiez s'il y a des clients associés
        if not customers_data:
            text = "Aucun client trouvé pour ce commercial."
            console.print(text, style="red")
            return

        selected_customer_id = CustomerView.prompt_client(customers_data)

        # Vérifiez si l'ID du client sélectionné est valide
        if selected_customer_id is None:
            text = "Erreur : Aucune sélection de client."
            console.print(text, style="red")
            return

        # Rechercher le client par ID
        customer = session.query(Customer).filter_by(customer_id=selected_customer_id).one_or_none()
        if customer:
            # Utilisation des attributs de l'objet client
            title = f"Données du client {customer}"
            # Afficher ou manipuler les données du client
            console.print(title, style="bold cyan")
        else:
            text = "Aucun client trouvé avec cet ID."
            console.print(text, style="red")
            return  # Sortir si le client n'existe pas

        # Mettre à jour le client avec les nouvelles données
        CustomerBase.update_customer(self.current_user, session, selected_customer_id)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion', 'COM', 'Commercial')
    def add_customer_commercial(self, session, customer) -> None:
        """
        Met à jour le commercial attribué à un client.

        Cette méthode permet de :
        - Sélectionner un client.
        - Sélectionner un commercial.
        - Attribuer le commercial sélectionné au client sélectionné.
        - Mettre à jour la base de données.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        :param customer: L'objet client pour lequel le commercial doit être mis à jour.
        """
        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return

        # Récupérer tous les commerciaux
        commercials = session.query(EpicUser).filter_by(role='COM').all()
        commercial_usernames = [c.username for c in commercials]

        # Demander à l'utilisateur de sélectionner un commercial
        selected_commercial_username = UserView.prompt_commercial(commercial_usernames)
        if not selected_commercial_username:
            text = "Erreur : Aucun commercial sélectionné."
            console.print(text, style="bold red")
            return

        # Récupérer l'ID du commercial sélectionné
        selected_commercial = session.query(EpicUser).filter_by(username=selected_commercial_username).first()
        if not selected_commercial:
            text = "Erreur : Le commercial sélectionné n'existe pas."
            console.print(text, style="bold red")
            return

        # Mettre à jour le commercial du client
        CustomerBase.update_commercial_customer(self.current_user, session, customer.customer_id, selected_commercial.epicuser_id)
        text = f"Le commercial {selected_commercial.username} a été attribué au client {customer} avec succès."
        console.print(text, style="cyan")
