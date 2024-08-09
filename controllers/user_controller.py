from models.entities import EpicUser


class EpicUserBase:
    def __init__(self, session):
        self.session = session

    def create_user(self, data):
        if data['role'] not in ['Commercial', 'Support', 'Gestion', 'Admin']:
            raise ValueError("Invalid role")
        role_code = self.get_rolecode(data['role'])
        if self.session.query(EpicUser).filter_by(username=data['username']).first():
            raise ValueError("Username already exists")
        user = EpicUser(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        user.role = role_code
        self.session.add(user)
        self.session.commit()

    def get_user(self, username):
        return self.session.query(EpicUser).filter_by(username=username).first()

    def get_employees(self):
        return self.session.query(EpicUser).all()

    def update_user(self, name, password=None, role=None):
        user = self.session.query(EpicUser).filter_by(username=name).first()
        if not user:
            raise ValueError("User not found")
        if password:
            user.set_password(password)
        if role:
            role_code = self.get_rolecode(role)
            user.role = role_code
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

    def get_commercials(self):
        return self.session.query(EpicUser).filter_by(role='COM').all()

    def get_supports(self):
        return self.session.query(EpicUser).filter_by(role='SUP').all()

    def get_gestions(self):
        return self.session.query(EpicUser).filter_by(role='GES').all()
