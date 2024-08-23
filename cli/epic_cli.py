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


@click.group()
def epic_cli():
    """Groupe de commandes evenèment"""
    pass


@click.command()
def start(**kwargs):
    """ Login to the database and start the dashboard """
    app = EpicBase()
    app.login(**kwargs)
    controller = EpicDashboard(epic_base=app)
    controller.run()


@click.command()
def logout():
    """ Logout from database """
    app = EpicBase()
    app.check_logout()
    app.epic.database_disconnect()


@click.command()
def initbase():
    """ Initialize the database """
    EpicBase.initbase()
