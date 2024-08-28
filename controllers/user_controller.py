from models.entities import EpicUser, Contract
from controllers.decorator import is_authenticated, requires_roles, sentry_activate
import logging
from sqlalchemy.orm import object_session
# Obtenez le logger configuré
logger = logging.getLogger(__name__)


class EpicUserBase:
    """
    Classe de base pour la gestion des utilisateurs EpicUser.
    """

    def __init__(self, session, user=None):
        """
        Initialise une instance de EpicUserBase avec une session de base de données.

        :param session: Session de base de données utilisée pour interagir avec les utilisateurs.
        """
        self.session = session
        self.user = user

    @staticmethod
    def create_user(session, data_profil):
        role_name = data_profil.get('role')
        if role_name == 'Gestion':
            role_code = 'GES'
        elif role_name == 'Commercial':
            role_code = 'COM'
        elif role_name == 'Support':
            role_code = 'SUP'
        elif role_name == 'Admin':
            role_code = 'ADM'
        else:
            raise ValueError("Invalid role code")
        username = EpicUser.generate_unique_username(session, data_profil['first_name'], data_profil['last_name'])
        username_dict = {'username': username}
        data_profil.update(username_dict)
        print(data_profil)
        email = EpicUser.generate_unique_email(session, data_profil['username'])

        if session.query(EpicUser).filter_by(username=username).first():
            raise ValueError("L'username existe déjà")

        user = EpicUser(
            first_name=data_profil['first_name'],
            last_name=data_profil['last_name'],
            username=username,
            email=email,
            role=role_code
        )
        user.set_password(data_profil['password'])
        session.add(user)
        session.commit()

        return user

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def update_user(self, session, name, password=None, role=None, state=None):
        """
        Met à jour les informations d'un utilisateur existant.

        :param name: Le nom d'utilisateur de l'utilisateur à mettre à jour.
        :param password: (Optionnel) Le nouveau mot de passe de l'utilisateur.
        :param role: (Optionnel) Le nouveau rôle de l'utilisateur.
        :param state: (Optionnel) Le nouvel état de l'utilisateur (par exemple, inactif).
        :raises ValueError: Si l'utilisateur n'est pas trouvé.
        """
        user = session.query(EpicUser).filter_by(username=name).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")

        if password:
            user.set_password(password)
        if role:
            role_code = user.get('role')
            user.role = role_code
        if state:
            if state == 'I' and user.state != 'I':
                user.set_inactive()
            else:
                user.state = state

        session.commit()

    @staticmethod
    def get_roles(self):
        """
        Récupère la liste des rôles disponibles.

        :return: Une liste de chaînes de caractères représentant les rôles.
        """
        return ["Commercial", "Support", "Gestion", "Admin"]

    @staticmethod
    def get_rolecode(self, role_name):
        """
        Récupère le code associé à un rôle donné.

        :param role_name: Le nom du rôle.
        :return: Le code du rôle correspondant, ou None si le rôle n'est pas trouvé.
        """
        role_map = {
            "Commercial": "COM",
            "Support": "SUP",
            "Gestion": "GES",
            "Admin": "ADM"
        }
        return role_map.get(role_name)

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def set_activate_inactivate(self, session, username):
        """
        Définit l'utilisateur comme inactif et déclenche les réaffectations ou notifications nécessaires.
        """
        user = session.query(EpicUser).filter_by(username=username).first()

        print(f"Le statut actuel de {username} est {user.state}")
        if user is not None and user.state == 'A':
            user.state = 'I'
            print(f"{user.username} est Inactife")
            session.commit()
            if user.role == 'COM':
                self.notify_gestion_to_reassign_user(user)
                self.reassign_customers()
            elif user.role == 'GES':
                self.notify_gestion_to_reassign_user(user)
                self.reassign_contracts(session)
            elif user.role == 'SUP':
                self.notify_gestion_to_reassign_user(user)
                self.reassign_events()
        elif user is not None and user.state == 'I':
            user.state = 'A'
            print(f"{user.username} est de nouveau Actif")
            session.commit()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_customers(self):
        """Réaffecte les clients du commercial inactif à un autre commercial."""
        new_commercial = self.find_alternate_commercial()
        for customer in self.customers:
            customer.commercial_id = new_commercial.epicuser_id
        session = object_session(self)
        session.commit()

        # Envoyer une notification au gestionnaire
        self.notify_gestion("Réaffectation des clients du commercial inactif terminée.")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_contracts(self, session):
        """Réaffecte les contrats d'un gestionnaire inactif à un autre gestionnaire."""
        new_gestion = session.query(EpicUser).filter_by(role='SUP', state='A').first()
        print(new_gestion)
        contracts = session.query(Contract).filter_by(role='SUP', state='A').first()
        for contract in self.contracts:
            contract.gestion_id = new_gestion.epicuser_id
        session = object_session(self)
        session.commit()

        # Envoyer une notification au gestionnaire
        self.notify_gestion("Réaffectation des contrats du gestionnaire inactif terminée.")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_events(self):
        """Réaffecte les contrats d'un support inactif à un autre support."""
        new_support = self.find_alternate_support()
        for event in self.events:
            event.support_id = new_support.epicuser_id
        session = object_session(self)
        session.commit()

        # Envoyer une notification au gestionnaire
        self.notify_gestion("Réaffectation des évènements du support inactif terminée.")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def notify_gestion_to_reassign_user(self, user):
        """Notifier le gestionnaire pour réaffecter les événements du support inactif."""
        if user:  # Vérifier si l'utilisateur est passé en paramètre
            print(user)
            message = f"L'utilisateur {user.username} est inactif. Veuillez réaffecter ses clients/contrats/événements."
            self.notify_gestion(message)
        else:
            print("Aucun utilisateur sélectionné pour la notification de réaffectation.")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def find_alternate_commercial(self):
        """Trouver un autre commercial pour réaffecter les clients."""
        session = object_session(self)
        return session.query(EpicUser).filter_by(role='COM', state='A').first()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def find_alternate_gestion(self):
        """Trouver un autre gestionnaire pour réaffecter les contrats."""
        session = object_session(self)
        return session.query(EpicUser).filter_by(role='GES', state='A').first()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def find_alternate_support(self):
        """Trouver un autre support pour réaffecter les évènements."""
        session = object_session(self)
        return session.query(EpicUser).filter_by(role='SUP', state='A').first()

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def notify_gestion(self, message):
        """Envoyer un message au gestionnaire pour des actions manuelles."""
        # Implémentation de l'envoi du message (par email, notification système, etc.)
        print(f"Notification pour le gestionnaire: {message}")
