import click
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicBase
from terminal.terminal_contract import EpicTerminalContract


@click.group()
def contract_cli():
    """Groupe de commandes evenèment"""
    pass


@click.command()
def list_contracts():
    """ list the contracts """
    app = EpicBase()

    if app.user:
        controle_contract = EpicTerminalContract(app.user, app.epic)
        contracts = controle_contract.list_of_contracts()
        for contract in contracts:
            click.echo(f"{contract.description} {contract.state} ({contract.customer_id})")
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def create_contract():
    """ create a contract """
    app = EpicBase()

    if app.user:
        controle_contract = EpicTerminalContract(app.user, app.epic)
        controle_contract.create_contract()
        app.refresh_session()
    app.epic.database_disconnect()


@click.command()
def update_contract():
    """ modify a contract """
    app = EpicBase()

    if app.user:
        controle_contract = EpicTerminalContract(app.user, app.epic)
        controle_contract.update_contract()
        app.refresh_session()
    app.epic.database_disconnect()


contract_cli.add_command(list_contracts)
contract_cli.add_command(create_contract)
contract_cli.add_command(update_contract)

if __name__ == '__main__':
    contract_cli()
