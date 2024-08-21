from models.entities import Event
from controllers.decorator import is_authenticated, is_admin, is_commercial, is_gestion


class EventBase:
    """
    Classe pour gérer les opérations liées aux événements dans l'application.
    """

    def __init__(self, session):
        """
        Initialise la classe EventBase avec une session de base de données.

        Paramètres :
        ------------
        session (Session) : La session SQLAlchemy pour interagir avec la base de données.
        """
        self.session = session

    @is_authenticated
    @is_admin
    @is_commercial
    def create_event(self, data):
        """
        Crée un nouvel événement avec les données fournies.

        Paramètres :
        ------------
        data (dict) : Dictionnaire contenant les informations de l'événement, telles que :
                      - title : Titre de l'événement.
                      - description : Description de l'événement.
                      - location : Lieu de l'événement.
                      - attendees : Nombre d'invités (par défaut à 0 si non fourni).
                      - date_started : Date de début de l'événement.
                      - date_ended : Date de fin de l'événement.
                      - contract_id : ID du contrat associé.
                      - customer_id : ID du client associé.
                      - support_id : ID du support associé.

        Retourne :
        ----------
        Event : L'événement créé.
        """
        # Utilisez .get() pour gérer les clés manquantes
        event = Event(
            title=data.get('title'),
            description=data.get('description'),
            location=data.get('location'),
            attendees=data.get('attendees', 0),  # Par défaut à 0 si non fourni
            date_started=data.get('date_started'),
            date_ended=data.get('date_ended'),
            contract_id=data.get('contract_id'),
            customer_id=data.get('customer_id'),
            support_id=data.get('support_id')
        )
        self.session.add(event)
        self.session.commit()
        return event

    @is_authenticated
    @is_admin
    @is_commercial
    def get_event(self, event_id):
        """
        Récupère un événement à partir de son ID.

        Paramètres :
        ------------
        event_id (int) : ID de l'événement à récupérer.

        Retourne :
        ----------
        Event : L'événement correspondant à l'ID, ou None si l'événement n'existe pas.
        """
        return self.session.query(Event).filter_by(event_id=event_id).first()

    @is_authenticated
    def get_all_events(self):
        """
        Récupère tous les événements de la base de données.

        Retourne :
        ----------
        list : Liste de tous les événements.
        """
        return self.session.query(Event).all()

    @is_authenticated
    @is_admin
    @is_commercial
    @is_gestion
    def update_event(self, event_id, data):
        """
        Met à jour un événement existant avec les nouvelles données.

        Paramètres :
        ------------
        event_id (int) : ID de l'événement à mettre à jour.
        data (dict) : Dictionnaire contenant les nouvelles informations de l'événement.

        Lève :
        ------
        ValueError : Si l'événement avec l'ID fourni n'existe pas.
        """
        event = self.session.query(Event).filter_by(event_id=event_id).first()
        if not event:
            raise ValueError("Événement non trouvé.")

        for key, value in data.items():
            setattr(event, key, value)

        self.session.commit()
