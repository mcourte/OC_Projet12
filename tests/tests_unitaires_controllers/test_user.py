import unittest
from unittest.mock import patch
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import EpicUser, Contract, Base
from controllers.user_controller import EpicUserBase
from config_test import generate_valid_token


class TestEpicBase(unittest.TestCase):

    def setUp(self):
        # Set up an in-memory SQLite database
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()

        self.current_user = EpicUser(
            username='mcourte',
            role='ADM',
            first_name='Magali',
            last_name='Courté',
            password='securepassword',
            email='mcourte@epic.com',
            state='A'
        )
        self.session.add(self.current_user)
        self.session.commit()
        self.valid_token = generate_valid_token('openclassroom_projet12', self.current_user.username)

    def test_invalid_user_role(self):
        with self.assertRaises(ValueError):
            EpicUser(
                role='InvalidRole',
                first_name='Pauline',
                last_name='Courant',
                username='pcourant',
                password='securepassword',
                email='pcourant@epic.com',
                state='A'
            )

    def test_user_with_contracts(self):
        user = EpicUser(
            role='COM',
            first_name='Marcelle',
            last_name='Celton',
            username='mcelton',
            password='securepassword',
            email='mcelton@epic.com',
            state='A'
        )
        self.session.add(user)
        self.session.commit()

        contract1 = Contract(
            description="Test Contract",
            total_amount=Decimal('1000.00'),
            remaining_amount=Decimal('1000.00'),
            state="C",
            customer_id=1,
            paiement_state="N",
            commercial_id=user.epicuser_id,
            gestion_id=3
        )
        contract2 = Contract(
            description="Test 2",
            total_amount=Decimal('1000.00'),
            remaining_amount=Decimal('1000.00'),
            state="C",
            customer_id=1,
            paiement_state="N",
            commercial_id=user.epicuser_id,
            gestion_id=3
        )
        self.session.add(contract1)
        self.session.add(contract2)
        self.session.commit()

        contracts = self.session.query(Contract).filter_by(commercial_id=user.epicuser_id).all()
        self.assertEqual(len(contracts), 2)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_set_activate_inactivate(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'username': 'jdoe', 'role': 'ADM'}

        # Add the user to be activated/inactivated
        user_to_modify = EpicUser(
            username='jdoe',
            role='COM',
            first_name='John',
            last_name='Doe',
            password='securepassword',
            email='jdoe@epic.com',
            state='A'
        )
        self.session.add(user_to_modify)
        self.session.commit()

        user_base = EpicUserBase(self.session, self.current_user)
        user_base.set_activate_inactivate(self.session, 'jdoe')

        updated_user = self.session.query(EpicUser).filter_by(username='jdoe').first()
        self.assertEqual(updated_user.state, 'I')
