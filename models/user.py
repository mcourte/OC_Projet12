from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
import argon2
from constantes import ROLE_ADM, ROLE_COM, ROLE_GES, ROLE_SUP
from .base import Base


class User(Base):
    """ Définition de la classe User qui sera la table dans la BD"""
    __tablename__ = 'users'

    user_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(String(10), nullable=False, index=True)
    password = Column(String(60), nullable=False)

    # Relation entre les différents models
    com_contracts = relationship("Contract", foreign_keys='Contract.com_contact_id', back_populates="com_contact")
    ges_contracts = relationship("Contract", foreign_keys='Contract.ges_contact_id', back_populates="ges_contact")

    @classmethod
    def generate_unique_username():
        """Vérifie que l'username n'existe pas sinon ajoute un index ( à partir de 1 ) à la suite"""
        pass

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
