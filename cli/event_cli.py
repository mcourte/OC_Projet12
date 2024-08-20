import click
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicBase
from terminal.terminal_event import EpicTerminalEvent


@click.group()
def event_cli():
    """Groupe de commandes evenèment"""
    pass


@click.command()
def list_events():
    """ list of events """
    app = EpicBase()

    if app.user:
        controle_event = EpicTerminalEvent(app.user, app.epic)
        controle_event.list_of_events()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def update_event():
    """ modify an event """
    app = EpicBase()

    if app.user:
        controle_event = EpicTerminalEvent(app.user, app.epic)
        controle_event.update_event()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def create_event():
    """ create an event """
    app = EpicBase()

    if app.user:
        controle_event = EpicTerminalEvent(app.user, app.epic)
        controle_event.create_event()
        app.refresh_session()
    app.epic.database_disconnect()


event_cli.add_command(create_event)
event_cli.add_command(update_event)
event_cli.add_command(list_events)
if __name__ == '__main__':
    event_cli()
