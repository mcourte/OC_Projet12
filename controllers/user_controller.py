# Import généraux
from sqlalchemy.orm import Session, scoped_session

# Import Modèles
from models.entities import EpicUser, Contract, Event, Customer

# Import Controllers
from controllers.decorator import is_authenticated, requires_roles, sentry_activate

# Import Views
from views.console_view import console
from views.user_view import UserView


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

    def get_user_info(self):
        if self.user:
            return self.user
        return None

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
    def get_roles(self):
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


    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def set_activate_inactivate(self, session, username):
        """
        Définit l'utilisateur comme actif ou inactif et déclenche les réaffectations ou notifications nécessaires.

        :param session: SQLAlchemy session instance
        :param username: Nom d'utilisateur à activer ou désactiver
        """
        # Vérifiez que session est une instance de SQLAlchemy Session ou scoped_session
        if not isinstance(session, (Session, scoped_session)):
            print(f"Erreur : Type trouvé : {type(session)}")
            return
        print(f"Type de session reçu : {type(session)}")
        user = session.query(EpicUser).filter_by(username=username).first()

        if not user:
            print(f"Utilisateur avec le nom {username} non trouvé.")
            return

        print(f"Le statut actuel de {username} est {user.state}")
        
        if user.state == 'A':
            user.state = 'I'
            text = f"{user.username} est Inactif.Veuillez réaffecter les Contrats/Clients/Evènement qui lui sont associés"
            console.print(text)
            if user.role == 'COM':
                print(f"réaffectation rôle {user.role}")
                self.reassign_customers(session, user)
            elif user.role == 'GES':
                print(f"réaffectation rôle {user.role}")
                self.reassign_contracts(session, user)
            elif user.role == 'SUP':
                print(f"réaffectation rôle {user.role}")
                self.reassign_events(session, user)
            session.commit()

        elif user.state == 'I':
            user.state = 'A'
            print(f"{user.username} est de nouveau Actif")
            session.commit()


    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_customers(self, session, user):
        """
        Réaffecte les clients d'un commercial inactif à un autre commercial.

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

            # Sélection du nouveau commercial actif pour les réaffectations
            new_commercial = session.query(EpicUser).filter_by(role='COM', state='A').all()

            # Assurez-vous que prompt_user retourne un utilisateur valide
            choice = UserView.prompt_user([g.username for g in new_commercial])  # assuming prompt_user returns the username
            if choice == user.username:
                texte = f"Erreur: L'utilisateur sélectionné '{choice}' est l'utilisateur que vous souhaitez "
                texte_l2 = "supprimer/rendre inactif. Veuillez sélectionner un autre utilisateur."
                text = texte + texte_l2
                console.print(text, style="bold red")
                return  # Vous pouvez également lever une exception ou afficher un message d'erreur
            if not choice:
                text = "Aucun commercial actif trouvé pour la réaffectation."
                console.print(text, style="bold")
                return

            # Obtenez l'objet EpicUser correspondant au choix
            chosen_user = session.query(EpicUser).filter_by(username=choice).first()
            if not chosen_user:
                text = "Le commercial sélectionné pour la réaffectation n'existe pas."
                console.print(text, style="bold red")
                return

            customers = session.query(Customer).filter_by(commercial_id=user.epicuser_id).all()
            for customer in customers:
                customer.commercial_id = chosen_user.epicuser_id
            session.commit()
            text = "Réaffectation des clients du commercial inactif terminée."
            console.print(text, style="bold green")

        except Exception as e:
            text = f"Erreur inattendue lors de la réaffectation des clients: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_contracts(self, session, user):
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
            new_gestion = session.query(EpicUser).filter_by(role='GES', state='A').all()

            # Assurez-vous que prompt_user retourne un utilisateur valide
            choice = UserView.prompt_user([g.username for g in new_gestion])  # assuming prompt_user returns the username
            if choice == user.username:
                texte = f"Erreur: L'utilisateur sélectionné '{choice}' est l'utilisateur que vous souhaitez "
                texte_l2 = "supprimer/rendre inactif. Veuillez sélectionner un autre utilisateur."
                text = texte + texte_l2
                console.print(text, style="bold red")
            if not choice:
                text = "Aucun gestionnaire actif trouvé pour la réaffectation."
                console.print(text, style="bold")
                return

            # Obtenez l'objet EpicUser correspondant au choix
            chosen_user = session.query(EpicUser).filter_by(username=choice).first()
            if not chosen_user:
                text = "Le gestionnaire sélectionné pour la réaffectation n'existe pas."
                console.print(text, style="bold red")
                return

            contracts = session.query(Contract).filter_by(commercial_id=user.epicuser_id).all()
            for contract in contracts:
                contract.gestion_id = chosen_user.epicuser_id

            session.commit()
            text = "Réaffectation des contrats du gestionnaire inactif terminée."
            console.print(text)

        except Exception as e:
            text = f"Erreur inattendue lors de la réaffectation des contrats: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def reassign_events(self, session, user):
        """
        Réaffecte les événements d'un support inactif à un autre support.

        :param session: SQLAlchemy session instance
        """
        try:
            # Sélection d'un nouveau support actif pour les réaffectations
            new_support = session.query(EpicUser).filter_by(role='SUP', state='A').all()
            choice = UserView.prompt_user([g.username for g in new_support])  # assuming prompt_user returns the username
            if choice == user.username:
                texte = f"Erreur: L'utilisateur sélectionné '{choice}' est l'utilisateur que vous souhaitez "
                texte_l2 = "supprimer/rendre inactif. Veuillez sélectionner un autre utilisateur."
                text = texte + texte_l2
                console.print(text, style="bold red")
            if not choice:
                text = "Aucun support actif trouvé pour la réaffectation."
                console.print(text, style="bold")
                return

            # Obtenez l'objet EpicUser correspondant au choix
            choosen_user = session.query(EpicUser).filter_by(username=choice).first()
            if not choosen_user:
                text = "Le support sélectionné pour la réaffectation n'existe pas."
                console.print(text, style="bold red")
                return

            events = session.query(Event).filter_by(support_id=user.epicuser_id).all()
            for event in events:
                event.support_id = choosen_user.epicuser_id

            session.commit()
            text = "Réaffectation des évènements du gestionnaire inactif terminée."
            console.print(text)

        except Exception as e:
            text = f"Erreur inattendue lors de la réaffectation des événements: {e}"
            console.print(text, style="bold red")

    @sentry_activate
    @is_authenticated
    @requires_roles('ADM', 'GES', 'Admin', 'Gestion')
    def delete_user(self, session, choosen_user):
        """
        Supprime un utilisateur de la base de données.

        Paramètres :
        ------------
        choosen_user : str
            Le nom d'utilisateur de l'utilisateur à supprimer.
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        bool : True si la suppression a réussi, False sinon.
        """
        try:
            # Vérifiez que session est une instance de SQLAlchemy Session ou scoped_session
            if not isinstance(session, (Session, scoped_session)):
                print(f"Erreur : Type trouvé : {type(session)}")
                return False
            print(f"Type de session reçu : {type(session)}")

            user = session.query(EpicUser).filter_by(username=choosen_user).first()

            if not user:
                print(f"Utilisateur avec le nom {choosen_user} non trouvé.")
                return False

            text = f"L'utilisateur : {user.username} va être supprimé de la base de donnée."
            text_l2 = "Veuillez réaffecter les Contrats/Clients/Evènement qui lui sont associés"
            message = text + text_l2
            console.print(message, style="bold red")
            if UserView.prompt_delete_user():

                if user.role.code == 'COM':
                    self.reassign_customers(session, user)
                elif user.role.code == 'GES':
                    self.reassign_contracts(session, user)
                elif user.role.code == 'SUP':
                    self.reassign_events(session, user)

                # Suppression de l'utilisateur
                session.delete(user)

                # Validation de la transaction
                session.commit()
                text = f"L'utilisateur '{user.username}' (ID {user.epicuser_id}) a été supprimé avec succès."
                console.print(text, style="bold green")
                return True
        except Exception as e:
            # Annulation de la transaction en cas d'erreur
            if isinstance(session, Session):  # Vérification supplémentaire
                session.rollback()
            print(f"Erreur lors de la suppression de l'utilisateur '{choosen_user}': {e}")
            return False
