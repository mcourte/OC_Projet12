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

from config_init import Base


class EpicUser(Base):
    """
    Classe représentant un utilisateur dans le système Epic.

    Attributs :
    -----------
    EPIC_ROLES : tuple
        Liste des rôles possibles pour les utilisateurs.
    USER_STATES : tuple
        Liste des états possibles pour les utilisateurs.
    role : Column
        Rôle de l'utilisateur.
    epicuser_id : Column
        Identifiant unique de l'utilisateur.
    first_name : Column
        Prénom de l'utilisateur.
    last_name : Column
        Nom de l'utilisateur.
    username : Column
        Nom d'utilisateur unique.
    password : Column
        Mot de passe de l'utilisateur, haché.
    email : Column
        Adresse e-mail unique de l'utilisateur.
    state : Column
        État de l'utilisateur (actif ou inactif).

    Relations :
    -----------
    customers : relationship
        Liste des clients associés à l'utilisateur en tant que commercial.
    events : relationship
        Liste des événements associés à l'utilisateur en tant que support.
    """

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
        """
        Génère un nom d'utilisateur unique à partir du prénom et du nom.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        first_name : str
            Le prénom de l'utilisateur.
        last_name : str
            Le nom de famille de l'utilisateur.

        Retourne :
        ----------
        str : Nom d'utilisateur unique généré.
        """
        first_name_normalized = unidecode(first_name)
        last_name_normalized = unidecode(last_name)

        # Remplacement des espaces par des underscores dans le nom de famille
        last_name_normalized = last_name_normalized.replace(" ", "_")

        base_username = f"{first_name_normalized[0].lower()}{last_name_normalized.lower()}"
        username = base_username
        counter = 1

        while session.query(cls).filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    @classmethod
    def generate_unique_email(cls, session, username):
        """
        Génère une adresse e-mail unique à partir du nom d'utilisateur.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        username : str
            Le nom d'utilisateur.

        Retourne :
        ----------
        str : Adresse e-mail unique générée.
        """
        base_email = f"{username}@epic.com"
        email = base_email
        counter = 1

        while session.query(cls).filter_by(email=email).first():
            email = f"{username}{counter}@epic.com"
            counter += 1
        return email

    def set_password(self, password):
        """
        Hache et définit le mot de passe de l'utilisateur.

        Paramètres :
        ------------
        password : str
            Le mot de passe en texte clair.
        """
        ph = PasswordHasher()
        self.password = ph.hash(password)

    def check_password(self, verification_password):
        """
        Vérifie si un mot de passe correspond au mot de passe haché de l'utilisateur.

        Paramètres :
        ------------
        verification_password : str
            Le mot de passe à vérifier.

        Retourne :
        ----------
        bool : True si le mot de passe correspond, False sinon.
        """
        ph = PasswordHasher()
        try:
            return ph.verify(self.password, verification_password)
        except VerifyMismatchError:
            return False

    def to_dict(self) -> dict:
        """
        Convertit les informations de l'utilisateur en dictionnaire.

        Retourne :
        ----------
        dict : Dictionnaire des informations de l'utilisateur.
        """
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'role': self.role
        }

    @classmethod
    def get_all_users(cls, session):
        """
        Récupère tous les utilisateurs dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les utilisateurs.
        """
        return session.query(cls).all()

    @classmethod
    def find_by_userpwd(cls, session, username, password):
        """
        Trouve un utilisateur par son nom d'utilisateur et son mot de passe.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        username : str
            Le nom d'utilisateur.
        password : str
            Le mot de passe en texte clair.

        Retourne :
        ----------
        EpicUser : L'utilisateur trouvé, ou None s'il n'est pas trouvé.
        """
        try:
            user = session.query(cls).filter_by(username=username).one()
            if user.check_password(password):
                return user
        except NoResultFound:
            return None

    @classmethod
    def find_by_username(cls, session, username):
        """
        Trouve un utilisateur par son nom d'utilisateur.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        username : str
            Le nom d'utilisateur.

        Retourne :
        ----------
        EpicUser : L'utilisateur trouvé, ou None s'il n'est pas trouvé.
        """
        return session.query(cls).filter_by(username=username).first()

    def update_role(self, new_role):
        """
        Met à jour le rôle de l'utilisateur.

        Paramètres :
        ------------
        new_role : str
            Le nouveau rôle à assigner.
        """
        self.role = new_role

    def set_inactive(self):
        """
        Définit l'utilisateur comme inactif et déclenche les réaffectations ou notifications nécessaires.
        """
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
    def get_all_admins(cls, session):
        """
        Récupère tous les administrateurs dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les administrateurs.
        """
        return session.query(cls).filter_by(role='ADM').order_by(cls.username).all()


