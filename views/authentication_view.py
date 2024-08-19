import re
import questionary
from .console_view import console
from rich.panel import Panel
from rich.text import Text


class AuthenticationView:

    @classmethod
    def display_logout(cls) -> None:
        text = "Vous êtes déconnecté"
        print(text)

    @classmethod
    def display_welcome(cls, username) -> None:
        text = f" Bienvenue {username} sur EpicEvent"
        panel = Panel(Text(text, justify="center"))
        console.print(panel)

    @classmethod
    def display_waiting_databasecreation(cls, f, data):
        print("Création de la base de données ...")
        with console.status("Création de la base de données ...",
                            spinner="circleQuarters"):
            f(*data)

    @classmethod
    def display_login(cls):
        username = console.input("Identifiant:")
        console.print(username)
        password = console.input("Mot de passe:")
        console.print(password)
        return username, password

    @staticmethod
    def prompt_login(**kwargs):
        username = questionary.text("Identifiant:").ask()
        password = questionary.password("Password:").ask()
        return username, password

    @classmethod
    def display_database_connection(cls, name):
        console.print(f'La base {name} est opérationnelle')

    @classmethod
    def prompt_baseinit(cls, **kwargs):
        basename = questionary.text(
                "Nom de votre base de données:",
                validate=lambda text: True,
                **kwargs).ask()
        if basename is None:
            raise KeyboardInterrupt
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

        port = questionary.text(
                "Port:",
                validate=lambda text: True
                if re.match(r"^[0-9]+$", text)
                else "Seul des chiffres sont autorisés",
                **kwargs).ask()
        if port is None:
            raise KeyboardInterrupt
        return (basename, username, password, port)

    @classmethod
    def prompt_manager(cls, **kwargs):
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
        return questionary.confirm(
            "Souhaitez-vous générer des données de test ?", **kwargs).ask()
