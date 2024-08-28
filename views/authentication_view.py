import re
import questionary
from .console_view import console


class AuthenticationView:
    """
    Classe pour gérer l'affichage des vues liées à l'authentification et à la configuration de la base de données.
    """

    @classmethod
    def display_logout(cls) -> None:
        """
        Affiche un message de déconnexion.
        """
        text = "Vous êtes déconnecté"
        print(text)

    @classmethod
    def display_welcome(cls, username) -> None:
        """
        Affiche un message de bienvenue à l'utilisateur.

        Paramètres :
        ------------
        username (str) : Le nom d'utilisateur à inclure dans le message de bienvenue.
        """
        text = f"!!! Bienvenue {username} sur le CRM de EpicEvent !!!"
        console.print(text, justify="center", style="bold blue")

    @classmethod
    def display_waiting_databasecreation(cls, f, data):
        """
        Affiche un message indiquant que la création de la base de données est en cours.

        Paramètres :
        ------------
        f (Callable) : La fonction à exécuter pour créer la base de données.
        data (tuple) : Les arguments à passer à la fonction de création de la base de données.
        """
        with console.status("Création de la base de données ...", spinner="circleQuarters"):
            f(*data)

    @staticmethod
    def prompt_login(**kwargs):
        """
        Demande à l'utilisateur de saisir un identifiant et un mot de passe.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la fonction questionary.text et questionary.password.

        Retourne :
        -----------
        tuple : Un tuple contenant l'identifiant et le mot de passe saisis par l'utilisateur.
        """
        text = "Pour vous connecter au CRM d'EpicEvents, merci de rentrez votre nom d'utilisateur et votre mot de passe"
        console.print(text, justify="center", style="bold blue")
        username = questionary.text("Identifiant:").ask()
        password = questionary.password("Password:").ask()
        return username, password

    @classmethod
    def display_database_connection(cls, name):
        """
        Affiche un message indiquant que la connexion à la base de données est opérationnelle.

        Paramètres :
        ------------
        name (str) : Le nom de la base de données à afficher dans le message.
        """
        text = f'La base {name} est opérationnelle'
        console.print(text, style="green")

    @classmethod
    def prompt_baseinit(cls, **kwargs):
        """
        Demande les informations nécessaires pour initialiser une nouvelle base de données.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la fonction questionary.text et questionary.password.

        Retourne :
        -----------
        tuple : Un tuple contenant le nom de la base de données, l'identifiant administrateur,
        le mot de passe administrateur et le port.
        """

        username = questionary.text(
            "Identifiant administrateur:",
            validate=lambda text: True
            if re.match(r"^[a-zA-Z]+$", text)
            else "Seul des caractères alpha sont autorisés",
            **kwargs).ask()
        if username is None:
            raise KeyboardInterrupt

        password = questionary.password(
            "Password administrateur:", **kwargs).ask()
        if password is None:
            raise KeyboardInterrupt

        return (username, password)

    @classmethod
    def prompt_manager(cls, **kwargs):
        """
        Demande les informations nécessaires pour créer un manager, y compris l'identifiant et le mot de passe.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la fonction questionary.text et questionary.password.

        Retourne :
        -----------
        tuple : Un tuple contenant l'identifiant et le mot de passe du manager.
        """
        username = questionary.text(
            "Identifiant manager:",
            validate=lambda text: True
            if re.match(r"^[a-zA-Z]+$", text)
            else "Seul des caractères alpha sont autorisés",
            **kwargs).ask()
        if username is None:
            raise KeyboardInterrupt

        password = questionary.password(
            "Password commercial:", **kwargs).ask()
        if password is None:
            raise KeyboardInterrupt

        result = questionary.password(
            "Confirmez le mot de passe:",
            validate=lambda text: True if text == password
            else "Les mots de passe ne correspondent pas",
            **kwargs).ask()
        if result is None:
            raise KeyboardInterrupt

        return (username, password)

    @classmethod
    def prompt_confirm_testdata(cls, **kwargs):
        """
        Demande à l'utilisateur s'il souhaite générer des données de test.

        Paramètres :
        ------------
        **kwargs : Arguments supplémentaires pour la fonction questionary.confirm.

        Retourne :
        -----------
        bool : True si l'utilisateur souhaite générer des données de test, False sinon.
        """
        return questionary.confirm(
            "Souhaitez-vous générer des données de test ?", **kwargs).ask()
