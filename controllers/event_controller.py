# Import Modèles
from models.entities import Event

# Import Controllers
from controllers.decorator import is_authenticated, requires_roles, sentry_activate

# Import Views
from views.console_view import console


class EventBase:
    """
    Classe pour gérer les opérations liées aux événements dans l'application.

    Cette classe fournit des méthodes pour créer et mettre à jour des événements dans la base de données.
    Elle utilise des décorateurs pour la gestion des sessions et des permissions.
    """

    def __init__(self, session):
        """
        Initialise la classe EventBase avec une session de base de données.

        Paramètres :
        ------------
        session (Session) : La session SQLAlchemy pour interagir avec la base de données.
        """
        self.session = session

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def create_event(self, data, session):
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
        session.add(event)
        session.commit()
        return event

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'GES', 'Admin', 'Commercial', 'Gestion')
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
            raise ValueError("Il n'existe pas d'événements avec cet ID")

        for key, value in data.items():
            setattr(event, key, value)

        self.session.commit()
        text = "L'événement a bien été mis à jour."
        console.print(text, style="bold green")
