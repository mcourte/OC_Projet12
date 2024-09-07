import click
import os
import sys
import sentry_sdk
import logging

# Désactiver tous les messages sauf CRITICAL
logging.basicConfig(level=logging.CRITICAL)

# Pour asyncio seulement (ou n'importe quelle autre bibliothèque spécifique)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from cli import epic_cli


def sentry_activate():
    sentry_sdk.init(
        dsn="https://f005574ea1d1b9036d974ac1ef6eacd1@o4507899769389056.ingest.de.sentry.io/4507899813757008",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
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


main.add_command(epic_cli.start)
main.add_command(epic_cli.logout)
main.add_command(epic_cli.initbase)
if __name__ == '__main__':
    sentry_activate()
    main()
