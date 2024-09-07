import pytest
from models.entities import Event, Contract, Commercial, EpicUser, Support, Gestion
from views.event_view import EventView
from views.user_view import UserView
from terminal.terminal_event import EpicTerminalEvent
from controllers.epic_controller import EpicDatabase
from controllers.session import create_engine, sessionmaker


@pytest.fixture(scope='module')
def test_session():
    # Crée une instance d'EpicDatabase avec les arguments requis
    db = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    # Crée un moteur et une session SQLAlchemy pour les tests
    engine = create_engine(db.get_engine_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    # Supprimer l'utilisateur spécifique s'il existe
    user_to_delete = session.query(EpicUser).filter_by(username='jdoe').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
    user_to_delete = session.query(EpicUser).filter_by(username='cdoe').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
    user_to_delete = session.query(EpicUser).filter_by(username='jbeam').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
    user_to_delete = session.query(EpicUser).filter_by(username='nuser').first()
    if user_to_delete:
        session.delete(user_to_delete)
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
    mocker.patch.object(EventView, 'prompt_data_event', return_value={"title": "Test Event",
                                                                      "description": "Description"})
    mocker.patch.object(EventView, 'prompt_add_support', return_value=False)

    # Simulation d'un utilisateur Commercial
    user = Commercial(epicuser_id=1, role='COM')
    setup_event_terminal.current_user = user

    # Appel de la méthode à tester
    setup_event_terminal.create_event(test_session)

    # Vérification que l'événement a été créé
    event = test_session.query(Event).filter_by(title="Test Event").first()
    assert event is not None
    assert event.title == "Test Event"


def test_update_event(setup_event_terminal, test_session, mocker):
    # Création d'un événement existant
    existing_event = Event(event_id=1, title="Old Event", description="Old Description")
    test_session.add(existing_event)
    test_session.commit()

    # Mock des méthodes de vue
    mocker.patch.object(EventView, 'prompt_select_event', return_value=existing_event)
    mocker.patch.object(EventView, 'prompt_data_event', return_value={"title": "Updated Event",
                                                                      "description": "Updated Description"})

    # Simulation de l'utilisateur ADM
    user = EpicUser(epicuser_id=1, role='ADM')
    setup_event_terminal.current_user = user

    # Appel de la méthode à tester
    setup_event_terminal.update_event(test_session)

    # Vérification que l'événement a été mis à jour
    event = test_session.query(Event).filter_by(event_id=1).first()
    assert event.title == "Updated Event"
    assert event.description == "Updated Description"


def test_list_of_events(setup_event_terminal, test_session, mocker):
    # Création d'événements dans la base de données
    event1 = Event(event_id=1, title="Event 1")
    event2 = Event(event_id=2, title="Event 2")
    test_session.add_all([event1, event2])
    test_session.commit()

    # Mock de la méthode d'affichage
    mocker.patch.object(EventView, 'display_list_events', return_value=None)

    # Simulation de l'utilisateur Gestion
    user = Gestion(epicuser_id=1, role='GES')
    setup_event_terminal.current_user = user

    # Appel de la méthode à tester
    setup_event_terminal.list_of_events(test_session)

    # Vérification que les événements sont listés
    events = test_session.query(Event).all()
    assert len(events) == 2


def test_update_event_support(setup_event_terminal, test_session, mocker):
    # Création d'un événement et d'un utilisateur Support
    event = Event(event_id=1, title="Event without Support", support_id=None)
    support_user = Support(epicuser_id=2, username="support_user", role="SUP")
    test_session.add_all([event, support_user])
    test_session.commit()

    # Mock de la vue pour sélectionner l'événement et le support
    mocker.patch.object(EventView, 'prompt_select_event', return_value=event)
    mocker.patch.object(UserView, 'prompt_select_support', return_value="support_user")

    # Simulation de l'utilisateur ADM
    user = EpicUser(epicuser_id=1, role='ADM')
    setup_event_terminal.current_user = user

    # Appel de la méthode à tester
    setup_event_terminal.update_event_support(test_session)

    # Vérification que le support a été attribué à l'événement
    updated_event = test_session.query(Event).filter_by(event_id=1).first()
    assert updated_event.support_id == support_user.epicuser_id
