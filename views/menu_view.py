import time
import re
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich import box
from rich.text import Text
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
    """
    Classe pour gérer l'affichage des menus et les interactions avec l'utilisateur.
    """

    @classmethod
    def thinking(cls):
        """
        Simule un traitement en attente pendant 30 secondes.
        """
        time.sleep(30)

    @classmethod
    def show_waiting(cls, f):
        """
        Affiche un indicateur de chargement pendant l'exécution de la fonction passée en argument.

        Args:
            f (function): Fonction à exécuter pendant l'affichage de l'indicateur de chargement.
        """
        with console.status("Working...", spinner="circleQuarters"):
            f()

    @classmethod
    def menu_gestion(cls) -> Panel:
        """
        Crée et retourne le menu de gestion.

        Returns:
            Panel: Menu de gestion formaté.
        """
        menu_text = "    07-Liste des employés triées\n"
        menu_text += "    08-Créer un nouvel employé\n"
        menu_text += "    09-Changer le statut actif/inactif d'un employé\n"
        menu_text += "    10-Créer un contrat\n"
        menu_text += "    11-Modifier un contrat\n"
        menu_text += "    12-Affecter un commercial à un client\n"
        menu_text += "    13-Affecter un gestionnaire à un contrat\n"
        menu_text += "    14-Affecter un support à un évènement"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Menu Gestion')
        return p

    @classmethod
    def menu_admin(cls) -> Panel:
        """
        Crée et retourne le menu de admin.

        Returns:
            Panel: Menu de gestion formaté.
        """
        menu_text = "    07-Liste des employés triée\n"
        menu_text += "    08-Créer un nouvel employé\n"
        menu_text += "    09-Changer le statut actif/inactif d'un employé\n"
        menu_text += "    10-Créer un contrat\n"
        menu_text += "    11-Modifier un contrat\n"
        menu_text += "    11-Affecter un commercial à un client\n"
        menu_text += "    13-Affecter un gestionnaire à un contrat\n"
        menu_text += "    14-Affecter un support à un évènement\n"
        menu_text += "    15-Créer un nouveau client\n"
        menu_text += "    16-Modifier les données d'un client\n"
        menu_text += "    17-Créer un évènement\n"
        menu_text += "    18-Modifier un évènement\n"
        menu_text += "    19-Lister évènement\n"
        menu_text += "    20-Lister contracts\n"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Menu Admin')
        return p

    @classmethod
    def menu_commercial(cls) -> Panel:
        """
        Crée et retourne le menu commercial.

        Returns:
            Panel: Menu commercial formaté.
        """
        menu_text = "    07-Créer un nouveau client\n"
        menu_text += "    08-Modifier les données d'un client\n"
        menu_text += "    09-Créer un évènement\n"
        menu_text += "    10-Effectuer une demande de création de contrat\n"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Menu Commercial')
        return p

    @classmethod
    def menu_support(cls) -> Panel:
        """
        Crée et retourne le menu support.

        Returns:
            Panel: Menu support formaté.
        """
        menu_text = "    07-Liste des évènements qui me sont attribués\n"
        menu_text += "    08-Modifier les données d'un évènement\n"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Menu Support')
        return p

    @classmethod
    def menu_role(cls, role) -> Panel:
        """
        Retourne le menu correspondant au rôle spécifié.

        Args:
            role (str): Le rôle de l'utilisateur ('G', 'C', 'S').

        Returns:
            Panel: Menu correspondant au rôle.
        """
        match role:
            case "GES":
                menu = cls.menu_gestion()
            case "COM":
                menu = cls.menu_commercial()
            case "SUP":
                menu = cls.menu_support()
            case "ADM":
                menu = cls.menu_admin()
            case _:
                menu = Panel("Menu non trouvé")
        return menu

    @classmethod
    def menu_accueil(cls) -> Panel:
        """
        Crée et retourne le menu d'accueil.

        Returns:
            Panel: Menu d'accueil formaté.
        """
        menu_text = "    01-Voir mes données\n"
        menu_text += "    02-Mettre à jour mes données\n"
        menu_text += "    03-Liste des clients\n"
        menu_text += "    04-Liste des contrats\n"
        menu_text += "    05-Liste des évènements\n"
        menu_text += "    06-Liste des utilisateurs"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Accueil')
        return p

    @classmethod
    def menu_quit(cls) -> Panel:
        """
        Crée et retourne le menu de déconnexion et de quitter.

        Returns:
            Panel: Menu de déconnexion et de quitter formaté.
        """
        menu_text = "    Q-Quitter l'application"
        p = Panel(
            Align.left(menu_text, vertical='top'),
            box=box.ROUNDED,
            title_align='left',
            title='Quitter')
        return p

    @classmethod
    def menu_choice(cls, role):
        """
        Affiche les menus disponibles en fonction du rôle de l'utilisateur et demande une sélection.

        Args:
            role (str): Le rôle de l'utilisateur ('G', 'C', 'S').

        Returns:
            str: Le choix de l'utilisateur.
        """
        def ask_prompt():
            """
            Demande à l'utilisateur ce qu'il souhaite faire et valide l'entrée.

            Returns:
                str: Réponse de l'utilisateur.
            """
            return questionary.text(
                "Que voulez-vous faire ?",
                validate=lambda text: True if re.match(r"[0-1][0-9]|D|Q", text)
                else "Votre choix est invalide").ask()

        def check_prompt(result):
            """
            Vérifie si le choix de l'utilisateur est valide.

            Args:
                result (str): Choix de l'utilisateur.

            Returns:
                bool: True si le choix est valide, sinon False.
            """
            match role:
                case 'GES': max_menu_idx = 14
                case 'ADM': max_menu_idx = 30
                case 'COM': max_menu_idx = 10
                case 'SUP': max_menu_idx = 8
            if result == 'Q':
                return True
            elif int(result) <= max_menu_idx:
                return True
            else:
                return False
        text = "Menu du CRM d'EpicEvents"
        panel = Panel(Text(text, justify="center", style="bold blue"))
        console.print(panel)
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
        """
        Affiche le menu pour la mise à jour d'un contrat en fonction de son état et demande une sélection.

        Args:
            state (str): L'état actuel du contrat.

        Returns:
            int: L'index du choix sélectionné (1 pour "Enregistrer un paiement",
            2 pour "Modifier les données du contrat", etc.).
        """
        menu_text = [
            'Enregistrer un paiement']
        menu_text.append('Modifier les données du contrat')
        menu_text.append('Signer le contrat')
        choice = questionary.select("Que voulez-vous faire ?",
                                    choices=menu_text).ask()
        if choice is None:
            raise KeyboardInterrupt
        return menu_text.index(choice) + 1
