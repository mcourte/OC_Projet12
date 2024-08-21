from models.entities import EpicUser
from controllers.decorator import is_authenticated, is_admin, is_gestion


class EpicUserBase:
    """
    Classe de base pour la gestion des utilisateurs EpicUser.
    """

    def __init__(self, session):
        """
        Initialise une instance de EpicUserBase avec une session de base de données.

        :param session: Session de base de données utilisée pour interagir avec les utilisateurs.
        """
        self.session = session

    @is_authenticated
    @is_admin
    @is_gestion
    def create_user(self, data):
        """
        Crée un nouvel utilisateur avec les données fournies.

        :param data: Dictionnaire contenant les informations de l'utilisateur, telles que
                     le prénom, le nom, le mot de passe, le rôle, etc.
        :return: L'objet EpicUser créé.
        :raises ValueError: Si le rôle n'est pas valide ou si le nom d'utilisateur existe déjà.
        """
        role = data.get('role')
        if role not in ['Commercial', 'Support', 'Gestion', 'Admin']:
            raise ValueError("Invalid role")
        role_code = self.get_rolecode(role)

        if 'username' not in data or not data['username']:
            data['username'] = EpicUser.generate_unique_username(self.session, data['first_name'], data['last_name'])

        if 'email' not in data or not data['email']:
            data['email'] = EpicUser.generate_unique_email(self.session, data['username'])

        if self.session.query(EpicUser).filter_by(username=data['username']).first():
            raise ValueError("L'username existe déjà")

        user = EpicUser(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['username'],
            email=data['email'],
            role=role_code
        )
        user.set_password(data['password'])
        self.session.add(user)
        self.session.commit()

        return user

    @is_authenticated
    @is_admin
    @is_gestion
    def get_user(self, username):
        """
        Récupère un utilisateur à partir de son nom d'utilisateur.

        :param username: Le nom d'utilisateur de l'utilisateur à récupérer.
        :return: L'objet EpicUser correspondant, ou None si l'utilisateur n'est pas trouvé.
        """
        return self.session.query(EpicUser).filter_by(username=username).first()

    @is_authenticated
    def get_all_users(self):
        """
        Récupère la liste de tous les utilisateurs.

        :return: Une liste d'objets EpicUser représentant tous les utilisateurs.
        """
        return self.session.query(EpicUser).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def update_user(self, name, password=None, role=None, state=None):
        """
        Met à jour les informations d'un utilisateur existant.

        :param name: Le nom d'utilisateur de l'utilisateur à mettre à jour.
        :param password: (Optionnel) Le nouveau mot de passe de l'utilisateur.
        :param role: (Optionnel) Le nouveau rôle de l'utilisateur.
        :param state: (Optionnel) Le nouvel état de l'utilisateur (par exemple, inactif).
        :raises ValueError: Si l'utilisateur n'est pas trouvé.
        """
        user = self.session.query(EpicUser).filter_by(username=name).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")

        if password:
            user.set_password(password)
        if role:
            role_code = self.get_rolecode(role)
            user.role = role_code
        if state:
            if state == 'I' and user.state != 'I':
                user.set_inactive()
            else:
                user.state = state

        self.session.commit()

    def get_roles(self):
        """
        Récupère la liste des rôles disponibles.

        :return: Une liste de chaînes de caractères représentant les rôles.
        """
        return ["Commercial", "Support", "Gestion", "Admin"]

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

    @is_authenticated
    @is_admin
    @is_gestion
    def get_commercials(self):
        """
        Récupère la liste de tous les utilisateurs ayant le rôle de Commercial.

        :return: Une liste d'objets EpicUser représentant les utilisateurs avec le rôle 'Commercial'.
        """
        return self.session.query(EpicUser).filter_by(role='COM').all()

    @is_authenticated
    @is_admin
    @is_gestion
    def get_supports(self):
        """
        Récupère la liste de tous les utilisateurs ayant le rôle de Support.

        :return: Une liste d'objets EpicUser représentant les utilisateurs avec le rôle 'Support'.
        """
        return self.session.query(EpicUser).filter_by(role='SUP').all()

    @is_authenticated
    @is_admin
    @is_gestion
    def get_gestions(self):
        """
        Récupère la liste de tous les utilisateurs ayant le rôle de Gestion.

        :return: Une liste d'objets EpicUser représentant les utilisateurs avec le rôle 'Gestion'.
        """
        return self.session.query(EpicUser).filter_by(role='GES').all()

    @is_authenticated
    @is_admin
    @is_gestion
    def find_by_username(cls, session, username):
        """
        Recherche un utilisateur par son nom d'utilisateur.

        :param session: Session de base de données utilisée pour interagir avec les utilisateurs.
        :param username: Le nom d'utilisateur de l'utilisateur à rechercher.
        :return: L'objet EpicUser correspondant, ou None si l'utilisateur n'est pas trouvé.
        """
        return session.query(cls).filter_by(username=username).first()
