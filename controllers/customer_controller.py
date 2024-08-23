from models.entities import Customer, Contract
from datetime import datetime
from controllers.decorator import is_authenticated, is_admin, is_commercial
from views.customer_view import CustomerView

class CustomerBase:
    """
    Classe de base pour la gestion des clients, permettant de créer, récupérer,
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

    @is_authenticated
    @is_admin
    @is_commercial
    def create_customer(self, session, customer_data):
        """
        Permet de créer un client.

        Paramètres :
        ------------
        customer_data : dict
            Un dictionnaire contenant les informations du client à créer.

        Retourne :
        ----------
        Customer : Le client créé.
        """
        # Utilisation de .get() pour gérer les clés manquantes
        customer = Customer(
            first_name=customer_data.get('first_name'),
            last_name=customer_data.get('last_name'),
            email=customer_data.get('email'),
            phone=customer_data.get('phone'),
            company_name=customer_data.get('company_name'),
            creation_time=datetime.utcnow(),
            update_time=datetime.utcnow(),
            commercial_id=customer_data.get('commercial_id')  # Gestion de l'absence de commercial_id
        )
        session.add(customer)
        session.commit()
        return customer

    @is_authenticated
    @is_admin
    @is_commercial
    def get_customer(self, cname: str, session) -> list[Customer]:
        """
        Récupère la liste des clients selon le nom du commercial.

        Paramètres :
        ------------
        cname (str) : Nom du commercial.
        session (Session) : La session SQLAlchemy à utiliser.

        Retourne :
        ----------
        List[Customer] : Liste des clients associés.
        """
        # Exemple d'utilisation de session pour une requête
        return session.query(Customer).filter(Customer.last_name == cname).all()

    @is_authenticated
    def get_all_customers(self):
        """
        Permet de retourner la liste de tous les clients.

        Retourne :
        ----------
        list[Customer] : La liste de tous les clients.
        """
        return self.session.query(Customer).all()

    @is_authenticated
    @is_admin
    @is_commercial
    def update_customer(self, session, customer_id):
        """
        Permet de mettre à jour le profil d'un client via son ID.

        Paramètres :
        ------------
        customer_id : int
            L'ID du client à mettre à jour.
        data : dict
            Un dictionnaire contenant les nouvelles valeurs pour les attributs du client.

        Exceptions :
        ------------
        ValueError :
            Levée si aucun client n'est trouvé avec l'ID spécifié.
        """
        data = CustomerView.prompt_data_customer(customer_id)
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            raise ValueError("Aucun client n'a été trouvé.")

        for key, value in data.items():
            setattr(customer, key, value)

        session.commit()

    @is_authenticated
    @is_admin
    @is_commercial
    def find_without_contract(self):
        """
        Permet de lister tous les clients qui n'ont pas de contrat associé.

        Retourne :
        ----------
        list[Customer] : La liste des clients sans contrat.
        """
        return self.session.query(Customer).outerjoin(Customer.contracts).filter(Contract.customer_id.is_(None)).all()

    @classmethod
    def update_commercial_customer(cls, current_user, session, customer_id, commercial_id):
        """
        Met à jour le commercial attribué à un client.

        Paramètres :
        ------------
        current_user : EpicUser
            L'utilisateur actuel effectuant la mise à jour.
        session : SQLAlchemy Session
            La session utilisée pour effectuer les opérations de base de données.
        customer_id : int
            L'ID du client à mettre à jour.
        commercial_id : int
            L'ID du nouveau commercial à attribuer au client.

        Exceptions :
        ------------
        ValueError :
            Levée si aucun client n'est trouvé avec l'ID spécifié.
        """
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            raise ValueError("Aucun client trouvé avec l'ID spécifié.")

        # Mise à jour du commercial
        customer.commercial_id = commercial_id
        session.commit()
        print(f"Commercial ID {commercial_id} attribué au client ID {customer_id}.")
