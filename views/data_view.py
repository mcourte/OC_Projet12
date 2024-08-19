import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from views.console_view import console


class DataView:

    @classmethod
    def display_workflow(cls):
        console.print('Mise à jour du workflow')

    @classmethod
    def display_nocontracts(cls):
        console.print('Aucun contrat trouvé')

    @classmethod
    def display_interupt(cls):
        console.print('Opération abandonée')

    @classmethod
    def display_error_contract_amount(cls):
        console.print('Ce montant est supérieur au restant dû')

    @classmethod
    def display_commercial_with_contracts(cls):
        console.print('Ce commercial gère des contracts actifs')

    @classmethod
    def display_need_one_manager(cls):
        console.print('La base doit contenir au moins un manager')

    @classmethod
    def display_error_unique(cls):
        console.print('Impossible: cet enregistrement existe déjà')

    @classmethod
    def display_error_contract_need_c(cls):
        console.print("Le contract doit être à l'état créé")

    @classmethod
    def display_data_update(cls):
        console.print('Vos modifications ont été enregistrées')
