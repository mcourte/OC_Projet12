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
def login(**kwargs):
    """ login to the database """
    app = EpicBase()
    app.login(**kwargs)
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