class Commercial(EpicUser):

    __mapper_args__ = {
        'polymorphic_identity': 'COM',
    }

    @classmethod
    def get_all_commercials(cls, session):
        """
        Récupère tous les commerciaux dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les commerciaux.
        """
        return session.query(cls).filter_by(role='COM').order_by(cls.username).all()

    @property
    def contracts(self):
        """
        Récupère tous les contrats associés aux clients du commercial.

        Retourne :
        ----------
        list : Liste de tous les contrats.
        """
        contracts = []
        for customer in self.customers:
            contracts.extend(customer.contracts)
        return contracts


class Support(EpicUser):
    """
    Classe représentant un utilisateur avec le rôle de Support.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'SUP',
    }

    events = relationship('Event', back_populates='support')

    @classmethod
    def get_all_supports(cls, session):
        """
        Récupère tous les supports dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les supports.
        """
        return session.query(cls).filter_by(role='SUP').order_by(cls.username).all()


class Gestion(EpicUser):
    """
    Classe représentant un utilisateur avec le rôle de Gestionnaire.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'GES',
    }

    @classmethod
    def get_all_gestions(cls, session):
        """
        Récupère tous les gestionnaires dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les gestionnaires.
        """
        return session.query(cls).filter_by(role='GES').order_by(cls.username).all()

    @classmethod
    def get_gestion(cls, session):
        """
        Récupère un gestionnaire au hasard dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        Gestion : Un gestionnaire aléatoire, ou None s'il n'y en a pas.
        """
        all_gest = session.query(cls).filter_by(role='GES').order_by(cls.username).all()
        return random.choice(all_gest) if all_gest else None


class Customer(Base):
    """
    Classe représentant un client dans le système.
    """
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
        """
        Trouve un client par son nom complet.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        name : str
            Le nom complet du client.

        Retourne :
        ----------
        Customer : Le client trouvé, ou lève une exception s'il n'est pas trouvé.
        """
        return session.query(cls).filter_by(full_name=name).one()

    @classmethod
    def get_all_customers(cls, session):
        """
        Récupère tous les clients dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les clients.
        """
        return session.query(cls).order_by(cls.last_name).all()

    @classmethod
    def find_without_contract(cls, session):
        """
        Trouve tous les clients sans contrat.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les clients sans contrat.
        """
        return session.query(cls).outerjoin(Contract).filter(Contract.customer_id.is_(None)).order_by(
            cls.last_name).all()


class Event(Base):
    """
    Classe représentant un événement dans le système.

    Attributs :
    -----------
    event_id : Column
        Identifiant unique de l'événement.
    title : Column
        Titre de l'événement.
    description : Column
        Description de l'événement.
    location : Column
        Lieu de l'événement.
    attendees : Column
        Nombre de participants à l'événement.
    report : Column
        Rapport associé à l'événement.
    date_started : Column
        Date de début de l'événement.
    date_ended : Column
        Date de fin de l'événement.
    contract_id : Column
        Identifiant du contrat associé.
    customer_id : Column
        Identifiant du client associé.
    support_id : Column
        Identifiant du support associé.

    Relations :
    -----------
    customer : relationship
        Relation avec le client associé à l'événement.
    support : relationship
        Relation avec le support associé à l'événement.
    contract : relationship
        Relation avec le contrat associé à l'événement.
    """
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
        """
        Trouve un événement par son titre et l'identifiant du contrat.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        contract_id : int
            L'identifiant du contrat associé à l'événement.
        title : str
            Le titre de l'événement.

        Retourne :
        ----------
        Event : L'événement trouvé.
        """
        return session.query(cls).filter_by(title=title, contract_id=contract_id).one()

    @classmethod
    def find_by_support(cls, session, support_id, title):
        """
        Trouve un événement par son titre et l'identifiant du support.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        support_id : int
            L'identifiant du support associé à l'événement.
        title : str
            Le titre de l'événement.

        Retourne :
        ----------
        Event : L'événement trouvé.
        """
        return session.query(cls).filter_by(title=title, support_id=support_id).one()

    @classmethod
    def get_all_events(cls, session):
        """
        Récupère tous les événements dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les événements.
        """
        return session.query(cls).all()


