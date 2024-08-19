import os
import sys
import random
from sqlalchemy import (
    ForeignKey,
    Column, Integer, String, TIMESTAMP, Sequence, Float
)
from sqlalchemy.orm import relationship, configure_mappers
from sqlalchemy_utils import ChoiceType
from sqlalchemy.sql import func
from sqlalchemy.exc import NoResultFound
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime
from sqlalchemy.orm import object_session
from unidecode import unidecode

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from config import Base


class EpicUser(Base):
    __tablename__ = 'epic_users'

    EPIC_ROLES = (
        ('COM', 'Commercial'),
        ('GES', 'Gestion'),
        ('SUP', 'Support'),
        ('ADM', 'Admin')
    )
    USER_STATES = (
        ('A', 'Actif'),
        ('I', 'Inactif')
    )

    role = Column(
        ChoiceType(EPIC_ROLES, impl=String(length=1)),
        nullable=False)
    epicuser_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(250), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    state = Column(ChoiceType(USER_STATES, impl=String(length=1)), default='A')

    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'USR'
    }

    # Relation entre les classes
    customers = relationship('Customer', back_populates='commercial')
    events = relationship('Event', back_populates='support', primaryjoin="EpicUser.epicuser_id==Event.support_id")

    @classmethod
    def generate_unique_username(cls, session, first_name, last_name):
        first_name_normalized = unidecode(first_name)
        last_name_normalized = unidecode(last_name)

        base_username = f"{first_name_normalized[0].lower()}{last_name_normalized.lower()}"
        username = base_username
        counter = 1

        while session.query(cls).filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    @classmethod
    def generate_unique_email(cls, session, username):
        base_email = f"{username}@epic.com"
        email = base_email
        counter = 1

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
        except VerifyMismatchError:
            return False

    def to_dict(self) -> dict:
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'role': self.role
        }

    @classmethod
    def getall(cls, session):
        return session.query(cls).all()

    @classmethod
    def find_by_userpwd(cls, session, username, password):
        try:
            user = session.query(cls).filter_by(username=username).one()
            if user.check_password(password):
                return user
        except NoResultFound:
            return None

    @classmethod
    def find_by_username(cls, session, username):
        return session.query(cls).filter_by(username=username).first()

    def update_role(self, new_role):
        self.role = new_role

    def set_inactive(self):
        """Définir un utilisateur comme inactif et déclencher les réaffectations ou notifications nécessaires."""
        self.state = 'I'
        session = object_session(self)
        session.commit()

        if self.role.code == 'COM':
            self.notify_gestion_to_reassign_user()
            self.reassign_customers()
        elif self.role.code == 'GES':
            self.notify_gestion_to_reassign_user()
            self.reassign_contracts()
        elif self.role.code == 'SUP':
            self.notify_gestion_to_reassign_user()
            self.reassign_events()

    def reassign_customers(self):
        """Réaffecte les clients du commercial inactif à un autre commercial."""
        new_commercial = self.find_alternate_commercial()
        for customer in self.customers:
            customer.commercial_id = new_commercial.epicuser_id
        session = object_session(self)
        session.commit()

        # Envoyer une notification au gestionnaire
        self.notify_gestion("Réaffectation des clients du commercial inactif terminée.")

    def reassign_contracts(self):
        """Réaffecte les contrats d'un gestionnaire inactif à un autre gestionnaire."""
        new_gestion = self.find_alternate_gestion()
        for contract in self.contracts:
            contract.gestion_id = new_gestion.epicuser_id
        session = object_session(self)
        session.commit()

        # Envoyer une notification au gestionnaire
        self.notify_gestion("Réaffectation des contrats du gestionnaire inactif terminée.")

    def reassign_events(self):
        """Réaffecte les contrats d'un support inactif à un autre support."""
        new_support = self.find_alternate_support()
        for event in self.events:
            event.support_id = new_support.epicuser_id
        session = object_session(self)
        session.commit()

        # Envoyer une notification au gestionnaire
        self.notify_gestion("Réaffectation des évènements du support inactif terminée.")

    def notify_gestion_to_reassign_user(self):
        """Notifier le gestionnaire pour réaffecter les événements du support inactif."""
        message = f"L'user {self.username} est inactif. Veuillez réaffecter ses clients/contrats/évènement."
        self.notify_gestion(message)

    def find_alternate_commercial(self):
        """Trouver un autre commercial pour réaffecter les clients."""
        session = object_session(self)
        return session.query(EpicUser).filter_by(role='COM', state='A').first()

    def find_alternate_gestion(self):
        """Trouver un autre gestionnaire pour réaffecter les contrats."""
        session = object_session(self)
        return session.query(EpicUser).filter_by(role='GES', state='A').first()

    def find_alternate_support(self):
        """Trouver un autre support pour réaffecter les évènements."""
        session = object_session(self)
        return session.query(EpicUser).filter_by(role='SUP', state='A').first()

    def notify_gestion(self, message):
        """Envoyer un message au gestionnaire pour des actions manuelles."""
        # Implémentation de l'envoi du message (par email, notification système, etc.)
        print(f"Notification pour le gestionnaire: {message}")


class Admin(EpicUser):

    __mapper_args__ = {
        'polymorphic_identity': 'ADM',
    }

    @classmethod
    def getall(cls, session):
        return session.query(cls).filter_by(role='ADM').order_by(cls.username).all()


class Commercial(EpicUser):

    __mapper_args__ = {
        'polymorphic_identity': 'COM',
    }

    @classmethod
    def getall(cls, session):
        return session.query(cls).filter_by(role='COM').order_by(cls.username).all()

    @property
    def contracts(self):
        contracts = []
        for customer in self.customers:
            contracts.extend(customer.contracts)
        return contracts


