import unittest
from unittest.mock import patch, MagicMock
import os
import sys


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.user_view import UserView


class TestUserView(unittest.TestCase):

    @patch('views.user_view.questionary.select')
    def test_prompt_commercial(self, mock_select):
        mock_select.return_value.ask.return_value = 'Commercial1'
        all_commercials = ['Commercial1', 'Commercial2']
        result = UserView.prompt_commercial(all_commercials)
        mock_select.assert_called_once_with("Choix du commercial:", choices=all_commercials)
        self.assertEqual(result, 'Commercial1')

    @patch('views.user_view.questionary.select')
    def test_prompt_user(self, mock_select):
        mock_select.return_value.ask.return_value = 'User1'
        all_users = ['User1', 'User2']
        result = UserView.prompt_user(all_users)
        mock_select.assert_called_once_with("Sélectionnez un employé:", choices=all_users)
        self.assertEqual(result, 'User1')

    @patch('views.user_view.PromptView.prompt_select')
    def test_prompt_select_support(self, mock_prompt_select):
        mock_prompt_select.return_value = 'Support1'
        values = ['Support1', 'Support2']
        result = UserView.prompt_select_support(values)
        mock_prompt_select.assert_called_once_with("Choix du support:", values)
        self.assertEqual(result, 'Support1')

    @patch('views.user_view.questionary.confirm')
    def test_prompt_confirm_profil(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True
        result = UserView.prompt_confirm_profil()
        mock_confirm.assert_called_once_with("Souhaitez-vous modifier vos données ?", **{})
        self.assertTrue(result)

    @patch('views.user_view.questionary.text')
    @patch('views.user_view.regexformat', {'all_nospace': ['^[A-Za-z]+$', 'Invalid first name'], 'all_letters': ['^[A-Za-z]+$', 'Invalid last name']})
    def test_prompt_data_profil(self, mock_text, mock_regex):
        mock_text.side_effect = [MagicMock(ask=MagicMock(return_value='John')),
                                 MagicMock(ask=MagicMock(return_value='Doe'))]

        result = UserView.prompt_data_profil()

        mock_text.assert_any_call("Prénom:", validate=unittest.mock.ANY)
        mock_text.assert_any_call("Nom:", validate=unittest.mock.ANY)
        self.assertEqual(result, {'first_name': 'John', 'last_name': 'Doe'})

    @patch('views.user_view.questionary.password')
    @patch('views.user_view.regexformat', {'password': ['^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z]).{6,}$', 'Invalid password']})
    def test_prompt_password(self, mock_password, mock_regex):
        mock_password.side_effect = [MagicMock(ask=MagicMock(return_value='NewPassword')),
                                     MagicMock(ask=MagicMock(return_value='NewPassword'))]

        result = UserView.prompt_password()

        mock_password.assert_any_call("Mot de passe:", validate=unittest.mock.ANY)
        mock_password.assert_any_call("Confirmez le mot de passe:", validate=unittest.mock.ANY)
        self.assertEqual(result, {'password': 'NewPassword'})

    @patch('views.user_view.questionary.select')
    def test_prompt_role(self, mock_select):
        mock_select.return_value.ask.return_value = 'Admin'
        result = UserView.prompt_role()
        mock_select.assert_called_once_with("Role:", choices=['Admin', 'Commercial', 'Gestion', 'Support'])
        self.assertEqual(result, 'Admin')

    @patch('views.user_view.prompt_data_profil')
    def test_prompt_data_user(self, mock_prompt_data_profil):
        mock_prompt_data_profil.return_value = {'first_name': 'John', 'last_name': 'Doe'}
        result = UserView.prompt_data_user()
        mock_prompt_data_profil.assert_called_once()
        self.assertEqual(result, {'first_name': 'John', 'last_name': 'Doe'})

    @patch('views.user_view.prompt_role')
    def test_prompt_data_role(self, mock_prompt_role):
        mock_prompt_role.return_value = 'Manager'
        result = UserView.prompt_data_role()
        mock_prompt_role.assert_called_once()
        self.assertEqual(result, {'role': 'Manager'})

    @patch('views.user_view.console')
    def test_display_list_users(self, mock_console):
        # Mock instances for users
        User = MagicMock()
        User.return_value = MagicMock(
            last_name='Doe',
            first_name='John',
            epicuser_id=1,
            username='jdoe',
            email='jdoe@example.com',
            role=MagicMock(value='User'),
            state=MagicMock(value='Active')
        )
        all_users = [User(), User()]
        mock_console.pager = MagicMock()
        UserView.display_list_users(all_users, pager=False)
        mock_console.print.assert_called_once()  # Ensure print was called
        print("\nAppuyez sur Entrée pour continuer...")

    @patch('views.user_view.questionary.text')
    def test_prompt_update_user(self, mock_text):
        mock_text.side_effect = [MagicMock(ask=MagicMock(return_value='NewJohn')),
                                 MagicMock(ask=MagicMock(return_value='NewDoe')),
                                 MagicMock(ask=MagicMock(return_value='NewPassword'))]

        user = MagicMock()
        result = UserView.prompt_update_user(user)

        mock_text.assert_any_call("Nouveau Prénom (laisser vide pour ne pas changer):")
        mock_text.assert_any_call("Nouveau Nom (laisser vide pour ne pas changer):")
        mock_text.assert_any_call("Nouveau mot de passe (laisser vide pour ne pas changer):")
        self.assertEqual(result, ('NewJohn', 'NewDoe', 'NewPassword'))

    @patch('views.user_view.questionary.select')
    def test_prompt_select_gestion(self, mock_select):
        all_gestions = [MagicMock(first_name='John', last_name='Doe'),
                        MagicMock(first_name='Jane', last_name='Smith')]
        mock_select.return_value.ask.return_value = 'John Doe'

        result = UserView.prompt_select_gestion(all_gestions)

        mock_select.assert_called_once_with("Choix du gestionnaire:", choices=['John Doe', 'Jane Smith'])
        self.assertEqual(result.first_name, 'John')
        self.assertEqual(result.last_name, 'Doe')
