# Import généraux
from sqlalchemy.orm import Session, scoped_session

# Import Modèles
from models.entities import EpicUser

# Import Controllers
from controllers.decorator import is_authenticated, requires_roles, sentry_activate

# Import Views
from views.console_view import console


class EpicUserBase:
    """
    Classe de base pour la gestion des utilisateurs EpicUser.

    Cette classe fournit des méthodes pour créer, mettre à jour et gérer les utilisateurs dans la base de données.
    Elle inclut également des fonctionnalités pour réaffecter les clients,
    contrats et événements lorsque des utilisateurs changent de statut.
    """

    def __init__(self, session, user=None):
        """
        Initialise une instance de EpicUserBase avec une session de base de données.

        :param session: Session de base de données utilisée pour interagir avec les utilisateurs.
        :param user: Instance d'EpicUser, si disponible, représentant l'utilisateur courant.
        """
        self.session = session
        self.user = user

    @staticmethod
    def create_user(session, data_profil):
        """
        Crée un nouvel utilisateur avec les données fournies.

        Paramètres :
        ------------
        session (Session) : La session SQLAlchemy pour interagir avec la base de données.
        data_profil (dict) : Dictionnaire contenant les informations de profil de l'utilisateur, telles que :
                             - first_name : Prénom de l'utilisateur.
                             - last_name : Nom de famille de l'utilisateur.
                             - password : Mot de passe de l'utilisateur.
                             - role : Rôle de l'utilisateur (Gestion, Commercial, Support, Admin).

        Retourne :
        ----------
        EpicUser : L'utilisateur créé.

        Lève :
        ------
        ValueError : Si le rôle est invalide ou si le nom d'utilisateur existe déjà.
        """
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
            raise ValueError("Code de rôle invalide")

        username = EpicUser.generate_unique_username(session, data_profil['first_name'], data_profil['last_name'])
        username_dict = {'username': username}
        data_profil.update(username_dict)
        email = EpicUser.generate_unique_email(session, data_profil['username'])

        if session.query(EpicUser).filter_by(username=username).first():
            raise ValueError("Le nom d'utilisateur existe déjà")

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

        Paramètres :
        ------------
        session (Session) : La session SQLAlchemy pour interagir avec la base de données.
        name (str) : Nom d'utilisateur de l'utilisateur à mettre à jour.
        password (str, optionnel) : Nouveau mot de passe de l'utilisateur.
        role (str, optionnel) : Nouveau rôle de l'utilisateur.
        state (str, optionnel) : Nouveau statut de l'utilisateur.

        Lève :
        ------
        ValueError : Si la session n'est pas valide, si le nom d'utilisateur n'est pas une chaîne,
        ou si l'utilisateur n'est pas trouvé.
        """
        # Vérifiez que session est bien une instance de SQLAlchemy Session
        if not isinstance(session, Session):
            raise ValueError("La session passée n'est pas une instance de SQLAlchemy Session.")

        # Vérifiez que name est une chaîne de caractères
        if not isinstance(name, str):
            raise ValueError("Le nom d'utilisateur doit être une chaîne de caractères.")

        # Requête pour trouver l'utilisateur
        user = session.query(EpicUser).filter_by(username=name).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")

        # Mise à jour des informations utilisateur
        if password:
            user.set_password(password)

        session.commit()

    @staticmethod
    def get_roles():
        """
        Récupère la liste des rôles disponibles.

        :return: Une liste de chaînes de caractères représentant les rôles.
        """
        return ["Commercial", "Support", "Gestion", "Admin"]

    @staticmethod
    def get_rolecode(role_name):
        """
        Récupère le code associé à un rôle donné.

        Paramètres :
        ------------
        role_name (str) : Le nom du rôle.

        Retourne :
        ----------
        str ou None : Le code du rôle correspondant, ou None si le rôle n'est pas trouvé.
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
            # Vérifiez que session est une instance de SQLAlchemy Session ou scoped_session
            if not isinstance(session, (Session, scoped_session)):
                print(f"Erreur  Type trouvé : {type(session)}")
                return

            user = session.query(EpicUser).filter_by(username=username).first()

            if not user:
                print(f"Utilisateur avec le nom {username} non trouvé.")
                return

            print(f"Le statut actuel de {username} est {user.state}")

            if user.state == 'A':
                user.state = 'I'
                print(f"{user.username} est Inactif")

                if user.role == 'COM':
                    self.notify_gestion_to_reassign_user(user)
                    self.reassign_customers(session)
                elif user.role == 'GES':
                    self.notify_gestion_to_reassign_user(user)
                    self.reassign_contracts(session)
                elif user.role == 'SUP':
                    self.notify_gestion_to_reassign_user(user)
                    self.reassign_events(session)
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

        Paramètres :
        ------------
        session (Session) : La session SQLAlchemy pour interagir avec la base de données.
        """
        try:
            # Sélection d'un nouveau commercial actif pour les réaffectations
            new_commercial = session.query(EpicUser).filter_by(role='COM', state='A').first()

            if not new_commercial:
                text = "Aucun commercial actif trouvé pour la réaffectation."
                console.print(text, style="bold")
                return

            # Réaffectation des clients
            if not hasattr(self, 'customers'):
                text = "Erreur: L'objet ne contient pas d'attribut 'customers'."
                console.print(text, style="bold red")
                return

            for customer in self.customers:
                customer.commercial_id = new_commercial.epicuser_id

            session.commit()
            self.notify_gestion("Réaffectation des clients du commercial inactif terminée.")

        except Exception as e:
            text = f"Erreur inattendue lors de la réaffectation des clients: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_contracts(self, session):
        """
        Réaffecte les contrats d'un gestionnaire inactif à un autre gestionnaire.

        Paramètres :
        ------------
        session (Session) : La session SQLAlchemy pour interagir avec la base de données.
        """
        try:
            # Vérification que la session est une instance de SQLAlchemy Session
            if not isinstance(session, (Session, scoped_session)):
                text = "Erreur: l'objet session n'est pas une instance SQLAlchemy Session."
                console.print(text, style="bold red")
                return

            # Sélection du nouveau gestionnaire actif pour les réaffectations
            new_gestion = session.query(EpicUser).filter_by(role='SUP', state='A').first()

            if not new_gestion:
                text = "Aucun gestionnaire actif trouvé pour la réaffectation."
                console.print(text, style="bold")
                return

            # Réaffectation des contrats
            if not hasattr(self, 'contracts'):
                text = "Erreur: L'objet ne contient pas d'attribut 'contracts'."
                console.print(text, style="bold red")
                return

            for contract in self.contracts:
                contract.gestion_id = new_gestion.epicuser_id

            session.commit()
            self.notify_gestion("Réaffectation des contrats du gestionnaire inactif terminée.")

        except Exception as e:
            text = f"Erreur inattendue lors de la réaffectation des contrats: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def notify_gestion_to_reassign_user(self, user):
        """
        Notifie le gestionnaire pour réaffecter les clients, contrats ou événements d'un utilisateur inactif.

        Paramètres :
        ------------
        user (EpicUser) : Instance de l'utilisateur à réaffecter.
        """
        try:
            # Vérifier si l'utilisateur est passé en paramètre
            if not user:
                text = "Aucun utilisateur sélectionné pour la notification de réaffectation."
                console.print(text, style="bold red")
                return

            message = f"L'utilisateur {user.username} est inactif. Veuillez réaffecter ses clients/contrats/événements."
            self.notify_gestion(message)

        except Exception as e:
            text = f"Erreur inattendue lors de la notification du gestionnaire: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def notify_gestion(self, message):
        """
        Envoie un message au gestionnaire pour des actions manuelles.

        Paramètres :
        ------------
        message (str) : Message à envoyer au gestionnaire.
        """
        # Implémentation de l'envoi du message (par email, notification système, etc.)
        text = f"Notification pour le gestionnaire: {message}"
        console.print(text, style="bold green")

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
