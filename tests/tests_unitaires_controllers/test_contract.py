import pytest
import jwt
from decimal import Decimal
from datetime import datetime, timedelta
from controllers.contract_controller import ContractBase
from models.entities import Contract, EpicUser
from config_init import Base, SECRET_KEY
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Fonction pour générer un token JWT pour un utilisateur donné
def generate_test_token(user):
    payload = {
        'user_id': user.epicuser_id,
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'iat': datetime.utcnow(),
        'roles': user.role  # Assurez-vous que 'user.role' est une chaîne
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


# Configurer la base de données de test en mémoire
@pytest.fixture(scope='module')
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)  # Crée toutes les tables dans la base en mémoire
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insérer un utilisateur actif pour les tests
    user = EpicUser(first_name="Test", last_name="User", password="password", email="tuser@epic.com",
                    username="test_user", state="A", role="ADM")
    session.add(user)
    session.commit()

    yield session  # Fournir la session aux tests

    session.close()
    Base.metadata.drop_all(engine)  # Nettoyer après les tests


@pytest.fixture
def contract_base(db_session):
    # Récupérer l'utilisateur pour les tests
    user = db_session.query(EpicUser).filter_by(username="test_user").first()
    # Générer un token pour l'utilisateur
    token = generate_test_token(user)
    return ContractBase(session=db_session, current_user=user, token=token)


def test_create_contract_success(contract_base, db_session):
    data = {
        'description': 'Test Contract',
        'total_amount': 1000,
        'remaining_amount': 1000,
        'customer_id': 1,
        'commercial_id': 1,
        'gestion_id': 1,
        'state': 'C',  # Utiliser le code de l'état comme une chaîne simple
        'paiement_state': 'N'  # Utiliser le code de l'état de paiement comme une chaîne simple
    }
    contract = contract_base.create_contract(db_session, data)
    assert contract is not None
    assert contract.description == 'Test Contract'


def test_add_paiement_success(contract_base, db_session):
    # Créer un contrat pour ajouter le paiement
    data = {
        'description': 'Test Contract',
        'total_amount': 1000,
        'remaining_amount': 1000,
        'customer_id': 1,
        'commercial_id': 1,
        'gestion_id': 1,
        'state': 'S',  # Utiliser le code de l'état comme une chaîne simple
        'paiement_state': 'N'  # Utiliser le code de l'état de paiement comme une chaîne simple
    }
    contract = contract_base.create_contract(db_session, data)

    paiement_data = {
        'paiement_id': 1,
        'amount': 500
    }

    # Ajouter un paiement avec succès
    paiement = contract_base.add_paiement(db_session, contract.contract_id, paiement_data)
    assert paiement is not None
    assert paiement.amount == Decimal('500')

    # Vérifier que le montant restant du contrat a été mis à jour
    updated_contract = db_session.query(Contract).filter_by(contract_id=contract.contract_id).first()
    assert updated_contract.remaining_amount == 500


def test_update_contract_success(contract_base, db_session):
    # Créer un contrat pour mettre à jour
    data = {
        'description': 'Test Contract',
        'total_amount': 1000,
        'remaining_amount': 1000,
        'customer_id': 1,
        'commercial_id': 1,
        'gestion_id': 1,
        'state': 'S',  # Utiliser le code de l'état comme une chaîne simple
        'paiement_state': 'N'  # Utiliser le code de l'état de paiement comme une chaîne simple
    }
    contract = contract_base.create_contract(db_session, data)

    # Mettre à jour le contrat
    update_data = {
        'description': 'Updated Contract'
    }
    contract_base.update_contract(contract.contract_id, update_data, db_session)

    # Vérifier que la mise à jour a été effectuée
    updated_contract = db_session.query(Contract).filter_by(contract_id=contract.contract_id).first()
    assert updated_contract.description == 'Updated Contract'


def test_signed_success(contract_base, db_session):
    # Créer un contrat pour le signer
    data = {
        'description': 'Test Contract',
        'total_amount': 1000,
        'remaining_amount': 1000,
        'customer_id': 1,
        'commercial_id': 1,
        'gestion_id': 1,
        'state': 'C',  # Utiliser le code de l'état comme une chaîne simple
        'paiement_state': 'N'  # Utiliser le code de l'état de paiement comme une chaîne simple
    }
    contract = contract_base.create_contract(db_session, data)

    # Signer le contrat
    contract_base.signed(contract.contract_id, db_session)

    # Vérifier que le contrat est marqué comme signé
    updated_contract = db_session.query(Contract).filter_by(contract_id=contract.contract_id).first()
    assert updated_contract.state == 'S'
