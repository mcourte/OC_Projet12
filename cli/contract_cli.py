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
from controllers.contract_controller import ContractBase
from config import SessionLocal


@click.group()
def contract_cli():
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
@click.argument('description')
@click.argument('total_amount')
@click.argument('remaining_amount')
@click.argument('state')
@click.argument('customer_id')
@click.argument('paiement_state')
def add_contract(description, total_amount, remaining_amount, state, customer_id, paiement_state):
    """Create a contract"""
    session = SessionLocal()
    contract_controller = ContractBase(session)
    try:
        contract_data = {
            'description': description,
            'total_amount': total_amount,
            'remaining_amount': remaining_amount,
            'state': state,
            'customer_id': customer_id,
            'paiement_state': paiement_state,
        }
        contract = contract_controller.create_contract(contract_data)
        click.echo(f"Contrat {contract.description} ajouté ")
    except ValueError as e:
        click.echo(str(e))
    finally:
        session.close()


@click.command()
def list_contracts():
    session = SessionLocal()
    contract_controller = ContractBase(session)
    contracts = contract_controller.get_all_contracts()
    for contract in contracts:
        click.echo(f"{contract.description} {contract.state} ({contract.customer_id})")
    session.close()


contract_cli.add_command(login)
contract_cli.add_command(add_contract)
contract_cli.add_command(list_contracts)
