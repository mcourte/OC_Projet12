# Import généraux
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

# Import Controllers
from controllers.decorator import (is_authenticated, requires_roles, sentry_activate)
from controllers.event_controller import EventBase, Event
from controllers.user_controller import EpicUserBase

# Import Modèles
from models.entities import EpicUser, Commercial, Contract, Gestion, Support

# Import Views
from views.event_view import EventView
from views.data_view import DataView
from views.console_view import console
from views.user_view import UserView

# Import Terminaux
from terminal.terminal_user import EpicTerminalUser
from terminal.terminal_customer import EpicTerminalCustomer


class EpicTerminalEvent:
    """
    Classe pour gérer les événements depuis l'interface terminal.

    Cette classe fournit des méthodes pour mettre à jour, créer, afficher des événements,
    et gérer les attributions de support.
    """

    def __init__(self, base, session):
        """
        Initialise la classe EpicTerminalEvent avec la base de données et la session.

        :param base: L'objet EpicDatabase pour accéder aux opérations de la base de données.
        :param session: La session SQLAlchemy pour effectuer des requêtes.
        """
        self.epic = base
        self.session = session
        self.current_user = None
        self.controller_user = EpicTerminalUser(self.epic, self.session)
        self.controller_customer = EpicTerminalCustomer(self.epic, self.session, self.current_user)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'GES', 'Admin', 'Commercial', 'Gestion')
    def update_event(self, session):
        """
        Permet à l'utilisateur de sélectionner un événement à modifier et de mettre à jour ses informations.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        try:
            if not self.current_user:
                raise ValueError("Utilisateur non connecté ou non valide.")

            # Ne réaffectez pas la session ici, elle est déjà passée en paramètre
            events = session.query(Event).all()

            if events:
                event = EventView.prompt_select_event(events)  # Sélection de l'événement
                data = EventView.prompt_data_event()  # Récupération des nouvelles données de l'événement
                print(f"data type : {type(data)}")
                print(f"event_id : {event.event_id}, type - {type(event.event_id)}")
                print(f"session type : {type(session)}")

                # Passez directement la session à la méthode update_event
                EventBase.update_event(event.event_id, data, session)

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            text = f"Erreur rencontrée: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'GES', 'Admin', 'Commercial', 'Gestion')
    def create_event(self, session):
        """
        Crée un nouvel événement en permettant de :
        - Sélectionner un contrat
        - Saisir les données de l'événement
        - Ajouter l'événement à la base de données
        - Générer un workflow pour le nouvel événement.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        if not self.current_user:
            text = "Erreur : Utilisateur non connecté ou non valide."
            console.print(text, style="bold red")
            return

        try:
            session = session()
            if self.current_user.role == 'COM' and isinstance(self.current_user, Commercial):
                contracts = session.query(Contract).filter(Contract.state == "S",
                                                           Contract.commercial_id == self.current_user.epicuser_id).all()
            else:
                contracts = session.query(Contract).filter_by(state="S").all()

            if contracts:
                contract = EventView.prompt_select_contract(contracts)
                data = EventView.prompt_data_event()
                event = EventBase.create_event(contract, data, session)
                if EventView.prompt_add_support():
                    EpicTerminalEvent.update_event_support(self, session, event)
            else:
                DataView.display_nocontracts()

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            text = f"Erreur rencontrée: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    def list_of_events(self, session):
        """
        Affiche la liste des événements en permettant de :
        - Choisir un commercial (facultatif)
        - Choisir un client (facultatif)
        - Sélectionner un contrat (si confirmé)
        - Sélectionner un support (si confirmé)
        - Lire la base de données et afficher les événements.

        :param session: Session SQLAlchemy pour interagir avec la base de données.
        """
        roles = EpicUserBase.get_roles(self)
        self.roles = roles
        if self.current_user.role == 'GES':
            if isinstance(self.current_user, Gestion):
                if EventView.prompt_filtered_events_gestion():
                    events = session.query(Event).all()
                    EventView.display_list_events(events)
                else:
                    events = session.query(Event).filter_by(support_id=None).all()
                    EventView.display_list_events(events)
        elif self.current_user.role == 'SUP':
            if isinstance(self.current_user, Support):
                if EventView.prompt_filtered_events_support():
                    events = session.query(Event).all()
                    EventView.display_list_events(events)
                else:
                    events = session.query(Event).filter_by(support_id=self.current_user.epicuser_id).all()
                    EventView.display_list_events(events)

        else:
            events = session.query(Event).all()
            EventView.display_list_events(events)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_event_support(self, session) -> None:
        """
        Met à jour le gestionnaire attribué à un contrat en permettant de :
        - Sélectionner un contrat sans gestionnaire
        - Sélectionner un gestionnaire
        - Attribuer le gestionnaire sélectionné au contrat

        Cette méthode met à jour le gestionnaire pour un contrat en fonction des sélections faites.
        """

        # Vérifiez si la session est correctement initialisée
        if session is None:
            text = "Erreur : La session est non initialisée."
            console.print(text, style="bold red")
            return

        # Récupérer tous les événements non attribués à un support
        events = session.query(Event).filter_by(support_id=None).all()
        if events:
            event = EventView.prompt_select_event(events)

        # Récupérer tous les supports
        supports = session.query(EpicUser).filter_by(role='SUP').all()

        # Demander à l'utilisateur de sélectionner un support
        selected_support_username = UserView.prompt_select_support(supports)

        # Récupérer l'ID du support sélectionné
        selected_support = session.query(EpicUser).filter_by(username=selected_support_username).first()
        if not selected_support:
            text = "Erreur : Le support sélectionné n'existe pas."
            console.print(text, style="bold red")
            return
        # Mettre à jour le support de l'évènement
        EventBase.update_support_event(session, event.event_id, selected_support.epicuser_id)
        text = f"Le support {selected_support.username} a été attribué à l'évènement {event.event_id} avec succès."
        console.print(text, style="cyan")
