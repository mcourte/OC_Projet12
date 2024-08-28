import click
import os
import sys
import logging
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
# Configuration de base du logging
logging.basicConfig(
    level=logging.DEBUG,  # Niveau de log minimum
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format des messages de log
)

# Créer un logger pour ce module
logger = logging.getLogger(__name__)
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from cli import epic_cli


def sentry_activate():
    dsn = "https://8d035592443a8c8d8bcef25a1b7fe5df@o4505946318635008"
    dsn += ".ingest.sentry.io/4505946331086848"
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            SqlalchemyIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )


@click.group(help="------ CRM EpicEvent ------")
def main():
    """Groupe principal de commandes"""
    pass


# Ajouter les sous-commandes de epic_cli au groupe principal
main.add_command(epic_cli.start)
main.add_command(epic_cli.logout)
main.add_command(epic_cli.initbase)

if __name__ == '__main__':
    main()
