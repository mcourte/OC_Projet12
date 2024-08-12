import os
import sys
import click
from sqlalchemy.orm import Session


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from config import SessionLocal
from controllers.user_controller import EpicUserBase


@click.command()
@click.argument('first_name')
@click.argument('last_name')
@click.argument('role')
@click.argument('password')
def add_user(first_name, last_name, role, password):
    session: Session = SessionLocal()
    user_controller = EpicUserBase(session)
    try:
        # Construire le dictionnaire avec les données de l'utilisateur
        user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'password': password,
        }
        user = user_controller.create_user(user_data)  # Passer le dictionnaire ici
        click.echo(f"Utilisateur {user.username} ajouté avec succès")
    except ValueError as e:
        click.echo(str(e))
    finally:
        session.close()


@click.command()
def list_users():
    session: Session = SessionLocal()
    user_controller = EpicUserBase(session)
    users = user_controller.get_all_users()
    for user in users:
        click.echo(f"{user.first_name} {user.last_name} ({user.username}) - {user.email}")
    session.close()


cli = click.Group()
cli.add_command(add_user)
cli.add_command(list_users)

if __name__ == '__main__':
    cli()
