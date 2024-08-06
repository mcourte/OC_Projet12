from sqlalchemy import Column, Integer, String, Sequence, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from enum import Enum
from argon2 import PasswordHasher
import argon2
from constantes import ROLE_ADM, ROLE_COM, ROLE_GES, ROLE_SUP
from config import Base


# Définition des rôles en tant qu'énumération
class Role(Enum):
    COM = ROLE_COM
    GES = ROLE_GES
    SUP = ROLE_SUP
    ADM = ROLE_ADM


class User(Base):
    """Définition de la classe User qui sera la table dans la BD"""
    __tablename__ = 'users'

    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(SQLAlchemyEnum(Role), nullable=False, index=True)
    password = Column(String(60), nullable=False)
    email = Column(String(254), unique=True, nullable=False)

    com_contracts = relationship('Contract', foreign_keys='Contract.com_contact_id', back_populates='com_contact')
    ges_contracts = relationship('Contract', foreign_keys='Contract.ges_contact_id', back_populates='ges_contact')
    ges_events = relationship('Event', foreign_keys='Event.ges_contact_id', back_populates='ges_contact')
    sup_events = relationship('Event', foreign_keys='Event.sup_contact_id', back_populates='sup_contact')

    def __init__(self, first_name, last_name, username, role, password, email):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.role = role
        self.password = password
        self.email = email

    @classmethod
    def generate_unique_username(cls, session, first_name, last_name):
        """Vérifie que l'username n'existe pas sinon ajoute un index (à partir de 1) à la suite"""
        username = f"{first_name[0].lower()}{last_name.lower()}"
        counter = 1

        while session.query(cls).filter_by(username=username).first():
            username = f"{username}{counter}"
            counter += 1
        return username

    @classmethod
    def generate_unique_email(cls, session, username):
        """Vérifie que l'email n'existe pas sinon ajoute un index (à partir de 1) à la suite"""
        base_email = f"{username}@epic.com"
        email = base_email
        counter = 1

        # Vérifie l'existence de l'email
        while session.query(cls).filter_by(email=email).first():
            email = f"{username}{counter}@epic.com"
            counter += 1
        return email

    def set_password(self, password):
        ph = PasswordHasher()
        self.password = ph.hash(password)

    def check_password(self, verification_password):
        ph = PasswordHasher()
        try:
            return ph.verify(self.password, verification_password)
        except argon2.exceptions.VerifyMismatchError:
            return False
