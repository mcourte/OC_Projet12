import os
import sys
from configparser import ConfigParser


def create_config(basename, username, password, port):
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
    def __init__(
            self,
            filename,
            message="The file doesn't exists"
            ):
        self.message = message
        self.filename = filename
        super().__init__(self.message)

    def __str__(self) -> str:
        return "the file " + self.filename + " doesn't exists"


class NoSectionPostgresql(Exception):
    def __init__(
            self,
            filename,
            section='',
            message="The file doesn't have the correct section"
            ):
        self.message = message
        self.section = section
        self.filename = filename
        super().__init__(self.message)

    def __str__(self) -> str:
        return "the file " + self.filename + " doesn't have "\
            + self.section + " section"


class Config():

    def __init__(self, filename='database.ini') -> None:
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
            raise NoSectionPostgresql(filename='database.ini', section=section)

    def __str__(self) -> str:
        return str(self.db_config)


class Environ():
    def __init__(self) -> None:
        """
        Load the .cli_env file
        :raise FileEnvNotExists if the file doesn't exist
        """
        # Determine the absolute path of the parent directory
        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

        # Add the parent directory to PYTHONPATH
        sys.path.insert(0, parent_dir)

        # Explicitly specify the .cli_env file
        dotenv_file = os.path.join(parent_dir, '.cli_env')
        if not os.path.exists(dotenv_file):
            raise FileNotExists(f"The file {dotenv_file} doesn't exist")
        self.DEFAULT_DATABASE = os.getenv('DEFAULT_DATABASE')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.TOKEN_DELTA = int(os.getenv('TOKEN_DELTA'))
