import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from terminal.terminal_contract import EpicTerminalContract
from controllers.user_controller import EpicUserBase
from models.entities import Contract
from config_init import Base, SECRET_KEY
from controllers.session import create_token


@pytest.fixture
def test_session():
    # Crée une base de données temporaire en mémoire
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


def test_list_of_contracts(test_session):
    # Crée un utilisateur commercial pour le test
    data_user = {'password': 'password', 'first_name': 'Admin', 'last_name': 'User', 'role': 'Commercial'}
    user = EpicUserBase.create_user(test_session, data_user)
    test_session.add(user)
    test_session.commit()

    # Prépare les données utilisateur pour le token
    user_data = {
        'username': 'auser',
        'role': 'COM'
    }
    # Crée un token pour l'utilisateur
    # Crée un token pour l'utilisateur
    token = create_token(user_data, SECRET_KEY)
    print("Generated Token:", token)
    # Crée des contrats pour le test
    contract1 = Contract(commercial_id=user.epicuser_id, customer_id=1, description='test',
                         total_amount=5000, remaining_amount=5000, state='C', paiement_state='N')
    contract2 = Contract(commercial_id=user.epicuser_id, customer_id=1, description='test',
                         total_amount=5000, remaining_amount=0, state='S', paiement_state='P')
    test_session.add_all([contract1, contract2])
    test_session.commit()

    # Instancie EpicTerminalContract et exécute la méthode
    terminal_contract = EpicTerminalContract(token, test_session)
    terminal_contract.current_user = user
    terminal_contract.list_of_contracts(test_session)


def test_create_contract(test_session):
    data_user = {'first_name': 'Admin',
                 'last_name': 'User',
                 'password': 'password',
                 'role': 'Commercial'}
    user = EpicUserBase.create_user(test_session, data_user)
    test_session.add(user)
    test_session.commit()

    # Instancie EpicTerminalContract et exécute la méthode
    terminal_contract = EpicTerminalContract(None, test_session)
    terminal_contract.current_user = user
    terminal_contract.create_contract(test_session)

    # Vérifiez que le contrat a été créé dans la base de données
    contracts = test_session.query(Contract).all()
    assert len(contracts) > 0


def test_update_contract(test_session):
    data_user = {'first_name': 'Admin',
                 'last_name': 'User',
                 'password': 'password',
                 'role': 'Commercial'}
    user = EpicUserBase.create_user(test_session, data_user)

    test_session.add(user)
    test_session.commit()

    contract = Contract(commercial_id=user.epicuser_id, customer_id=1, description='test',
                        total_amount=5000, remaining_amount=5000,
                        state='C', paiement_state='N')
    test_session.add(contract)
    test_session.commit()

    terminal_contract = EpicTerminalContract(None, test_session)
    terminal_contract.current_user = user

    # Simulez la sélection d'un contrat à mettre à jour
    terminal_contract.update_contract(test_session)

    # Vérifiez les modifications du contrat
    updated_contract = test_session.query(Contract).filter_by(contract_id=contract.contract_id).first()
    assert updated_contract.state == 'S'  # Supposons que le contrat a été signé


def test_update_contract_gestion(test_session):
    data_admin = {'first_name': 'Admin',
                  'last_name': 'User',
                  'password': 'password',
                  'role': 'Commercial'}
    admin = EpicUserBase.create_user(test_session, data_admin)
    data_ges = {'first_name': 'Test',
                'last_name': 'User',
                'password': 'password',
                'role': 'Gestion'}
    gestionnaire = EpicUserBase.create_user(test_session, data_ges)

    test_session.add_all([admin, gestionnaire])
    test_session.commit()

    contract = Contract(commercial_id=admin.epicuser_id, customer_id=1, description='test',
                        total_amount=5000, remaining_amount=5000,
                        state='C', paiement_state='N')
    test_session.add(contract)
    test_session.commit()

    terminal_contract = EpicTerminalContract(None, test_session)
    terminal_contract.current_user = admin

    terminal_contract.update_contract_gestion(test_session)

    # Vérifiez que le gestionnaire a été attribué au contrat
    updated_contract = test_session.query(Contract).filter_by(contract_id=contract.contract_id).first()
    assert updated_contract.gestion_id == gestionnaire.epicuser_id


def test_add_paiement_contract(test_session):
    data_user = {'first_name': 'Admin',
                 'last_name': 'User',
                 'password': 'password',
                 'role': 'Commercial'}
    user = EpicUserBase.create_user(test_session, data_user)

    test_session.add(user)
    test_session.commit()

    contract = Contract(commercial_id=user.epicuser_id, customer_id=1, description='test',
                        total_amount=5000, remaining_amount=5000,
                        state='C', paiement_state='N')
    test_session.add(contract)
    test_session.commit()

    terminal_contract = EpicTerminalContract(None, test_session)
    terminal_contract.current_user = user

    terminal_contract.add_paiement_contract(test_session)

    # Vérifiez que le paiement a été ajouté au contrat
    updated_contract = test_session.query(Contract).filter_by(contract_id=contract.contract_id).first()
    assert updated_contract.paiement_state == 'P'  # Supposons que le paiement a été ajouté
