import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, requires_roles, sentry_activate)
from controllers.event_controller import EventBase, Event
from controllers.user_controller import EpicUserBase
from models.entities import EpicUser, Commercial, Contract, Gestion, Support
from views.event_view import EventView
from views.data_view import DataView
from views.console_view import console
from terminal.terminal_user import EpicTerminalUser
from terminal.terminal_customer import EpicTerminalCustomer
from views.user_view import UserView


class EpicTerminalEvent:
    """
    Classe pour gérer les événements depuis l'interface terminal.
    """

    def __init__(self, base, session):
        """
        Initialise la classe EpicTerminalEvent avec l'utilisateur et la base de données.

        Paramètres :
        ------------
        user (EpicUser) : L'utilisateur actuellement connecté.
        base (EpicDatabase) : L'objet EpicDatabase pour accéder aux opérations de la base de données.
        """
        self.epic = base
        self.session = session
        self.current_user = None
        self.controller_user = EpicTerminalUser(self.epic, self.session)
        self.controller_customer = EpicTerminalCustomer(self.epic, self.session, self.current_user)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'SUP', 'Admin', 'Gestion', 'Support')
    def update_event(self, session):
        """
        Met à jour un événement en permettant de :
        - Sélectionner un support
        - Sélectionner un contrat
        - Sélectionner un événement à mettre à jour
        - Appliquer les modifications dans la base de données.
        """
        try:
            # Récupérer tous les événements
            events = session.query(Event).filter_by(support_id=None).all()
            if events:
                event = EventView.prompt_select_event(events)
                event_id = event.event_id  # Assurez-vous d'utiliser l'I

                # Récupérer tous les supports
                supports = session.query(EpicUser).filter_by(role='SUP').all()
                supports_dict = {s.username: s.epicuser_id for s in supports}
                support_username = UserView.prompt_select_support(list(supports_dict.keys()))
                support_id = supports_dict[support_username]  # Obtenez l'ID du support sélectionné
                text = f"Support sélectionné: {support_username} (ID: {support_id})"
                console.print(text, style="cyan")

                # Mettre à jour l'événement
                EventBase.update_event(self, event_id, {"support_id": support_id})

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            text = f"Erreur rencontrée: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial', 'GES', 'Gestion')
    def create_event(self, session):
        """
        Crée un nouvel événement en permettant de :
        - Sélectionner un contrat
        - Saisir les données de l'événement
        - Ajouter l'événement à la base de données
        - Générer un workflow pour le nouvel événement.
        """
        if not self.current_user:
            text = "Erreur : Utilisateur non connecté ou non valide."
            console.print(text, style="bold red")
            return

        roles = EpicUserBase.get_roles(self)
        self.roles = roles
        if self.current_user.role == 'COM':
            if isinstance(self.current_user, Commercial):
                contracts = session.query(Contract).filter(Contract.state == "S",
                                                           Contract.commercial_id == self.current_user.epicuser_id).all()
                if contracts:
                    contract = EventView.prompt_select_contract(contracts)
                    try:
                        data = EventView.prompt_data_event()
                        event = EventBase.create_event(contract, data, session)
                    except KeyboardInterrupt:
                        DataView.display_interupt()
                else:
                    DataView.display_nocontracts()
        else:
            contracts = session.query(Contract).filter_by(state="S").all()
            if contracts:
                contract = EventView.prompt_select_contract(contracts)
                try:
                    data = EventView.prompt_data_event()
                    event = EventBase.create_event(contract, data, session)
                    if EventView.prompt_add_support():
                        EpicTerminalEvent.update_event_support(self, session, event)
                except KeyboardInterrupt:
                    DataView.display_interupt()
            else:
                DataView.display_nocontracts()

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

    @is_authenticated
    @requires_roles('ADM', 'GES', 'SUP', 'COM', 'Admin', 'Gestion', 'Support', 'Commercial')
    def update_event_support(self, session, event):
        """
        Met à jour un événement en permettant de :
        - Sélectionner un support
        - Sélectionner un contrat
        - Sélectionner un événement à mettre à jour
        - Appliquer les modifications dans la base de données.
        """
        try:

            # Récupérer tous les supports
            supports = session.query(EpicUser).filter_by(role='SUP').all()
            supports_dict = {s.username: s.epicuser_id for s in supports}
            support_username = UserView.prompt_select_support(list(supports_dict.keys()))
            support_id = supports_dict[support_username]  # Obtenez l'ID du support sélectionné
            text = f"Support sélectionné: {support_username} (ID: {support_id})"
            console.print(text, style="cyan")

            # Mettre à jour l'événement
            EventBase.update_event(self, event.event_id, {"support_id": support_id})

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            text = f"Erreur rencontrée: {e}"
            console.print(text, style="bold red")
