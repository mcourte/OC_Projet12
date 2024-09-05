# Import généraux
from datetime import datetime
# Import des Views
from views.customer_view import CustomerView
from views.console_view import console
# Import des Modèles
from models.entities import Customer
# Import des Controllers
from controllers.decorator import is_authenticated, requires_roles, sentry_activate


class CustomerBase:
    """
    Classe de base pour la gestion des clients. Permet de créer, récupérer,
    mettre à jour et trouver des clients sans contrat associé.
    """

    def __init__(self, session):
        """
        Initialise la classe CustomerBase avec une session SQLAlchemy.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        """
        self.session = session

    def create_customer(session, customer_data):
        """
        Crée un nouveau client avec les informations fournies.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        customer_data : dict
            Un dictionnaire contenant les informations du client à créer, telles que
            'first_name', 'last_name', 'email', 'phone', 'company_name' et
            'commercial_id'. La clé 'commercial_id' peut être absente.

        Retourne :
        ----------
        Customer
            Le client nouvellement créé.
        """
        customer = Customer(
            first_name=customer_data.get('first_name'),
            last_name=customer_data.get('last_name'),
            email=customer_data.get('email'),
            phone=customer_data.get('phone'),
            company_name=customer_data.get('company_name'),
            creation_time=datetime.utcnow(),
            update_time=datetime.utcnow(),
            commercial_id=customer_data.get('commercial_id')
        )
        session.add(customer)
        session.commit()
        console.print(f"Client {customer.first_name} {customer.last_name} ajouté avec succès", style="bold green")
        return customer

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def update_customer(self, session, customer_id):
        """
        Met à jour le profil d'un client existant en utilisant son ID.

        Paramètres :
        ------------
        session : Session
            La session SQLAlchemy pour interagir avec la base de données.
        customer_id : int
            L'ID du client à mettre à jour.

        Exceptions :
        ------------
        ValueError
            Levée si aucun client n'est trouvé avec l'ID spécifié.
        """
        data = CustomerView.prompt_data_customer(customer_id)
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            raise ValueError("Aucun client n'a été trouvé.")

        for key, value in data.items():
            setattr(customer, key, value)
        console.print(f"Client {customer.first_name} {customer.last_name} mis à jour avec succès", style="bold green")

        session.commit()

    @classmethod
    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def update_commercial_customer(self, session, customer_id, commercial_id):
        """
        Met à jour le commercial attribué à un client.

        Paramètres :
        ------------
        cls : type
            La classe CustomerBase.
        current_user : EpicUser
            L'utilisateur actuel effectuant la mise à jour.
        session : Session
            La session SQLAlchemy utilisée pour effectuer les opérations de base de données.
        customer_id : int
            L'ID du client à mettre à jour.
        commercial_id : int
            L'ID du nouveau commercial à attribuer au client.

        Exceptions :
        ------------
        ValueError
            Levée si aucun client n'est trouvé avec l'ID spécifié.
        """

        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            raise ValueError("Aucun client trouvé avec l'ID spécifié.")

        # Mise à jour du commercial
        customer.commercial_id = commercial_id
        session.commit()
        text = f"Commercial ID {commercial_id} attribué au client ID {customer_id}."
        console.print(text, style="bold green")