class Support(EpicUser):

    __mapper_args__ = {
        'polymorphic_identity': 'SUP',
    }

    events = relationship('Event', back_populates='support')

    @classmethod
    def getall(cls, session):
        return session.query(cls).filter_by(role='SUP').order_by(cls.username).all()


class Gestion(EpicUser):

    __mapper_args__ = {
        'polymorphic_identity': 'GES',
    }

    @classmethod
    def getall(cls, session):
        return session.query(cls).filter_by(role='GES').order_by(cls.username).all()

    @classmethod
    def getone(cls, session):
        all_gest = session.query(cls).filter_by(role='GES').order_by(cls.username).all()
        return random.choice(all_gest) if all_gest else None


class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False, index=True)
    email = Column(String(254), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    company_name = Column(String(100), nullable=False, index=True)
    creation_time = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    update_time = Column(TIMESTAMP, onupdate=func.now(), nullable=False)
    commercial_id = Column(Integer, ForeignKey('epic_users.epicuser_id'))

    commercial = relationship('EpicUser', back_populates='customers')
    events = relationship('Event', back_populates='customer')
    contracts = relationship('Contract', back_populates='customer')

    def __repr__(self):
        return f'Customer {self.first_name} {self.last_name}'

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(cls).filter_by(full_name=name).one()

    @classmethod
    def getall(cls, session):
        return session.query(cls).order_by(cls.last_name).all()

    @classmethod
    def find_without_contract(cls, session):
        return session.query(cls).outerjoin(Contract).filter(Contract.customer_id.is_(None)).order_by(
            cls.last_name).all()


class Event(Base):
    __tablename__ = 'events'

    event_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    location = Column(String)
    attendees = Column(Integer)
    report = Column(String)
    date_started = Column(TIMESTAMP, nullable=False)
    date_ended = Column(TIMESTAMP, nullable=False)

    contract_id = Column(Integer, ForeignKey('contracts.contract_id'))
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    support_id = Column(Integer, ForeignKey('epic_users.epicuser_id'))

    customer = relationship('Customer', back_populates='events')
    support = relationship('Support', back_populates='events')
    contract = relationship('Contract', back_populates='events')

    @classmethod
    def find_by_title(cls, session, contract_id, title):
        return session.query(cls).filter_by(title=title, contract_id=contract_id).one()

    @classmethod
    def find_by_support(cls, session, support_id, title):
        return session.query(cls).filter_by(title=title, support_id=support_id).one()

    @classmethod
    def getall(cls, session):
        return session.query(cls).all()


class Contract(Base):
    __tablename__ = 'contracts'

    CONTRACT_STATES = (
        ('C', 'Créé'),
        ('S', 'Signé'),
    )
    PAIEMENT_STATES = (
        ('P', 'Soldé'),
        ('N', 'Non_Soldé'),
    )

    contract_id = Column(Integer, Sequence('contract_id_seq'), primary_key=True)
    description = Column(String(500), nullable=False)
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=True)
    state = Column(ChoiceType(CONTRACT_STATES, impl=String(length=1)), default='C')
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False, index=True)
    paiement_state = Column(ChoiceType(PAIEMENT_STATES, impl=String(length=1)), default='N')

    customer = relationship('Customer', back_populates='contracts')
    events = relationship('Event', back_populates='contract')
    paiements = relationship('Paiement', back_populates='contract')

    def __repr__(self):
        return f'{self.description}'

    @classmethod
    def find_by_ref(cls, session, contract_id):
        return session.query(cls).filter_by(contract_id=contract_id).one()

    @classmethod
    def find_by_customer(cls, session, customer):
        return session.query(cls).filter_by(customer=customer).order_by(cls.contract_id).all()

    @classmethod
    def find_by_epicuser_id(cls, session, epicuser_id):
        return session.query(cls).filter_by(epicuser=epicuser_id).order_by(cls.contract_id).all()

    @classmethod
    def find_by_state(cls, session, state):
        return session.query(cls).filter_by(state=state).order_by(cls.contract_id).all()

    @classmethod
    def find_by_paiement_state(cls, session, paiement_state):
        return session.query(cls).filter_by(paiement_state=paiement_state).order_by(cls.contract_id).all()

    @classmethod
    def getall(cls, session):
        return session.query(cls).order_by(cls.contract_id).all()

    @classmethod
    def find_by_selection(cls, session, commercial, customer):
        query = session.query(cls).join(Customer, Customer.customer_id == cls.customer_id)
        if customer:
            query = query.filter(Customer.last_name == customer)
        if commercial:
            query = query.join(EpicUser, EpicUser.epicuser_id == Customer.commercial_id).filter(
                EpicUser.username == commercial)
        return query.order_by(cls.contract_id).all()


class Paiement(Base):
    __tablename__ = 'paiements'

    id = Column(Integer, primary_key=True)
    ref = Column(String, nullable=False, unique=True)
    date_amount = Column(TIMESTAMP, nullable=False, default=datetime.now())
    amount = Column(Integer)
    contract_id = Column(Integer, ForeignKey('contracts.contract_id'), nullable=False, index=True)

    contract = relationship('Contract', back_populates='paiements')

    def __repr__(self):
        return f'{self.date_amount}: {self.ref}/{self.amount}'

    @classmethod
    def find_by_ref(cls, session, ref):
        return session.query(cls).filter_by(ref=ref).one()


configure_mappers()
