import sys
import os
from unittest.mock import MagicMock, patch
import unittest
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.event_controller import EventBase
from config_test import generate_valid_token


class TestEventBase(unittest.TestCase):

    def setUp(self):
        # Mock de la session SQLAlchemy
        self.session = MagicMock()

        # Exemple de correction dans le setUp de votre test
        self.current_user = {
            'username': 'mcourte',
            'role': 'ADM'
        }
        self.valid_token = generate_valid_token('openclassroom_projet12', self.current_user)

    def setup_event(self):
        session = MagicMock()
        current_user = MagicMock()
        valid_token = "some_valid_token"
        return (session, current_user, valid_token)

    def test_create_event(self):
        session = MagicMock()

        # Générer un token JWT valide
        valid_token = generate_valid_token('openclassroom_projet12', 'testuser')

        data = {
            'title': 'Réunion annuelle',
            'description': 'Réunion annuelle de l\'entreprise',
            'location': 'Paris',
            'attendees': 50,
            'date_started': '2024-09-06',
            'date_ended': '2024-09-06',
            'contract_id': 1,
            'customer_id': 2,
            'support_id': 3
        }

        # Injecter le token valide dans le contexte du test
        with patch('controllers.session.decode_token', return_value=valid_token):
            event = EventBase.create_event(data, session)

        # Assertion sur la création de l'événement
        self.assertIsNotNone(event)
