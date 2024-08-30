import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.console_view import error_console


class ErrorView:
    """
    Classe pour gérer l'affichage des messages d'erreur.
    """
    @classmethod
    def display_error_exception(cls, text):
        """
        Affiche un message d'erreur général pour indiquer qu'une exception est survenue
        et fournit des détails sur l'erreur.

        Paramètres :
        ------------
        text (str) : Description de l'exception ou des détails sur l'erreur.
        """
        error_console.print('Une erreur est survenue dans le traitement')
        error_console.print(text)
