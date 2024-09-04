import pytest
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.contract_controller import ContractBase
from models.entities import EpicUser, Contract, Paiement
from views import console_view


class TestContractBase(unittest.TestCase):

    def setUp(self):
        # Mock pour la session SQLAlchemy
        self.session = MagicMock()

        # Mock pour l'utilisateur actuel
        self.current_user = MagicMock(spec=EpicUser)

        # Instance de la classe ContractBase
        self.contract_base = ContractBase(self.session, self.current_user)

    @patch('views.console_view.console')
    def test_create_contract_success(self, mock_console):
        # Données d'entrée
        data = {
            'description': 'Test contract',
            'total_amount': Decimal('1000.00'),
            'remaining_amount': Decimal('1000.00'),
            'state': 'C',
            'customer_id': 1,
            'paiement_state': 'N',
            'commercial_id': 2
        }

        # Appel de la méthode
        contract = self.contract_base.create_contract(self.session, data)

        # Vérifications
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(contract, Contract)
        self.assertEqual(contract.description, 'Test contract')
        self.assertEqual(contract.total_amount, Decimal('1000.00'))

    def test_update_contract_success(self):
        # Mock du contrat existant
        contract = MagicMock(spec=Contract)
        self.session.query().filter_by().first.return_value = contract

        # Données de mise à jour
        data = {'description': 'Updated contract'}

        # Appel de la méthode
        self.contract_base.update_contract(1, data, self.session)

        # Vérifications
        self.assertEqual(contract.description, 'Updated contract')
        self.session.commit.assert_called_once()

    def test_update_contract_not_found(self):
        # Mock du contrat non trouvé
        self.session.query().filter_by().first.return_value = None

        # Vérifications
        with self.assertRaises(ValueError):
            self.contract_base.update_contract(1, {'description': 'Updated contract'}, self.session)

    @patch('views.console_view.console')
    def test_add_paiement_success(self, mock_console):
        # Mock du contrat existant
        contract = MagicMock(spec=Contract)
        contract.remaining_amount = Decimal('1000.00')
        self.session.query().filter_by().first.side_effect = [None, contract]

        # Données d'entrée
        data = {'paiement_id': 1, 'amount': '500.00'}

        # Appel de la méthode
        self.contract_base.add_paiement(self.session, 1, data)

        # Vérifications
        self.session.add.assert_called()
        self.session.commit.assert_called_once()
        self.assertEqual(contract.remaining_amount, Decimal('500.00'))

    def test_add_paiement_duplicate_error(self):
        # Mock d'un paiement déjà existant
        paiement = MagicMock(spec=Paiement)
        self.session.query().filter_by().first.return_value = paiement

        # Données d'entrée
        data = {'paiement_id': 1, 'amount': '500.00'}

        # Vérifications
        with self.assertRaises(ValueError):
            self.contract_base.add_paiement(self.session, 1, data)
        self.session.rollback.assert_called_once()

    @patch('views.console_view.console')
    def test_signed_success(self, mock_console):
        # Mock du contrat existant
        contract = MagicMock(spec=Contract)
        self.session.query().filter_by().first.return_value = contract

        # Appel de la méthode
        self.contract_base.signed(self.session, 1)

        # Vérifications
        self.assertEqual(contract.state, 'S')
        self.session.commit.assert_called_once()

    def test_signed_contract_not_found(self):
        # Mock du contrat non trouvé
        self.session.query().filter_by().first.return_value = None

        # Vérifications
        with self.assertRaises(ValueError):
            self.contract_base.signed(self.session, 1)

    @patch('views.console_view.console')
    def test_update_gestion_contract_success(self, mock_console):
        # Mock du contrat existant
        contract = MagicMock(spec=Contract)
        self.session.query().filter_by().first.return_value = contract

        # Appel de la méthode
        self.contract_base.update_gestion_contract(self.current_user, self.session, 1, 2)

        # Vérifications
        self.assertEqual(contract.gestion_id, 2)
        self.session.commit.assert_called_once()

    def test_update_gestion_contract_not_found(self):
        # Mock du contrat non trouvé
        self.session.query().filter_by().first.return_value = None

        # Vérifications
        with self.assertRaises(ValueError):
            self.contract_base.update_gestion_contract(self.current_user, self.session, 1, 2)
