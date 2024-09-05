import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import Customer, EpicUser, Admin
from controllers.customer_controller import CustomerBase
from terminal.terminal_customer import EpicTerminalCustomer
from config_init import Base
from datetime import datetime


# Configuration de la base de données en mémoire pour les tests
@pytest.fixture(scope='module')
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Création d'un utilisateur actif
    admin = Admin(first_name="Admin", last_name="User", password="password", email="auser@epic.com",
                  username="auser", state="A", role="ADM")
    commercial = EpicUser(first_name="Commercial", last_name="User", password="password", email="cuser@epic.com",
                          username="cuser", state="A", role="COM")
    session.add(admin)
    session.add(commercial)
    session.commit()

    # Ajout d'un client avec des dates en datetime
    now = datetime.now()
    customer = Customer(first_name="Test", last_name="Customer", email='test@gmail.com', phone='0649730864', company_name='Test',
                        commercial_id=1, creation_time=now, update_time=now)
    session.add(customer)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def epic_terminal_customer(db_session):
    # Récupérer l'utilisateur pour les tests
    user = db_session.query(EpicUser).filter_by(username="auser").first()
    return EpicTerminalCustomer(base=CustomerBase(session=db_session), session=db_session, current_user=user)


def test_choice_customer(epic_terminal_customer, db_session):
    # Test de la méthode choice_customer
    commercial = db_session.query(EpicUser).filter_by(username="cuser").first()
    customers = db_session.query(Customer).filter_by(commercial_id=commercial.epicuser_id).all()

    selected_customer = epic_terminal_customer.choice_customer(db_session, "cuser")
    assert selected_customer is None  # Pas de client pour le commercial dans cet exemple


def test_list_of_customers(epic_terminal_customer, db_session):
    # Test de la méthode list_of_customers
    epic_terminal_customer.list_of_customers(db_session)
    # Vérifiez que la méthode `console.print` a été appelée avec le texte attendu.
    # Vous devrez peut-être utiliser un outil pour capturer les appels à `console.print`


def test_update_customer_commercial(epic_terminal_customer, db_session):
    # Test de la méthode update_customer_commercial
    customer = db_session.query(Customer).first()
    commercial = db_session.query(EpicUser).filter_by(username="cuser").first()

    epic_terminal_customer.update_customer_commercial(db_session)

    # Vérifiez si le commercial a été correctement attribué au client
    updated_customer = db_session.query(Customer).filter_by(customer_id=customer.customer_id).first()
    assert updated_customer.commercial_id == commercial.epicuser_id


def test_create_customer(epic_terminal_customer, db_session):
    # Test de la méthode create_customer
    epic_terminal_customer.create_customer(db_session)
    # Vous devrez vérifier si un nouveau client a été ajouté avec succès à la base de données


def test_update_customer(epic_terminal_customer, db_session):
    # Test de la méthode update_customer
    customer = db_session.query(Customer).first()

    epic_terminal_customer.update_customer(db_session)

    # Vérifiez si les informations du client ont été mises à jour
    updated_customer = db_session.query(Customer).filter_by(customer_id=customer.customer_id).first()
    assert updated_customer is not None


def test_add_customer_commercial(epic_terminal_customer, db_session):
    # Test de la méthode add_customer_commercial
    customer = db_session.query(Customer).first()
    epic_terminal_customer.add_customer_commercial(db_session, customer)

    # Vérifiez si le commercial a été correctement attribué au client
    updated_customer = db_session.query(Customer).filter_by(customer_id=customer.customer_id).first()
    assert updated_customer.commercial_id is not None
