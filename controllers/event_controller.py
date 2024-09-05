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
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def create_event(data, session):
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
        # Création de l'événement
        event = Event(
            title=data.get('title'),
            description=data.get('description'),
            location=data.get('location'),
            attendees=data.get('attendees', 0),
            date_started=data.get('date_started'),
            date_ended=data.get('date_ended'),
            contract_id=data.get('contract_id'),
            customer_id=data.get('customer_id'),
            support_id=data.get('support_id')
        )
        session.add(event)
        session.commit()
        return event

    @staticmethod
    @sentry_activate
    @requires_roles('ADM', 'COM', 'GES', 'Admin', 'Commercial', 'Gestion')
    def update_event(event_id, data, session):
        """
        Met à jour un événement existant avec les nouvelles données.

        :param event_id: ID de l'événement à mettre à jour.
        :param data: Dictionnaire contenant les nouvelles informations de l'événement.
        :param session: Session SQLAlchemy pour interagir avec la base de données.
        :raises ValueError: Si l'événement avec l'ID fourni n'existe pas.
        """
        try:
            # Rechercher l'événement dans la base de données
            event = session.query(Event).filter_by(event_id=event_id).first()

            if not event:
                raise ValueError(f"Événement avec l'ID {event_id} non trouvé.")

            # Mise à jour des attributs de l'événement avec les nouvelles données
            for key, value in data.items():
                if hasattr(event, key):
                    setattr(event, key, value)
                else:
                    console.print(f"L'événement n'a pas d'attribut '{key}'.", style="bold red")

            # Sauvegarder les modifications
            session.commit()

        except Exception as e:
            console.print(f"Erreur inattendue : {str(e)}", style="bold red")
            session.rollback()

    @classmethod
    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_support_event(self, session, event_id, support_id):
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
        event = session.query(Event).filter_by(event_id=event_id).first()
        if not event:
            raise ValueError("Aucun évènement trouvé avec l'ID spécifié.")

        # Mise à jour du support
        event.support_id = support_id
        session.commit()
