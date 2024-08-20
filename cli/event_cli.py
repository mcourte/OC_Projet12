import click
import os
import sys
from sqlalchemy.orm import Session

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicBase
from controllers.event_controller import EventBase
from config import SessionLocal


@click.group()
def event_cli():
    """Groupe de commandes evenèment"""
    pass


@click.command()
@click.option('--username')
@click.option('--password')
def login(username, password):
    """ login to the database """
    app = EpicBase()
    result = app.login(username=username, password=password)
    if result:
        print("Connexion réussie")
    else:
        print("Échec de la connexion")
    app.epic.database_disconnect()


@click.command()
@click.argument('title')
@click.argument('description')
@click.argument('location')
@click.argument('attendees')
@click.argument('date_started')
@click.argument('date_ended')
def add_event(title, description, location, attendees, date_started, date_ended):
    """ create an event """
    session: Session = SessionLocal()
    event_controller = EventBase(session)
    try:
        # Construire le dictionnaire avec les données de l'utilisateur
        event_data = {
            'title': title,
            'description': description,
            'location': location,
            'attendees': attendees,
            'date_started': date_started,
            'date_ended': date_ended,
        }
        event = event_controller.create_event(event_data)
        click.echo(f"Evènement {event.title} ajouté avec succès")
    except ValueError as e:
        click.echo(str(e))
    finally:
        session.close()


@click.command()
def list_events():
    session: Session = SessionLocal()
    event_controller = EventBase(session)
    events = event_controller.get_all_events()
    for event in events:
        click.echo(f"{event.title} {event.location} ({event.attendees})")
    session.close()


# Ajoutez les commandes au groupe
event_cli.add_command(login)
event_cli.add_command(add_event)
event_cli.add_command(list_events)
