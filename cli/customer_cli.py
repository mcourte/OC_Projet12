import click
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicBase
from controllers.customer_controller import CustomerBase
from config import SessionLocal
from terminal.terminal_customer import EpicTerminalCustomer


@click.group()
def customer_cli():
    """Groupe de commandes evenèment"""
    pass


@click.command()
def list_customers():
    """ list all the clients """
    app = EpicBase()

    if app.user:
        controle_customer = EpicTerminalCustomer(app.user, app.epic)
        controle_customer.list_of_customers()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def update_customer():
    """ modify the commercial of a client """
    app = EpicBase()

    if app.user:
        controle_customer = EpicTerminalCustomer(app.user, app.epic)
        controle_customer.update_customer()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def create_customer():
    """ create a new client """
    app = EpicBase()

    if app.user:
        controle_customer = EpicTerminalCustomer(app.user, app.epic)
        controle_customer.create_customer()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def update():
    """ modify data of a client """
    app = EpicBase()

    if app.user:
        controle_client = EpicTerminalCustomer(app.user, app.epic)
        controle_client.update_customer()
        app.refresh_session()
    app.epic.database_disconnect()


customer_cli.add_command(list_customers)
customer_cli.add_command(create_customer)
customer_cli.add_command(update_customer)
if __name__ == '__main__':
    customer_cli()
