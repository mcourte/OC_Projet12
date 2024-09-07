import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.entities import EpicUser, Event, Contract
from terminal.terminal_event import EpicTerminalEvent, EventView, UserView
from config_test import generate_valid_token, SECRET_KEY
from controllers.epic_controller import EpicDatabase


@pytest.fixture(scope='module')
def test_session():
    # Crée une instance d'EpicDatabase avec les arguments requis
    db = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    # Crée un moteur et une session SQLAlchemy pour les tests
    engine = create_engine(db.get_engine_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    # Supprimer les utilisateurs spécifiques s'ils existent
    users_to_delete = ['jdoe', 'cdoe', 'jbeam', 'nuser', 'ecourte', 'ncourte']
    for username in users_to_delete:
        user_to_delete = session.query(EpicUser).filter_by(username=username).first()
        if user_to_delete:
            session.delete(user_to_delete)
            session.commit()

    # Supprimer les clients spécifiques s'ils existent
    events_to_delete = ['350', '200', '210', '131']
    for event_id in events_to_delete:
        event_to_delete = session.query(Event).filter_by(event_id=event_id).first()
        if event_to_delete:
            session.delete(event_to_delete)
            session.commit()

    yield session
    session.close()


@pytest.fixture
def epic_database():
    # Création et configuration de la base de données
    database = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    yield database


@pytest.fixture
def setup_event_terminal(epic_database, test_session):
    return EpicTerminalEvent(epic_database, test_session)  # Assure-toi que cette classe existe


def test_create_event(setup_event_terminal, test_session, mocker):
    # Mock de la vue pour sélectionner un contrat et entrer les données de l'événement
    mocker.patch.object(EventView, 'prompt_select_contract', return_value=Contract(contract_id=1, state="S"))
    mocker.patch.object(EventView, 'prompt_data_event', return_value={
        "title": "Test Event",
        "description": "Description",
        "date_started": datetime.now(),  # Assure-toi que ces champs ne sont pas null
        "date_ended": datetime.now() + timedelta(hours=2)
    })
    mocker.patch.object(EventView, 'prompt_add_support', return_value=False)

    # Simulation d'un utilisateur Commercial
    user = EpicUser(
        role='COM',
        first_name='Eva',
        last_name='Courté',
        username='ecourte',
        password='securepassword',
        email='ecourte@epic.com',
        state='A'
    )
    setup_event_terminal.current_user = user
    setup_event_terminal.current_token = generate_valid_token(user.username, SECRET_KEY)  # Assure-toi que le token est valide

    try:
        # Appel de la méthode à tester
        setup_event_terminal.create_event(test_session)

        # Vérification que l'événement a été créé
        event = test_session.query(Event).filter_by(title="Test Event").first()
        assert event is not None
        assert event.title == "Test Event"
    except Exception:
        test_session.rollback()
        raise


def test_update_event(setup_event_terminal, test_session, mocker):
    # Création d'un événement existant
    existing_event = Event(event_id=350, title="Old Event", description="Old Description",
                           date_started=datetime.now(), date_ended=datetime.now() + timedelta(hours=2))
    test_session.add(existing_event)
    test_session.commit()

    # Mock des méthodes de vue
    mocker.patch.object(EventView, 'prompt_select_event', return_value=existing_event)
    mocker.patch.object(EventView, 'prompt_data_event', return_value={
        "title": "Updated Event",
        "description": "Updated Description",
        "date_started": datetime.now(),
        "date_ended": datetime.now() + timedelta(hours=2)
    })
    # Simulation de l'utilisateur ADM
    user = EpicUser(
        role='ADM',
        first_name='Eva',
        last_name='Courté',
        username='ecourte',
        password='securepassword',
        email='ecourte@epic.com',
        state='A'
    )
    setup_event_terminal.current_user = user
    setup_event_terminal.current_token = generate_valid_token(user.username, SECRET_KEY)

    try:
        # Appel de la méthode à tester
        setup_event_terminal.update_event(test_session)

        # Vérification que l'événement a été mis à jour
        event = test_session.query(Event).filter_by(event_id=350).first()
        assert event.title == "Updated Event"
        assert event.description == "Updated Description"
    except Exception:
        test_session.rollback()
        raise


def test_list_of_events(setup_event_terminal, test_session, mocker):
    # Création d'événements dans la base de données
    event1 = Event(event_id=200, title="Event 1", date_started=datetime.now(), date_ended=datetime.now() + timedelta(hours=2))
    event2 = Event(event_id=210, title="Event 2", date_started=datetime.now(), date_ended=datetime.now() + timedelta(hours=2))
    test_session.add_all([event1, event2])
    test_session.commit()

    # Mock de la méthode d'affichage
    mocker.patch.object(EventView, 'display_list_events', return_value=None)

    # Simulation de l'utilisateur Gestion
    user = EpicUser(
        role='GES',
        first_name='Eva',
        last_name='Courté',
        username='ecourte',
        password='securepassword',
        email='ecourte@epic.com',
        state='A'
    )
    setup_event_terminal.current_user = user
    setup_event_terminal.current_token = generate_valid_token(user.username, SECRET_KEY)  # Assure-toi que le token est valide

    try:
        # Appel de la méthode à tester
        setup_event_terminal.list_of_events(test_session)

        # Vérification que les événements sont listés
        events = test_session.query(Event).all()
        assert len(events) == 2
    except Exception:
        test_session.rollback()
        raise


def test_update_event_support(setup_event_terminal, test_session, mocker):
    # Création d'un événement et d'un utilisateur Support
    event = Event(event_id=131, title="Event without Support", support_id=None,
                  date_started=datetime.now(), date_ended=datetime.now() + timedelta(hours=2))
    support_user = EpicUser(
        role='GES',
        first_name='Eva',
        last_name='Courté',
        username='ecourte',
        password='securepassword',
        email='ecourte@epic.com',
        state='A'
    )
    test_session.add_all([event, support_user])
    test_session.commit()

    # Mock de la vue pour sélectionner l'événement et le support
    mocker.patch.object(EventView, 'prompt_select_event', return_value=event)
    mocker.patch.object(UserView, 'prompt_select_support', return_value="support_user")

    # Simulation de l'utilisateur ADM
    user = EpicUser(
        role='ADM',
        first_name='Nolan',
        last_name='Courté',
        username='ncourte',
        password='securepassword',
        email='ncourte@epic.com',
        state='A'
    )
    setup_event_terminal.current_user = user
    setup_event_terminal.current_token = generate_valid_token(user.username, SECRET_KEY)  # Assure-toi que le token est valide

    try:
        # Appel de la méthode à tester
        setup_event_terminal.update_event_support(test_session)

        # Vérification que le support a été attribué à l'événement
        updated_event = test_session.query(Event).filter_by(event_id=131).first()
        assert updated_event.support_id == support_user.epicuser_id
    except Exception:
        test_session.rollback()
        raise
