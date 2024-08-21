from models.entities import Customer, Contract
from datetime import datetime
from controllers.decorator import is_authenticated, is_admin, is_commercial


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
    def create_customer(self, customer_data):
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
        self.session.add(customer)
        self.session.commit()
        return customer

    @is_authenticated
    @is_admin
    @is_commercial
    def get_customer(self, customer_id):
        """
        Permet de retrouver un client via son ID.

        Paramètres :
        ------------
        customer_id : int
            L'ID du client à retrouver.

        Retourne :
        ----------
        Customer : Le client correspondant à l'ID, ou None s'il n'existe pas.
        """
        return self.session.query(Customer).filter_by(customer_id=customer_id).first()

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
    def update_customer(self, customer_id, data):
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
        customer = self.session.query(Customer).filter_by(customer_id=customer_id).first()
        if not customer:
            raise ValueError("Aucun client n'a été trouvé.")

        for key, value in data.items():
            setattr(customer, key, value)

        self.session.commit()

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
