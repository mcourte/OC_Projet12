import os
import pytest

# Sauvegarder la valeur actuelle de DATABASE_URL
original_database_url = os.getenv('DATABASE_URL')

# Définir l'URL pour les tests
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:password@localhost:5432/app_db'


import unittest
from unittest.mock import patch, MagicMock
from controllers.database_controller import EpicDatabase
from sqlalchemy_utils.functions import database_exists
from views.authentication_view import AuthenticationView
from controllers.user_controller import EpicUserBase

class TestEpicDatabase(unittest.TestCase):

    @patch('controllers.database_controller.EpicDatabase.database_exists')
    @patch('views.authentication_view.AuthenticationView.display_database_connection')
    def test_database_connection_existing(self, mock_display_connection, mock_database_exists):
        # Mock database_exists to return True
        mock_database_exists.return_value = True

        db = EpicDatabase('test_db', 'localhost', 'user', 'password')
        mock_database_exists.assert_called_once()
        mock_display_connection.assert_called_once_with('test_db')

    @patch('controllers.database_controller.EpicDatabase.database_exists')
    def test_database_connection_non_existing(self, mock_database_exists):
        # Mock database_exists to return False
        mock_database_exists.return_value = False

        with patch('builtins.print') as mock_print:
            db = EpicDatabase('test_db', 'localhost', 'user', 'password')
            mock_print.assert_called_once_with('erreur')

    @patch('controllers.database_controller.EpicDatabase.create_database')
    @patch('controllers.database_controller.EpicDatabase.Base.metadata.create_all')
    @patch('controllers.user_controller.EpicUserBase')
    def test_database_creation(self, MockEpicUserBase, mock_create_all, mock_create_database):
        # Mock classes and methods
        mock_create_database.return_value = None
        mock_session = MagicMock()
        MockEpicUserBase.return_value = MagicMock()

        db = EpicDatabase('test_db', 'localhost', 'user', 'password')
        db.first_initdb = MagicMock()

        db.database_creation('admin_user', 'admin_password')

        mock_create_database.assert_called_once()
        mock_create_all.assert_called_once()
        db.first_initdb.assert_called_once_with('admin_user', 'admin_password')

    @patch('controllers.user_controller.EpicUserBase')
    def test_authenticate_user_success(self, MockEpicUserBase):
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        MockEpicUserBase.return_value.get_user.return_value = mock_user

        db = EpicDatabase('test_db', 'localhost', 'user', 'password')
        result = db.authenticate_user('username', 'password')
        self.assertTrue(result)
        self.assertEqual(db.user, mock_user)

    @patch('controllers.user_controller.EpicUserBase')
    def test_authenticate_user_failure(self, MockEpicUserBase):
        MockEpicUserBase.return_value.get_user.return_value = None

        db = EpicDatabase('test_db', 'localhost', 'user', 'password')
        result = db.authenticate_user('username', 'password')
        self.assertFalse(result)
        self.assertIsNone(db.user)

    @patch('controllers.user_controller.EpicUser.find_by_username')
    @patch('views.authentication_view.AuthenticationView.display_database_connection')
    def test_check_connection_success(self, mock_display_connection, MockFindByUsername):
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        MockFindByUsername.return_value = mock_user

        db = EpicDatabase('test_db', 'localhost', 'user', 'password')
        result = db.check_connection('username', 'password')
        self.assertEqual(result, mock_user)
        mock_display_connection.assert_called_once_with('test_db')

    @patch('controllers.user_controller.EpicUser.find_by_username')
    def test_check_connection_failure(self, MockFindByUsername):
        MockFindByUsername.return_value = None

        db = EpicDatabase('test_db', 'localhost', 'user', 'password')
        result = db.check_connection('username', 'password')
        self.assertIsNone(result)
