import click
import sys
import os

# Determine the absolute path of the parent directory
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Add the parent directory to PYTHONPATH
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
        click.echo("Connexion réussie")
    else:
        click.echo("Échec de la connexion")


@click.command()
def logout():
    """ Logout from database """
    app = EpicBase()
    app.check_logout()
    app.epic.database_disconnect()


@click.command()
def dashboard():
    """ Access to menu """
    controller = EpicDashboard()
    controller.run()


@click.command()
def initbase():
    """ Init the database """
    app = EpicBase()
    app.initbase()
