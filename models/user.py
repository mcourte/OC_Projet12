from sqlalchemy import Column, Integer, String, Sequence, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from enum import Enum
import argon2
from constantes import ROLE_ADM, ROLE_COM, ROLE_GES, ROLE_SUP
from .base import Base


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

    # Relations entre les différents modèles
    com_contracts = relationship("Contract", foreign_keys='Contract.com_contact_id', back_populates="com_contact")
    ges_contracts = relationship("Contract", foreign_keys='Contract.ges_contact_id', back_populates="ges_contact")
    ges_events = relationship("Event", foreign_keys='Event.ges_contact_id', back_populates="ges_contact")
    sup_events = relationship("Event", foreign_keys='Event.sup_contact_id', back_populates="sup_contact")

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
        base_username = (first_name[0] + last_name).lower()
        username = base_username
        counter = 1

        # Vérifie l'existence de l'username
        while session.query(cls).filter_by(username=username).first():
            username = f"{base_username}{counter}"
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

    @staticmethod
    def get_all_roles():
        """Permet de choisir le rôle de l'User"""
        return [ROLE_GES, ROLE_COM, ROLE_SUP, ROLE_ADM]

    def set_password(self, password):
        """Hache le mot de passe et le stocke."""
        salt = argon2.using(salt_size=16).generate_salt()
        salted_password = salt + password
        self.hashed_password = argon2.using(rounds=10).hash(salted_password)

    def check_password(self, hashed_password, verification_password):
        """Vérifie que le mot de passe fourni correspond au mot de passe haché."""
        return argon2.verify_password(hashed_password, verification_password)
