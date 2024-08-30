from models.entities import EpicUser
from controllers.decorator import is_authenticated, requires_roles, sentry_activate
import logging
import sqlalchemy.orm
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
        """

        # Vérifiez que session est bien une instance de SQLAlchemy Session
        if not isinstance(session, sqlalchemy.orm.Session):
            raise ValueError("La session passée n'est pas une instance de SQLAlchemy Session.")

        # Vérifiez que name est une chaîne de caractères
        if not isinstance(name, str):
            raise ValueError("Le nom d'utilisateur doit être une chaîne de caractères.")

        print(f"session: {session}")
        print(f"type session: {type(session)}")

        # Requête pour trouver l'utilisateur
        user = session.query(EpicUser).filter_by(username=name).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")

        # Mise à jour des informations utilisateur
        if password:
            user.set_password(password)

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
        Définit l'utilisateur comme actif ou inactif et déclenche les réaffectations ou notifications nécessaires.

        :param session: SQLAlchemy session instance
        :param username: Nom d'utilisateur à activer ou désactiver
        """
        try:
            # Vérification que la session est une instance de SQLAlchemy Session
            if not isinstance(session, sqlalchemy.orm.session):
                print("Erreur: l'objet session n'est pas une instance SQLAlchemy Session.")
                return

            user = session.query(EpicUser).filter_by(username=username).first()

            # Vérification que l'utilisateur existe
            if not user:
                print(f"Utilisateur avec le nom {username} non trouvé.")
                return

            print(f"Le statut actuel de {username} est {user.state}")

            # Vérification et changement de l'état de l'utilisateur
            if user.state == 'A':
                user.state = 'I'
                print(f"{user.username} est Inactif")

                # Gestion des réaffectations et notifications basées sur le rôle de l'utilisateur
                if user.role == 'COM':
                    self.notify_gestion_to_reassign_user(user)
                    self.reassign_customers(session)  # Ajout de la session comme argument
                elif user.role == 'GES':
                    self.notify_gestion_to_reassign_user(user)
                    self.reassign_contracts(session)
                elif user.role == 'SUP':
                    self.notify_gestion_to_reassign_user(user)
                    self.reassign_events(session)  # Ajout de la session comme argument
                session.commit()

            elif user.state == 'I':
                user.state = 'A'
                print(f"{user.username} est de nouveau Actif")
                session.commit()

        except Exception as e:
            print(f"Erreur inattendue lors de la mise à jour de l'utilisateur: {e}")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_customers(self, session):
        """
        Réaffecte les clients d'un commercial inactif à un autre commercial.

        :param session: SQLAlchemy session instance
        """
        try:
            # Sélection d'un nouveau commercial actif pour les réaffectations
            new_commercial = session.query(EpicUser).filter_by(role='COM', state='A').first()

            if not new_commercial:
                print("Aucun commercial actif trouvé pour la réaffectation.")
                return

            # Réaffectation des clients
            if not hasattr(self, 'customers'):
                print("Erreur: L'objet ne contient pas d'attribut 'customers'.")
                return

            for customer in self.customers:
                customer.commercial_id = new_commercial.epicuser_id

            session.commit()
            self.notify_gestion("Réaffectation des clients du commercial inactif terminée.")

        except Exception as e:
            print(f"Erreur inattendue lors de la réaffectation des clients: {e}")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_contracts(self, session):
        """
        Réaffecte les contrats d'un gestionnaire inactif à un autre gestionnaire.

        :param session: SQLAlchemy session instance
        """
        try:
            # Vérification que la session est une instance de SQLAlchemy Session
            if not isinstance(session, sqlalchemy.orm.session):
                print("Erreur: l'objet session n'est pas une instance SQLAlchemy Session.")
                return

            # Sélection du nouveau gestionnaire actif pour les réaffectations
            new_gestion = session.query(EpicUser).filter_by(role='SUP', state='A').first()

            if not new_gestion:
                print("Aucun gestionnaire actif trouvé pour la réaffectation.")
                return

            # Réaffectation des contrats
            if not hasattr(self, 'contracts'):
                print("Erreur: L'objet ne contient pas d'attribut 'contracts'.")
                return

            for contract in self.contracts:
                contract.gestion_id = new_gestion.epicuser_id

            session.commit()
            self.notify_gestion("Réaffectation des contrats du gestionnaire inactif terminée.")

        except Exception as e:
            print(f"Erreur inattendue lors de la réaffectation des contrats: {e}")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_events(self, session):
        """
        Réaffecte les événements d'un support inactif à un autre support.

        :param session: SQLAlchemy session instance
        """
        try:
            # Sélection d'un nouveau support actif pour les réaffectations
            new_support = session.query(EpicUser).filter_by(role='SUP', state='A').first()

            if not new_support:
                print("Aucun support actif trouvé pour la réaffectation.")
                return

            # Réaffectation des événements
            if not hasattr(self, 'events'):
                print("Erreur: L'objet ne contient pas d'attribut 'events'.")
                return

            for event in self.events:
                event.support_id = new_support.epicuser_id

            session.commit()
            self.notify_gestion("Réaffectation des événements du support inactif terminée.")

        except Exception as e:
            print(f"Erreur inattendue lors de la réaffectation des événements: {e}")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def notify_gestion_to_reassign_user(self, user):
        """
        Notifier le gestionnaire pour réaffecter les événements du support inactif.

        :param user: Instance de l'utilisateur à réaffecter
        """
        try:
            # Vérifier si l'utilisateur est passé en paramètre
            if not user:
                print("Aucun utilisateur sélectionné pour la notification de réaffectation.")
                return

            print(user)
            message = f"L'utilisateur {user.username} est inactif. Veuillez réaffecter ses clients/contrats/événements."
            self.notify_gestion(message)

        except Exception as e:
            print(f"Erreur inattendue lors de la notification du gestionnaire: {e}")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def notify_gestion(self, message):
        """Envoyer un message au gestionnaire pour des actions manuelles."""
        # Implémentation de l'envoi du message (par email, notification système, etc.)
        print(f"Notification pour le gestionnaire: {message}")
