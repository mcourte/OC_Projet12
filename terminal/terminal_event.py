import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.decorator import (is_authenticated, requires_roles, sentry_activate)
from controllers.event_controller import EventBase, Event
from controllers.user_controller import EpicUser
from controllers.customer_controller import Customer
from controllers.contract_controller import Contract
from views.event_view import EventView
from views.data_view import DataView
from views.customer_view import CustomerView
from views.console_view import console
from terminal.terminal_user import EpicTerminalUser
from terminal.terminal_customer import EpicTerminalCustomer
from views.contract_view import ContractView
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
            print(f"Nombre d'événements trouvés: {len(events)}")
            if events:
                event = EventView.prompt_select_event(events)
                event_id = event.event_id  # Assurez-vous d'utiliser l'I

                # Récupérer tous les supports
                supports = session.query(EpicUser).filter_by(role='SUP').all()
                supports_dict = {s.username: s.epicuser_id for s in supports}
                support_username = UserView.prompt_select_support(list(supports_dict.keys()))
                support_id = supports_dict[support_username]  # Obtenez l'ID du support sélectionné
                print(f"Support sélectionné: {support_username} (ID: {support_id})")

                # Mettre à jour l'événement
                EventBase.update_event(self, event_id, {"support_id": support_id})

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            print(f"Erreur rencontrée: {e}")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'COM', 'Admin', 'Commercial')
    def create_event(self, session):
        """
        Crée un nouvel événement en permettant de :
        - Sélectionner un contrat
        - Saisir les données de l'événement
        - Ajouter l'événement à la base de données
        - Générer un workflow pour le nouvel événement.
        """
        contracts = session.query(Contract).all()
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
    def list_of_events_filtered(self, session):
        """
        Affiche la liste des événements en permettant de :
        - Choisir un commercial (facultatif)
        - Choisir un client (facultatif)
        - Sélectionner un contrat (si confirmé)
        - Sélectionner un support (si confirmé)
        - Lire la base de données et afficher les événements.
        """
        try:
            # Choisir un commercial (facultatif)
            commercials = session.query(EpicUser).filter_by(role='COM').all()
            commercial = UserView.prompt_select_commercial(commercials)
            if commercial:
                # Si un commercial est sélectionné, choisir un client
                if CustomerView.prompt_confirm_customer():
                    customers = session.query(Customer).filter_by(commercial_id=commercial.epicuser_id).all()
                    selected_customer = CustomerView.prompt_customers(customers)
                    text = (f'Client sélectionné : {selected_customer}')
                    console.print(text, justify="cente", style="bold blue")
                    # Initialiser les filtres
                    filter_by_client = selected_customer.customer_id
                else:
                    filter_by_client = None
            else:
                # Si aucun commercial n'est sélectionné, afficher tous les événements
                filter_by_client = None

            filter_by_contract = None
            filter_by_support = None

            # Sélectionner un contrat si confirmé
            if filter_by_client and ContractView.prompt_confirm_contract():
                contracts = session.query(Contract).filter_by(customer_id=filter_by_client).all()
                text = (f'Contrats disponibles : {contracts}')
                console.print(text, justify="cente", style="bold blue")
                contracts_data = [{"Description": f"{c.description}", "ID": c.contract_id} for c in contracts]
                contract_ref = EventView.prompt_select_contract(contracts_data)
                filter_by_contract = contract_ref['ID'] if contract_ref else None

            # Sélectionner un support si confirmé
            if UserView.prompt_confirm_support():
                supports = session.query(EpicUser).filter_by(role='SUP').all()
                supports_name = [c.username for c in supports]
                supports_name.append(EventView.no_support())
                sname = UserView.prompt_select_support(supports_name)
                text = (f'Support sélectionné : {sname}')
                console.print(text, justify="cente", style="bold blue")
                if sname != EventView.no_support():
                    support = session.query(EpicUser).filter_by(username=sname).first()
                    if support:
                        filter_by_support = support.epicuser_id
                    else:
                        print('Support non trouvé.')

            # Construire la requête de filtrage des événements
            query = session.query(Event)
            if filter_by_client:
                query = query.filter_by(customer_id=filter_by_client)
            if filter_by_contract:
                query = query.filter_by(contract_id=filter_by_contract)
            if filter_by_support:
                query = query.filter_by(support_id=filter_by_support)
            else:
                query = query

            # Exécuter la requête et afficher les résultats
            events = query.all()
            EventView.display_list_events(events)

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            print(f"Erreur rencontrée : {e}")

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
        events = session.query(Event).all()
        EventView.display_list_events(events)

    @is_authenticated
    @requires_roles('ADM', 'GES', 'SUP', 'Admin', 'Gestion', 'Support')
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
            print(f"Support sélectionné: {support_username} (ID: {support_id})")

            # Mettre à jour l'événement
            EventBase.update_event(self, event.event_id, {"support_id": support_id})

        except KeyboardInterrupt:
            DataView.display_interupt()
        except Exception as e:
            print(f"Erreur rencontrée: {e}")
