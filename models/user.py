from sqlalchemy import Column, Integer, String, Sequence
import bcrypt
from .base import Base


class User(Base):
    __tablename__ = 'users'

    # Définition des rôles en tant que constantes
    ROLE_COM = 'com'
    ROLE_GES = 'ges'
    ROLE_SUP = 'sup'

    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    role = Column(String(10), nullable=False)
    hashed_password = Column(String(60), nullable=False)

    @classmethod
    def generate_unique_username(cls, session, first_name, last_name):
        base_username = f"{first_name}.{last_name}".lower()
        username = base_username
        index = 0
        while session.query(cls).filter_by(username=username).first():
            username = f"{base_username}{index}"
            index += 1
        return username

    @staticmethod
    def get_all_roles():
        return [User.ROLE_COM, User.ROLE_GES, User.ROLE_SUP]

    def set_password(self, plain_password):
        """Hache le mot de passe et le stocke."""
        self.hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, plain_password):
        """Vérifie que le mot de passe fourni correspond au mot de passe haché."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.hashed_password.encode('utf-8'))
