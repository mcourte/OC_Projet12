import os
import sys
import click
from sqlalchemy.orm import Session

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from config_init import SessionLocal
from controllers.user_controller import EpicUserBase
from controllers.epic_controller import EpicBase
from terminal.terminal_user import EpicTerminalUser


@click.group()
def user_cli():
    """Groupe de commandes utilisateur"""
    pass


@click.command()
def login():
    """Login a user"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")


@click.command()
@click.argument('first_name')
@click.argument('last_name')
@click.argument('role')
@click.argument('password')
def add_user(first_name, last_name, role, password):
    """Login a user"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")
    session: Session = SessionLocal()
    user_controller = EpicUserBase(session)
    try:
        user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'password': password,
        }
        user = user_controller.create_user(user_data)
        click.echo(f"Utilisateur {user.username} ajouté avec succès")
    except ValueError as e:
        click.echo(str(e))
    finally:
        session.close()


@click.command()
def list_users():
    """Affiche la liste des utilisateurs"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")
        return

    session = SessionLocal()  # Créez une session locale
    user_controller = app.epic.users  # Utilisez l'instance EpicUserBase de EpicDatabase
    try:
        users = user_controller.get_all_users()  # Appelle sans argument
        for user in users:
            click.echo(f"{user.first_name} {user.last_name} ({user.username}) - {user.email}")
    except Exception as e:
        click.echo(f"Erreur lors de la récupération des utilisateurs : {e}")
    finally:
        session.close()


@click.command()
def mydata():
    """Login a user"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")
    """Show data of connected employee"""
    if app.user:
        controle_user = EpicTerminalUser(app.user, app.epic)
        controle_user.show_profil()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def update_mydata():
    """Update data of connected employee"""
    """Login a user"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")
    if app.user:
        controle_user = EpicTerminalUser(app.user, app.epic)
        controle_user.update_profil()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def create():
    """Create a new employee"""
    """Login a user"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")
    if app.user:
        controle_user = EpicTerminalUser(app.user, app.epic)
        controle_user.create_user()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def update_password():
    """Modify the password of an employee"""
    """Login a user"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")
    if app.user:
        controle_employee = EpicTerminalUser(app.user, app.epic)
        controle_employee.update_user_password()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def inactivate():
    """Inactivate an employee"""
    app = EpicBase()
    if app.login():
        print("Connexion réussie.")
    else:
        print("Échec de la connexion.")
    if app.user:
        controle_employee = EpicTerminalUser(app.user, app.epic)
        controle_employee.inactivate_user()
        app.refresh_session()
    app.epic.database_disconnect()


# Ajoutez les commandes au groupe
user_cli.add_command(login)
user_cli.add_command(mydata)
user_cli.add_command(update_mydata)
user_cli.add_command(list_users)
user_cli.add_command(create)
user_cli.add_command(update_password)
user_cli.add_command(inactivate)

if __name__ == '__main__':
    user_cli()
