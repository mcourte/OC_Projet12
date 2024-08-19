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
from controllers.customer_controller import CustomerBase
from config import SessionLocal


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
@click.argument('first_name')
@click.argument('last_name')
@click.argument('email')
@click.argument('phone')
@click.argument('company_name')
@click.argument('commercial_id')
def add_customer(first_name, last_name, email, phone, company_name, commercial_id):
    """Create a customer"""
    session = SessionLocal()
    customer_controller = CustomerBase(session)
    try:
        customer_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'company_name': company_name,
            'commercial_id': commercial_id,
        }
        customer = customer_controller.create_customer(customer_data)
        click.echo(f"Client {customer.customer_id} ajouté avec succès")
    except ValueError as e:
        click.echo(str(e))
    finally:
        session.close()


@click.command()
def list_customers():
    session: Session = SessionLocal()
    customer_controller = CustomerBase(session)
    customers = customer_controller.get_all_customers()
    for customer in customers:
        click.echo(f"{customer.first_name} {customer.last_name}")
    session.close()
