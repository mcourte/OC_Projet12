import os
import sys
import unittest
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from rich.console import Console
from rich import box

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.event_view import EventView


class TestEventView(unittest.TestCase):

    @patch.object(Console, 'print')
    @patch('views.event_view.Table', autospec=True)
    def test_display_list_events(self, mock_table, mock_print):
        mock_event = MagicMock()
        mock_event.event_id = 1
        mock_event.title = 'Event Title'
        mock_event.location = 'Event Location'
        mock_event.attendees = 50
        mock_event.date_started = datetime(2024, 1, 1)
        mock_event.date_ended = datetime(2024, 1, 2)
        mock_event.customer_id = 'Customer123'
        mock_event.support_id = 'Support123'
        all_events = [mock_event]

        # Appel de la méthode
        EventView.display_list_events(all_events)

        # Vérifiez que print est appelé le nombre attendu de fois
        self.assertEqual(mock_print.call_count, 2)  # Ajustez selon le comportement attendu

        # Vérifiez les autres appels de la méthode comme avant
        mock_table.assert_called_once_with(
            title="Liste des Evènements",
            box=box.SQUARE,
            title_justify="center",
            title_style="bold blue"
        )

    @pytest.mark.unit
    @patch('questionary.text')
    def test_prompt_data_event(self, mock_text):
        title = 'Titre'
        description = 'des'
        location = 'Rennes'
        attendees = '10'
        date_started = '24/10/2024'
        date_ended = '25/10/2024'
        result = {title, description, location, attendees, date_started, date_ended}

        result = EventView.prompt_data_event()

        assert result == result

    @patch('questionary.select')
    @patch.object(Console, 'print')
    def test_prompt_select_event(self, mock_print, mock_select):
        # Création d'un mock pour les évènements
        mock_event = MagicMock()
        mock_event.event_id = 1
        mock_event.title = 'Event Title'
        all_events = [mock_event]

        # Configurer le mock select pour retourner une valeur
        mock_select.return_value.ask.return_value = '1 Event Title'

        result = EventView.prompt_select_event(all_events)

        self.assertEqual(result, mock_event)

    @patch('questionary.select')
    @patch.object(Console, 'print')
    def test_prompt_select_contract(self, mock_print, mock_select):
        # Création d'un mock pour les contrats
        mock_contract = MagicMock()
        mock_contract.contract_id = 101
        mock_contract.description = 'Contract Description'
        all_contracts = [mock_contract]

        # Configurer le mock select pour retourner une valeur
        mock_select.return_value.ask.return_value = '101 Contract Description'

        result = EventView.prompt_select_contract(all_contracts)

        self.assertEqual(result, mock_contract)

    @patch('questionary.select')
    def test_prompt_select_statut(self, mock_select):
        # Définir des états fictifs pour les tests
        EventView.CONTRACT_STATES = [
            ('active', 'Actif'),
            ('inactive', 'Inactif')
        ]

        # Configurer le mock select pour retourner une valeur
        mock_select.return_value.ask.return_value = 'active Actif'

        result = EventView.prompt_select_statut()

        self.assertEqual(result, 'active')

    @patch('questionary.confirm')
    def test_prompt_add_support(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = EventView.prompt_add_support()

        self.assertTrue(result)

    @patch('questionary.confirm')
    def test_prompt_filtered_events_gestion(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = EventView.prompt_filtered_events_gestion()

        self.assertTrue(result)

    @patch('questionary.confirm')
    def test_prompt_filtered_events_support(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = EventView.prompt_filtered_events_support()

        self.assertTrue(result)
