from models.entities import EpicUser
from controllers.decorator import is_authenticated, is_admin, is_gestion


class EpicUserBase:
    def __init__(self, session):
        self.session = session

    @is_authenticated
    @is_admin
    @is_gestion
    def create_user(self, data):
        """Permet de créer un Utilisateur
        Informations à fournir : Nom, Prénom, Mot de passe"""
        if data['role'] not in ['Commercial', 'Support', 'Gestion', 'Admin']:
            raise ValueError("Invalid role")
        role_code = self.get_rolecode(data['role'])

        # Générer un nom d'utilisateur unique
        if 'username' not in data or not data['username']:
            data['username'] = EpicUser.generate_unique_username(self.session, data['first_name'], data['last_name'])

        # Générer un email unique
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
        return user  # Assurez-vous que ceci retourne bien un objet EpicUser

    @is_authenticated
    @is_admin
    @is_gestion
    def get_user(self, username):
        """Permet de retrouver un Utilisateur via son username"""
        return self.session.query(EpicUser).filter_by(username=username).first()

    @is_authenticated
    def get_all_users(self):
        """Permet de retourner la liste de tous les utilisateurs"""
        return self.session.query(EpicUser).all()

    @is_authenticated
    @is_admin
    @is_gestion
    def update_user(self, name, password=None, role=None, state=None):
        """Permet de mettre à jour un utilisateur, y compris pour le marquer comme inactif."""
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
        return ["Commercial", "Support", "Gestion", "Admin"]

    def get_rolecode(self, role_name):
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
        """Permet de lister tous les utilisateurs avec le rôle de Commercial"""
        return self.session.query(EpicUser).filter_by(role='COM').all()

    @is_authenticated
    @is_admin
    @is_gestion
    def get_supports(self):
        """Permet de lister tous les utilisateurs avec le rôle de Support"""
        return self.session.query(EpicUser).filter_by(role='SUP').all()

    @is_authenticated
    @is_admin
    @is_gestion
    def get_gestions(self):
        """Permet de lister tous les utilisateurs avec le rôle de Gestion"""
        return self.session.query(EpicUser).filter_by(role='GES').all()
