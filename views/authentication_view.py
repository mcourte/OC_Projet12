import questionary
from .console_view import console


class AuthenticationView:
    """
    Classe pour gérer l'affichage des vues liées à l'authentification et à la configuration de la base de données.
    """

    @classmethod
    def display_logout(cls) -> None:
        """
        Affiche un message indiquant que l'utilisateur est déconnecté.
        """
        text = "Vous êtes déconnecté"
        console.print(text)

    @classmethod
    def display_welcome(cls, username) -> None:
        """
        Affiche un message de bienvenue à l'utilisateur.

        :param username: Le nom d'utilisateur à inclure dans le message de bienvenue.
        :type username: str
        """
        text = f"!!! Bienvenue {username} sur le CRM de EpicEvent !!!"
        console.print(text, justify="center", style="bold blue")

    @staticmethod
    def prompt_login(**kwargs):
        """
        Demande à l'utilisateur de saisir un identifiant et un mot de passe pour se connecter.

        :param kwargs: Arguments supplémentaires pour les fonctions questionary.text et questionary.password.
        :return: Un tuple contenant l'identifiant et le mot de passe saisis par l'utilisateur.
        :rtype: tuple
        """
        text = "Pour vous connecter au CRM d'EpicEvents, merci de rentrer votre nom d'utilisateur et votre mot de passe"
        console.print(text, justify="center", style="bold blue")
        username = questionary.text("Identifiant:").ask()
        password = questionary.password("Mot de passe:").ask()
        return username, password

    @classmethod
    def display_database_connection(cls, name):
        """
        Affiche un message indiquant que la connexion à la base de données est opérationnelle.

        :param name: Le nom de la base de données à afficher dans le message.
        :type name: str
        """
        text = f'La base {name} est opérationnelle'
        console.print(text, style="green")
