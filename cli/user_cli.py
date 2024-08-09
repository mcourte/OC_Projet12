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
from controllers.user_controller import UserController


@click.command()
@click.argument('first_name')
@click.argument('last_name')
@click.argument('username')
@click.argument('role')
@click.argument('password')
@click.argument('email')
def add_user(first_name, last_name, username, role, password, email):
    session: Session = SessionLocal()
    user_controller = UserController(session)
    try:
        user = user_controller.create_user(first_name, last_name, username, role, password, email)
        click.echo(f"Utilisateur {user.username} ajouté avec succès")
    except ValueError as e:
        click.echo(str(e))
    finally:
        session.close()


@click.command()
def list_users():
    session: Session = SessionLocal()
    user_controller = UserController(session)
    users = user_controller.get_all_users()
    print(users)
    session.close()


cli = click.Group()
cli.add_command(add_user)
cli.add_command(list_users)

if __name__ == '__main__':
    cli()
