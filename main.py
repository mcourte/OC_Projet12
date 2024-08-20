import click
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from config import SessionLocal
from controllers.user_controller import EpicUser
from cli import contract_cli, customer_cli, epic_cli, event_cli, user_cli


@click.group(help="------ CRM EpicEvent ------")
def main():
    session = SessionLocal()
    user_controller = EpicUser()
    pass


# Ajoutez les groupes de commandes et les commandes individuelles
main.add_command(epic_cli.login)
main.add_command(epic_cli.logout)
main.add_command(epic_cli.dashboard)
main.add_command(epic_cli.initbase)

# Ajouter le groupe de commandes user_cli
main.add_command(user_cli.user_cli)  # Ajoutez ici le groupe de commandes user_cli

main.add_command(customer_cli.customer_cli)
main.add_command(contract_cli.contract_cli)
main.add_command(event_cli.event_cli)

if __name__ == '__main__':
    main()
