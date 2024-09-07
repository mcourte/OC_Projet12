import sys
import os
from unittest.mock import MagicMock
import unittest
import pytest
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.event_controller import Event, EventBase
from config_test import generate_valid_token
from models.entities import EpicUser


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

    @pytest.mark.unit
    def test_create_event(setup_event):
        session, current_user, valid_token = setup_event

        # Appelez la fonction pour créer un événement
        event = EventBase.create_event(session, valid_token, 'Test Event')

        # Assertions
        assert event is not None
        assert event.name == 'Test Event'
