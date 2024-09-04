import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import unittest
# Add the root directory to PYTHONPATH
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.insert(0, parent_dir)

# Import the necessary modules
from controllers.user_controller import EpicUserBase


class TestEpicUserBase(unittest.TestCase):

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    def test_set_activate_inactivate(self, mock_epic_user, mock_console):
        session_mock = MagicMock()
        epic_user_base = EpicUserBase(session_mock)

        user_mock = MagicMock(state='A', username='test_user', role='COM')
        session_mock.query().filter_by().first.return_value = user_mock

        epic_user_base.set_activate_inactivate(session_mock, 'test_user')

        self.assertEqual(user_mock.state, 'I')
        mock_console.print.assert_called_with(
            "test_user est Inactif.Veuillez réaffecter les Contrats/Clients/Evènement qui lui sont associés"
        )
        session_mock.commit.assert_called_once()

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    def test_create_user_success(self, mock_epic_user, mock_console):
        session_mock = MagicMock()
        data_profil = {
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'securepassword',
            'role': 'Commercial'
        }

        mock_epic_user.generate_unique_username.return_value = 'johndoe'
        mock_epic_user.generate_unique_email.return_value = 'johndoe@example.com'

        user_mock = MagicMock()
        session_mock.query().filter_by().first.return_value = None
        mock_epic_user.return_value = user_mock

        result = EpicUserBase.create_user(session_mock, data_profil)

        mock_epic_user.assert_called_once_with(
            first_name='John',
            last_name='Doe',
            username='johndoe',
            email='johndoe@example.com',
            role='COM'
        )
        user_mock.set_password.assert_called_once_with('securepassword')
        session_mock.add.assert_called_once_with(user_mock)
        session_mock.commit.assert_called_once()
        self.assertEqual(result, user_mock)

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    def test_update_user(self, mock_epic_user, mock_console):
        session_mock = MagicMock()
        epic_user_base = EpicUserBase(session_mock)

        user_mock = MagicMock()
        session_mock.query().filter_by().first.return_value = user_mock

        epic_user_base.update_user(session_mock, 'johndoe', password='newpassword')

        user_mock.set_password.assert_called_once_with('newpassword')
        session_mock.commit.assert_called_once()

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    @patch('views.user_view.UserView.prompt_user')
    def test_reassign_customers(self, mock_prompt_user, mock_epic_user, mock_console):
        session_mock = MagicMock()
        epic_user_base = EpicUserBase(session_mock)

        user_mock = MagicMock(epicuser_id=1, username='old_user')
        new_commercial_mock = [MagicMock(username='new_user')]
        session_mock.query().filter_by().all.return_value = new_commercial_mock

        mock_prompt_user.return_value = 'new_user'
        chosen_user_mock = MagicMock(epicuser_id=2)
        session_mock.query().filter_by().first.return_value = chosen_user_mock

        customers_mock = [MagicMock()]
        session_mock.query().filter_by().all.return_value = customers_mock

        epic_user_base.reassign_customers(session_mock, user_mock)

        for customer in customers_mock:
            self.assertEqual(customer.commercial_id, chosen_user_mock.epicuser_id)
        session_mock.commit.assert_called_once()
        mock_console.print.assert_called_with("Réaffectation des clients du commercial inactif terminée.", style="bold green")

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    @patch('views.user_view.UserView.prompt_user')
    def test_reassign_contracts(self, mock_prompt_user, mock_epic_user, mock_console):
        session_mock = MagicMock()
        epic_user_base = EpicUserBase(session_mock)

        user_mock = MagicMock(epicuser_id=1, username='old_user')
        new_gestion_mock = [MagicMock(username='new_user')]
        session_mock.query().filter_by().all.return_value = new_gestion_mock

        mock_prompt_user.return_value = 'new_user'
        chosen_user_mock = MagicMock(epicuser_id=2)
        session_mock.query().filter_by().first.return_value = chosen_user_mock

        contracts_mock = [MagicMock()]
        session_mock.query().filter_by().all.return_value = contracts_mock

        epic_user_base.reassign_contracts(session_mock, user_mock)

        for contract in contracts_mock:
            self.assertEqual(contract.gestion_id, chosen_user_mock.epicuser_id)
        session_mock.commit.assert_called_once()
        mock_console.print.assert_called_with("Réaffectation des contrats du gestionnaire inactif terminée.")

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    @patch('views.user_view.UserView.prompt_user')
    def test_reassign_events(self, mock_prompt_user, mock_epic_user, mock_console):
        session_mock = MagicMock()
        epic_user_base = EpicUserBase(session_mock)

        user_mock = MagicMock(epicuser_id=1, username='old_user')
        new_support_mock = [MagicMock(username='new_user')]
        session_mock.query().filter_by().all.return_value = new_support_mock

        mock_prompt_user.return_value = 'new_user'
        chosen_user_mock = MagicMock(epicuser_id=2)
        session_mock.query().filter_by().first.return_value = chosen_user_mock

        events_mock = [MagicMock()]
        session_mock.query().filter_by().all.return_value = events_mock

        epic_user_base.reassign_events(session_mock, user_mock)

        for event in events_mock:
            self.assertEqual(event.support_id, chosen_user_mock.epicuser_id)
        session_mock.commit.assert_called_once()
        mock_console.print.assert_called_with("Réaffectation des évènements du gestionnaire inactif terminée.")

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    def test_delete_user(self, mock_epic_user, mock_console):
        session_mock = MagicMock()
        epic_user_base = EpicUserBase(session_mock)

        user_mock = MagicMock(epicuser_id=1, username='test_user', role=MagicMock(code='COM'))
        session_mock.query().filter_by().first.return_value = user_mock

        with patch.object(epic_user_base, 'reassign_customers') as mock_reassign_customers:
            result = epic_user_base.delete_user(session_mock, 'test_user')

            mock_reassign_customers.assert_called_once_with(session_mock, user_mock)
            session_mock.delete.assert_called_once_with(user_mock)
            session_mock.commit.assert_called_once()
            mock_console.print.assert_called_with("L'utilisateur 'test_user' (ID 1) a été supprimé avec succès.", style="bold green")
            self.assertTrue(result)
