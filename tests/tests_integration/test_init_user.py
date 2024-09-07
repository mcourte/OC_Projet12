import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from controllers.epic_controller import EpicUser, EpicDatabase
from terminal.terminal_user import EpicTerminalUser
from views.user_view import UserView
from config_test import get_cached_token


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


@pytest.fixture(scope='module')
def terminal_user(test_session):
    db = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    terminal_user = EpicTerminalUser(db, test_session, current_user=None)
    return terminal_user


@pytest.fixture
def setup_user(test_session):
    """Créer un utilisateur de test unique pour les tests."""
    user = test_session.query(EpicUser).filter_by(username='mcourte').first()
    test_session.add(user)
    test_session.commit()
    return user


def test_show_profil(terminal_user, setup_user, capsys):
    token = get_cached_token()
    terminal_user.current_user = setup_user
    terminal_user.show_profil(test_session, token)

    # Capture la sortie pour vérifier le contenu affiché
    captured = capsys.readouterr()
    output = captured.out
    assert "Magali" in output
    assert "Courté" in output
    assert "mcourte" in output
    assert "ADM" in output


def test_update_profil(terminal_user, setup_user, test_session):
    token = get_cached_token()
    user = setup_user
    terminal_user.current_user = user

    # Simulez les réponses de l'utilisateur pour les mises à jour
    UserView.prompt_update_user = lambda _: ('Choupette', 'Doe', 'newpassword')

    terminal_user.update_profil(test_session, token)

    # Rechargez l'utilisateur depuis la base de données
    updated_user = test_session.query(EpicUser).filter_by(username=user.username).first()

    assert updated_user.first_name == 'Choupette'
    assert updated_user.last_name == 'Doe'
    assert updated_user.check_password('newpassword')  # Assurez-vous que la méthode check_password existe


def test_list_of_users(terminal_user, test_session, capsys):
    # Configurez les utilisateurs pour le test
    users = test_session.query(EpicUser).all()
    terminal_user.list_of_users(users)

    # Capture la sortie pour vérifier le contenu affiché
    output = capsys.readouterr().out
    assert "jfoe" in output
    assert "John Foe" in output
    assert "jbeam" in output
    assert "John Beam" in output


def test_create_user(terminal_user, test_session):
    # Simulez les entrées de l'utilisateur pour le test
    UserView.prompt_data_role = lambda: {'role': 'COM'}
    UserView.prompt_data_user = lambda: {'username': 'nuser', 'first_name': 'New', 'last_name': 'User'}
    UserView.prompt_password = lambda: {'password': 'newpassword'}

    terminal_user.create_user(test_session)

    # Vérifiez que le nouvel utilisateur a été ajouté à la base de données
    new_user = test_session.query(EpicUser).filter_by(username='nuser').first()

    assert new_user is not None
    assert new_user.first_name == 'New'
    assert new_user.last_name == 'User'
    assert new_user.role == 'COM'
    assert new_user.check_password('newpassword')  # Assurez-vous que la méthode check_password existe


def test_inactivate_user(terminal_user, setup_user, test_session):
    user = 'cdoe'
    terminal_user.current_user = user
    terminal_user.inactivate_user(test_session)

    inactivated_user = test_session.query(EpicUser).filter_by(username='cdoe').first()
    assert inactivated_user is not None
    assert not inactivated_user.is_active  # Supposons qu'il y a un champ is_active


def test_delete_user(terminal_user, setup_user, test_session):
    user = 'jdoe'
    terminal_user.current_user = user
    terminal_user.delete_user(test_session)

    deleted_user = test_session.query(EpicUser).filter_by(username=user).first()
    assert deleted_user is None