class Contract(Base):
    """
    Classe représentant un contrat dans le système.

    Attributs :
    -----------
    CONTRACT_STATES : tuple
        États possibles d'un contrat (Créé, Signé).
    PAIEMENT_STATES : tuple
        États possibles de paiement (Soldé, Non_Soldé).
    contract_id : Column
        Identifiant unique du contrat.
    description : Column
        Description du contrat.
    total_amount : Column
        Montant total du contrat.
    remaining_amount : Column
        Montant restant dû.
    state : Column
        État actuel du contrat.
    customer_id : Column
        Identifiant du client associé au contrat.
    paiement_state : Column
        État actuel du paiement du contrat.

    Relations :
    -----------
    customer : relationship
        Relation avec le client associé au contrat.
    events : relationship
        Liste des événements associés au contrat.
    paiements : relationship
        Liste des paiements associés au contrat.
    """
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

    commercial_id = Column(Integer, ForeignKey('epic_users.epicuser_id'))
    gestion_id = Column(Integer, ForeignKey('epic_users.epicuser_id'))

    customer = relationship('Customer', back_populates='contracts')
    events = relationship('Event', back_populates='contract')
    paiements = relationship('Paiement', back_populates='contract')

    def __repr__(self):
        """
        Retourne une représentation en chaîne de caractères du contrat.

        Retourne :
        ----------
        str : Description du contrat.
        """
        return f'{self.description}'

    @classmethod
    def find_by_contract_id(cls, session, contract_id):
        """
        Trouve un contrat par son identifiant.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        contract_id : int
            L'identifiant du contrat.

        Retourne :
        ----------
        Contract : Le contrat trouvé.
        """
        return session.query(cls).filter_by(contract_id=contract_id).one()

    @classmethod
    def find_by_customer(cls, session, customer):
        """
        Trouve tous les contrats associés à un client donné.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        customer : Customer
            Le client dont on cherche les contrats.

        Retourne :
        ----------
        list : Liste des contrats associés au client.
        """
        return session.query(cls).filter_by(customer=customer).order_by(cls.contract_id).all()

    @classmethod
    def find_by_epicuser_id(cls, session, epicuser_id):
        """
        Trouve tous les contrats associés à un utilisateur Epic spécifique.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        epicuser_id : int
            L'identifiant de l'utilisateur Epic.

        Retourne :
        ----------
        list : Liste des contrats associés à l'utilisateur.
        """
        return session.query(cls).filter_by(epicuser=epicuser_id).order_by(cls.contract_id).all()

    @classmethod
    def find_by_state(cls, session, state):
        """
        Trouve tous les contrats par état.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        state : str
            L'état des contrats à rechercher.

        Retourne :
        ----------
        list : Liste des contrats correspondant à l'état.
        """
        return session.query(cls).filter_by(state=state).order_by(cls.contract_id).all()

    @classmethod
    def state_signed(cls, session):
        """
        Trouve tous les contrats signés.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les contrats signés.
        """
        return session.query(cls).filter_by(state="S").order_by(cls.contract_id).all()

    @classmethod
    def find_by_paiement_state(cls, session, paiement_state):
        """
        Trouve tous les contrats par état de paiement.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        paiement_state : str
            L'état de paiement des contrats à rechercher.

        Retourne :
        ----------
        list : Liste des contrats correspondant à l'état de paiement.
        """
        return session.query(cls).filter_by(paiement_state=paiement_state).order_by(cls.contract_id).all()

    @classmethod
    def get_all_contracts(cls, session):
        """
        Récupère tous les contrats dans la base de données.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.

        Retourne :
        ----------
        list : Liste de tous les contrats.
        """
        return session.query(cls).order_by(cls.contract_id).all()

    @classmethod
    def find_by_selection(cls, session, commercial, customer):
        """
        Trouve tous les contrats en fonction d'un commercial et/ou d'un client.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        commercial : str
            Le nom d'utilisateur du commercial.
        customer : str
            Le nom de famille du client.

        Retourne :
        ----------
        list : Liste des contrats correspondant aux critères.
        """
        query = session.query(cls).join(Customer, Customer.customer_id == cls.customer_id)
        if customer:
            query = query.filter(Customer.last_name == customer)
        if commercial:
            query = query.join(EpicUser, EpicUser.epicuser_id == Customer.commercial_id).filter(
                EpicUser.username == commercial)
        return query.order_by(cls.contract_id).all()


class Paiement(Base):
    """
    Classe représentant un paiement dans le système.

    Attributs :
    -----------
    id : Column
        Identifiant unique du paiement.
    ref : Column
        Référence unique du paiement.
    date_amount : Column
        Date et heure du paiement.
    amount : Column
        Montant payé.
    contract_id : Column
        Identifiant du contrat associé au paiement.

    Relations :
    -----------
    contract : relationship
        Relation avec le contrat associé au paiement.
    """
    __tablename__ = 'paiements'

    paiement_id = Column(Integer, primary_key=True)
    date_amount = Column(TIMESTAMP, nullable=False, default=datetime.now())
    amount = Column(Integer)
    contract_id = Column(Integer, ForeignKey('contracts.contract_id'), nullable=False, index=True)

    contract = relationship('Contract', back_populates='paiements')

    def __init__(self, paiement_id, amount, contract_id):
        self.paiement_id = paiement_id
        self.amount = amount
        self.contract_id = contract_id
        self.date_amount = datetime.now()

    def __repr__(self):
        """
        Retourne une représentation en chaîne de caractères du paiement.

        Retourne :
        ----------
        str : Représentation du paiement avec la date, la référence et le montant.
        """
        return f'{self.date_amount}: {self.ref}/{self.amount}'

    @classmethod
    def find_by_paiement_id(cls, session, paiement_id):
        """
        Trouve un paiement par sa référence unique.

        Paramètres :
        ------------
        session : Session
            La session de la base de données en cours.
        ref : str
            La référence unique du paiement.

        Retourne :
        ----------
        Paiement : Le paiement trouvé.
        """
        return session.query(cls).filter_by(paiement_id=paiement_id).one()


configure_mappers()
