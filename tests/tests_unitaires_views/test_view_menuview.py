import io
import pytest
from unittest.mock import patch
from rich.panel import Panel
from rich.align import Align
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.menu_view import MenuView


def extract_text(renderable):
    if isinstance(renderable, Panel):
        return str(renderable.renderable)
    return str(renderable)


def test_menu_gestion():
    panel = MenuView.menu_gestion()
    assert panel.title == 'Menu Gestion'
    assert 'Créer un nouvel employé' in extract_text(panel.renderable)


def test_menu_commercial():
    panel = MenuView.menu_commercial()
    assert panel.title == 'Menu Commercial'
    assert 'Créer un nouveau client' in extract_text(panel.renderable)


def test_menu_support():
    panel = MenuView.menu_support()
    assert panel.title == 'Menu Support'
    assert 'Liste des évènements qui me sont attribués' in extract_text(panel.renderable)


def test_menu_accueil():
    panel = MenuView.menu_accueil()
    assert panel.title == 'Accueil'
    assert 'Voir mes données' in extract_text(panel.renderable)


def test_menu_quit():
    panel = MenuView.menu_quit()
    assert panel.title == 'Quitter'
    assert 'Me déconnecter' in extract_text(panel.renderable)


def test_menu_role():
    with patch('views.menu_view.MenuView.menu_gestion') as mock_menu_gestion:
        mock_menu_gestion.return_value = Panel(Align.left("Gestion Menu", vertical='top'))
        assert 'Gestion Menu' in extract_text(MenuView.menu_role('G').renderable)

    with patch('views.menu_view.MenuView.menu_commercial') as mock_menu_commercial:
        mock_menu_commercial.return_value = Panel(Align.left("Commercial Menu", vertical='top'))
        assert 'Commercial Menu' in extract_text(MenuView.menu_role('C').renderable)

    with patch('views.menu_view.MenuView.menu_support') as mock_menu_support:
        mock_menu_support.return_value = Panel(Align.left("Support Menu", vertical='top'))
        assert 'Support Menu' in extract_text(MenuView.menu_role('S').renderable)


@patch('questionary.text')
@patch('views.menu_view.console.print')
def test_menu_choice(mock_console_print, mock_questionary_text):
    mock_questionary_text.return_value.ask.return_value = '05'
    result = MenuView.menu_choice('G')
    assert result == '05'
    mock_questionary_text.assert_called_once()


@patch('questionary.select')
def test_menu_update_contract(mock_questionary_select):
    mock_questionary_select.return_value.ask.return_value = 'Enregistrer un paiement'
    result = MenuView.menu_update_contract('C')
    assert result == 1
    mock_questionary_select.assert_called_once()


@patch('time.sleep', return_value=None)
def test_thinking(mock_sleep):
    instance = MenuView()
    instance.thinking()
    mock_sleep.assert_called_once_with(30)
