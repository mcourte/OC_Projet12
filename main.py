import click
import os
import sys
import logging

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
