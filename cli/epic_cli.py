import click
import sys
import os


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicBase
from controllers.epic_dashboard import EpicDashboard


@click.command()
@click.option('--username', prompt='Username', help='The username for login.')
@click.option('--password', prompt=True, hide_input=True, help='The password for login.')
def login(username, password):
    """ Login to the database """
    app = EpicBase()
    result = app.login(username=username, password=password)
    if result:
        print("Connexion réussie")
    else:
        print("Échec de la connexion")
    app.epic.database_disconnect()



@click.command()
def logout():
    """ logout from database """
    app = EpicBase()
    app.check_logout()
    app.epic.database_disconnect()


@click.command()
def dashboard():
    """ access to menu """
    controller = EpicDashboard()
    controller.run()


@click.command()
def initbase():
    """ init the database """
    EpicBase.initbase()
