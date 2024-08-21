import os
import sys
from configparser import ConfigParser


def create_config(basename, username, password, port):
    """
    Crée un fichier de configuration pour une base de données PostgreSQL.

    Paramètres :
    ------------
    basename : str
        Le nom de la base de données.
    username : str
        Le nom d'utilisateur pour la base de données.
    password : str
        Le mot de passe pour la base de données.
    port : str
        Le port utilisé pour la connexion à la base de données.

    Retourne :
    ----------
    str : Le nom du fichier de configuration créé.
    """
    data = [
        '[postgresql]',
        f'DATABASE = {basename}',
        'HOST = localhost',
        f'USER = {username}',
        f'PASSWORD = {password}',
        f'PORT = {port}'
    ]
    filename = f"{basename}_database.ini"
    file = open(filename, "w")
    for line in data:
        file.write(line + "\n")
    file.close()
    return filename


class FileNotExists(Exception):
    """
    Exception levée lorsque le fichier spécifié n'existe pas.
    """

    def __init__(self, filename, message="Le fichier n'existe pas"):
        """
        Initialise l'exception avec le nom du fichier et un message.

        Paramètres :
        ------------
        filename : str
            Le nom du fichier qui n'existe pas.
        message : str
            Le message d'erreur à afficher (optionnel).
        """
        self.message = message
        self.filename = filename
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Retourne une représentation en chaîne de caractères de l'exception.

        Retourne :
        ----------
        str : Message d'erreur indiquant que le fichier n'existe pas.
        """
        return "Le fichier " + self.filename + " n'existe pas"


class NoSectionPostgresql(Exception):
    """
    Exception levée lorsque la section PostgreSQL est absente du fichier de configuration.
    """

    def __init__(self, filename, section='', message="Le fichier n'a pas la section correcte"):
        """
        Initialise l'exception avec le nom du fichier, la section manquante, et un message.

        Paramètres :
        ------------
        filename : str
            Le nom du fichier qui manque la section.
        section : str
            La section attendue dans le fichier.
        message : str
            Le message d'erreur à afficher (optionnel).
        """
        self.message = message
        self.section = section
        self.filename = filename
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        Retourne une représentation en chaîne de caractères de l'exception.

        Retourne :
        ----------
        str : Message d'erreur indiquant que la section est absente.
        """
        return "Le fichier " + self.filename + " n'a pas la section " + self.section


class Config:
    """
    Classe permettant de charger et de gérer les configurations de base de données à partir d'un fichier INI.
    """

    def __init__(self, filename='database.ini') -> None:
        """
        Initialise l'objet Config en chargeant les paramètres du fichier spécifié.

        Paramètres :
        ------------
        filename : str
            Le nom du fichier de configuration à charger (par défaut 'database.ini').

        Exceptions :
        ------------
        FileNotExists :
            Levée si le fichier de configuration n'existe pas.
        NoSectionPostgresql :
            Levée si la section 'postgresql' est absente du fichier.
        """
        self.filename = filename
        section = 'postgresql'
        parser = ConfigParser()

        try:
            with open(self.filename):
                parser.read(self.filename)
        except IOError:
            raise FileNotExists(self.filename)

        self.db_config = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                self.db_config[param[0]] = param[1]
        else:
            raise NoSectionPostgresql(filename=self.filename, section=section)

    def __str__(self) -> str:
        """
        Retourne une représentation en chaîne de caractères de la configuration de la base de données.

        Retourne :
        ----------
        str : Représentation des paramètres de la base de données.
        """
        return str(self.db_config)


class Environ:
    """
    Classe permettant de charger les variables d'environnement à partir d'un fichier .cli_env.
    """

    def __init__(self) -> None:
        """
        Charge le fichier .cli_env.

        Exceptions :
        ------------
        FileNotExists :
            Levée si le fichier .cli_env n'existe pas.
        """
        # Déterminer le chemin absolu du répertoire parent
        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

        # Ajouter le répertoire parent au PYTHONPATH
        sys.path.insert(0, parent_dir)

        # Spécifier explicitement le fichier .cli_env
        dotenv_file = os.path.join(parent_dir, '.cli_env')
        if not os.path.exists(dotenv_file):
            raise FileNotExists(f"Le fichier {dotenv_file} n'existe pas")
        self.DEFAULT_DATABASE = os.getenv('DEFAULT_DATABASE')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.TOKEN_DELTA = int(os.getenv('TOKEN_DELTA'))
