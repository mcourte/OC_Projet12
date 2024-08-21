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
    def display_error_login(cls):
        """
        Affiche un message d'erreur lorsque l'utilisateur ou le mot de passe est inconnu.
        """
        error_console.print('ERROR : Utilisateur ou mot de passe inconnu')

    @classmethod
    def display_token_expired(cls):
        """
        Affiche un message d'erreur indiquant que le token a expiré et fournit des instructions pour se reconnecter.
        """
        s = 'ERROR : Token expiré ! Veuillez vous reconnecter.\n'
        s += 'Commande : python epicevent.py login'
        error_console.print(s)

    @classmethod
    def display_token_invalid(cls):
        """
        Affiche un message d'erreur lorsque le token est invalide.
        """
        error_console.print('ERROR : Token invalide ! Veuillez vous reconnecter.')

    @classmethod
    def display_not_commercial(cls):
        """
        Affiche un message d'erreur lorsque l'accès est refusé en raison d'un rôle commercial requis.
        """
        error_console.print('ERROR : Accès refusé, rôle commercial requis.')

    @classmethod
    def display_not_manager(cls):
        """
        Affiche un message d'erreur lorsque l'accès est refusé en raison d'un rôle manager requis.
        """
        error_console.print('ERROR : Accès refusé, rôle manager requis.')

    @classmethod
    def display_not_support(cls):
        """
        Affiche un message d'erreur lorsque l'accès est refusé en raison d'un rôle support requis.
        """
        error_console.print('ERROR : Accès refusé, rôle support requis.')

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
