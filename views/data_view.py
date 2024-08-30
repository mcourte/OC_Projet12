import os
import sys
from rich.panel import Panel
from rich import box
from rich.align import Align

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from views.console_view import console


class DataView:
    """
    Classe pour gérer l'affichage des messages et des données.
    """

    @classmethod
    def display_workflow(cls):
        """
        Affiche un message indiquant la mise à jour du workflow.
        """
        console.print('Mise à jour du workflow')

    @classmethod
    def display_nocontracts(cls):
        """
        Affiche un message indiquant qu'aucun contrat n'a été trouvé.
        """
        console.print('Aucun contrat trouvé')

    @classmethod
    def display_interupt(cls):
        """
        Affiche un message indiquant que l'opération a été abandonnée.
        """
        console.print('Opération abandonnée')

    @classmethod
    def display_data_update(cls):
        """
        Affiche un message indiquant que les modifications ont été enregistrées.
        """
        console.print('Vos modifications ont été enregistrées')

    @classmethod
    def display_profil(cls, e):
        """
        Affiche les informations de profil d'un utilisateur.

        :param e: Instance de l'utilisateur dont les informations doivent être affichées.
        :type e: User
        """
        text = f'Prénom: {e.first_name}\n'
        text += f'Nom: {e.last_name}\n'
        text += f'Email: {e.email}\n' if e.email else 'Email: \n'
        text += f'Rôle: {e.role.value}\n'
        text += f'État: {e.state.value}\n'
        p = Panel(
            Align.center(text, vertical='bottom'),
            box=box.ROUNDED,
            style='cyan',
            title_align='center',
            title='Mes informations')
        console.print(p)
