import time
import re
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich import box
import questionary
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from views.console_view import console, error_console


class MenuView:

    @classmethod
    def thinking(cls):
        time.sleep(30)

    @classmethod
    def show_waiting(cls, f):
        with console.status("Working...", spinner="circleQuarters"):
            f()

    @classmethod
    def menu_gestion(cls) -> Panel:
        menu_text = "    05-Liste des employés\n"
        menu_text += "    06-Créer un nouvel employé\n"
        menu_text += "    07-Modifier le role d'un employé\n"
        menu_text += "    08-Changer le statut actif/inactif d'un employé\n"
        menu_text += "    09-Créer un contrat\n"
        menu_text += "    10-Modifier un contrat\n"
        menu_text += "    11-Affecter un commercial à un client\n"
        menu_text += "    12-Affecter un support à un évènement"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Menu Gestion')
        return p

    @classmethod
    def menu_commercial(cls) -> Panel:
        menu_text = "    05-Créer un nouveau client\n"
        menu_text += "    06-Modifier les données d'un client\n"
        menu_text += "    07-Creer un évènement\n"
        menu_text += "    08-Effectuer une demande de création de contrat\n"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Menu commercial')
        return p

    @classmethod
    def menu_support(cls) -> Panel:
        menu_text = "    05-Liste des évènements qui me sont attribués\n"
        menu_text += "    06-Modifier les données d'un évènement\n"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Menu support')
        return p

    @classmethod
    def menu_role(cls, role) -> Panel:
        match role:
            case "G":
                menu = cls.menu_gestion()
            case "C":
                menu = cls.menu_commercial()
            case "S":
                menu = cls.menu_support()
            case _:
                menu = Panel("Menu not found")
        return menu

    @classmethod
    def menu_accueil(cls) -> Panel:
        menu_text = "    01-Voir mes données\n"
        menu_text += "    02-Liste des clients\n"
        menu_text += "    03-Liste des contrats\n"
        menu_text += "    04-Liste des évènements"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Accueil')
        return p

    @classmethod
    def menu_quit(cls) -> Panel:
        menu_text = "    D-Me déconnecter\n"
        menu_text += "    Q-Quitter l'application"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Quitter')
        return p

    @classmethod
    def menu_choice(cls, role):

        def ask_prompt():
            return questionary.text(
                "Que voulez-vous faire ?",
                validate=lambda text: True if re.match(r"[0-1][0-9]|D|Q", text)
                else "Votre choix est invalide").ask()

        def check_prompt(result):
            match role:
                case 'G': max_menu_idx = 13
                case 'C': max_menu_idx = 9
                case 'S': max_menu_idx = 7
            if result in ['D', 'Q']:
                return True
            elif int(result) <= max_menu_idx:
                return True
            else:
                return False

        console.print()
        menu = [cls.menu_accueil(), cls.menu_role(role), cls.menu_quit()]
        console.print(Columns(menu))

        result = ask_prompt()
        while not check_prompt(result):
            error_console.print('Votre choix est invalide')
            result = ask_prompt()

        return result

    @classmethod
    def menu_update_contract(cls, state):
        menu_text = [
            'Enregistrer un paiement']
        if state == 'C':
            menu_text.append('Modifier les données du contrat')
            menu_text.append('signé le contrat')
            menu_text.append('Annuler le contrat')
        choice = questionary.select(
                "Que voulez-vous faire ?",
                choices=menu_text,
            ).ask()
        if choice is None:
            raise KeyboardInterrupt
        return menu_text.index(choice) + 1
