import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import unittest

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from models.entities import Event
from controllers.event_controller import EventBase


class TestEventBase(unittest.TestCase):

    @patch('views.console_view.console')
    @patch('models.entities.Event')
    def test_create_event(self, mock_event, mock_console):
        session_mock = MagicMock()
        event_base = EventBase(session_mock)

        # Simule les données de l'événement
        data = {
            'title': 'New Event',
            'description': 'Event Description',
            'location': 'Event Location',
            'attendees': 100,
            'date_started': '2024-09-10',
            'date_ended': '2024-09-11',
            'contract_id': 1,
            'customer_id': 2,
            'support_id': 3
        }

        # Crée un mock pour l'événement
        event_mock = MagicMock()
        mock_event.return_value = event_mock

        # Appelle la méthode create_event
        result = event_base.create_event(data, session_mock)

        # Vérifie que l'événement a été créé avec les bonnes valeurs
        mock_event.assert_called_once_with(
            title='New Event',
            description='Event Description',
            location='Event Location',
            attendees=100,
            date_started='2024-09-10',
            date_ended='2024-09-11',
            contract_id=1,
            customer_id=2,
            support_id=3
        )

        # Vérifie que l'événement a été ajouté à la session et commit
        session_mock.add.assert_called_once_with(event_mock)
        session_mock.commit.assert_called_once()

        # Vérifie que le résultat est bien l'événement créé
        self.assertEqual(result, event_mock)

    @patch('views.console_view.console')
    @patch('models.entities.Event')
    def test_update_event_success(self, mock_event, mock_console):
        session_mock = MagicMock()
        event_base = EventBase(session_mock)

        # Simule l'événement existant
        existing_event_mock = MagicMock()
        session_mock.query().filter_by().first.return_value = existing_event_mock

        # Simule les nouvelles données de l'événement
        data = {
            'title': 'Updated Event',
            'description': 'Updated Description',
            'location': 'Updated Location',
            'attendees': 150
        }

        # Appelle la méthode update_event
        event_base.update_event(1, data)

        # Vérifie que les attributs de l'événement ont été mis à jour
        self.assertEqual(existing_event_mock.title, 'Updated Event')
        self.assertEqual(existing_event_mock.description, 'Updated Description')
        self.assertEqual(existing_event_mock.location, 'Updated Location')
        self.assertEqual(existing_event_mock.attendees, 150)

        # Vérifie que la session a été commit
        session_mock.commit.assert_called_once()

        # Vérifie que le message de succès a été imprimé
        mock_console.print.assert_called_once_with("L'événement a bien été mis à jour.", style="bold green")

    @patch('models.entities.Event')
    def test_update_event_not_found(self, mock_event):
        session_mock = MagicMock()
        event_base = EventBase(session_mock)

        # Simule qu'aucun événement n'a été trouvé
        session_mock.query().filter_by().first.return_value = None

        # Vérifie que l'appel de update_event avec un ID inexistant lève une ValueError
        with self.assertRaises(ValueError):
            event_base.update_event(999, {'title': 'Nonexistent Event'})

        # Vérifie que la session n'a pas été commit en cas d'erreur
        session_mock.commit.assert_not_called()
