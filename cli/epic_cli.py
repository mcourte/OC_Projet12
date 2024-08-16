import click
import sys
import os


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicBase


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
def logout():
    """ logout from database """
    app = EpicBase()
    app.check_logout()
    app.epic.database_disconnect()


@click.command()
def initbase():
    """ init the database """
    EpicBase.initbase()


cli = click.Group()
cli.add_command(login)
cli.add_command(initbase)
cli.add_command(logout)
if __name__ == '__main__':
    cli()
