import os
import sys
from configparser import ConfigParser


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

        if not os.path.exists(self.filename):
            # Créez le fichier de configuration avec des valeurs par défaut si nécessaire
            self.create_config('app_db', 'postgres', 'password', '5432')

        parser.read(self.filename)

        if parser.has_section(section):
            self.database = parser.get(section, 'DATABASE')
            self.host = parser.get(section, 'HOST')
            self.user = parser.get(section, 'USER')
            self.password = parser.get(section, 'PASSWORD')
            self.port = parser.get(section, 'PORT')
        else:
            raise NoSectionPostgresql(filename=self.filename, section=section)

    def create_config(self, name_db, username, password, port):
        """
        Crée un fichier de configuration avec des valeurs spécifiées.
        """
        with open(self.filename, 'w') as configfile:
            configfile.write('[postgresql]\n')
            configfile.write(f'DATABASE = {name_db}\n')
            configfile.write('HOST = localhost\n')
            configfile.write(f'USER = {username}\n')
            configfile.write(f'PASSWORD = {password}\n')
            configfile.write(f'PORT = {port}\n')


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

        # Charger les variables d'environnement depuis le fichier
        self.load_env(dotenv_file)

        # Accéder aux variables d'environnement
        self.DEFAULT_DATABASE = os.getenv('DEFAULT_DATABASE')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.TOKEN_DELTA = os.getenv('TOKEN_DELTA')

        # Vérification des variables d'environnement
        if self.DEFAULT_DATABASE is None:
            raise ValueError("La variable d'environnement DEFAULT_DATABASE n'est pas définie.")
        if self.SECRET_KEY is None:
            raise ValueError("La variable d'environnement SECRET_KEY n'est pas définie.")
        if self.TOKEN_DELTA is None:
            raise ValueError("La variable d'environnement TOKEN_DELTA n'est pas définie.")

        try:
            self.TOKEN_DELTA = int(self.TOKEN_DELTA)
        except ValueError:
            raise ValueError("TOKEN_DELTA doit être un entier.")

    def load_env(self, dotenv_file):
        """
        Charge les variables d'environnement à partir du fichier spécifié.
        """
        with open(dotenv_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
