import os
import sys


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicDatabase

from controllers.config import Config
from controllers.session import stop_session
from views.authentication_view import AuthenticationView
from views.menu_view import MenuView


class EpicDashboard:
    def __init__(self, epic_base) -> None:
        self.gestion = epic_base

        # Debugging: Vérification de l'initialisation de current_user
        if not hasattr(self.gestion, 'current_user') or not self.gestion.current_user:
            raise ValueError("L'utilisateur n'est pas initialisé ou n'est pas authentifié.")

        print(f"Utilisateur connecté : {self.gestion.current_user.username}")

        config = Config()
        self.database = EpicDatabase(
            database=config.database,
            host=config.host,
            user=config.user,
            password=config.password,
            port=config.port
        )
        self.session = self.gestion.epic.session

    def call_function(self, choice) -> bool:

        match choice:
            case '01':
                self.database.users.show_profil(self.gestion)
            case '02':
                self.database.users.update_profil(self.gestion)
            case '03':
                self.database.customers.list_of_customers(self.session)
            case '04':
                self.database.contracts.list_of_contracts(self.session)
            case '05':
                self.database.events.list_of_events(self.session)
            case '06':
                self.database.users.list_of_users(self.session)
            case '07':
                if self.gestion.current_user.role.code in {'COM'}:
                    self.database.customers.create_customer(self.session)
                if self.gestion.current_user.role.code in {'GES'}:
                    self.database.users.list_of_users(self.session)
                if self.gestion.current_user.role.code in {'SUP'}:
                    self.database.events.list_of_events_filtered(self.session)
            case '08':
                if self.gestion.current_user.role.code in {'GES', 'ADM'}:
                    self.database.users.create_user(self.session)
                if self.gestion.current_user.role.code in {'COM', 'ADM'}:
                    self.database.customers.update_customer(self.session)  # Passez le token ici
            case '09':
                if self.gestion.current_user.role.code in {'GES', 'ADM'}:
                    self.database.users.inactivate_user(self.session)
            case '10':
                if self.gestion.current_user.role.code in {'GES', 'ADM'}:
                    self.database.contracts.create_contract(self.session)
            case '11':
                if self.gestion.current_user.role.code in {'GES', 'ADM', 'COM'}:
                    self.database.contracts.update_contract(self.session)
            case '12':
                if self.gestion.current_user.role.code in {'ADM', 'GES'}:
                    self.database.customers.update_customer_commercial(self.session)
            case '13':
                if self.gestion.current_user.role.code in {'ADM', 'GES'}:
                    self.database.contracts.update_contract_gestion(self.session)
            case '14':
                if self.gestion.current_user.role.code in {'ADM', 'GES', 'SUP'}:
                    self.database.events.update_event(self.session)
            case '15':
                if self.gestion.current_user.role.code in {'ADM'}:
                    self.database.customers.create_customer(self.session)
            case '16':
                if self.gestion.current_user.role.code in {'ADM', 'COM'}:
                    self.database.customers.update_customer(self.session)
            case '17':
                if self.gestion.current_user.role.code in {'ADM', 'GES'}:
                    self.database.events.create_event(self.session)
            case '18':
                if self.gestion.current_user.role.code in {'ADM', 'GES', 'SUP'}:
                    self.database.events.update_event(self.session)
            case '19':
                if self.gestion.current_user.role.code in {'ADM', 'SUP'}:
                    self.database.events.list_of_events_filtered(self.session)
            case 'D':
                stop_session()
                return False
            case 'Q':
                stop_session()
                return False
        return True

    def run(self) -> None:
        try:
            if not self.gestion.current_user:
                raise ValueError("L'utilisateur n'est pas initialisé.")
            print("Tableau de bord en cours d'exécution...")
            username = self.gestion.current_user.username
            print(f"Utilisateur : {username}")
            user_info = self.database.get_user(username)
            if user_info:
                print("Utilisateur trouvé:", user_info)
            else:
                print("Aucun utilisateur trouvé.")
        except Exception:
            pass

        if self.gestion.current_user:
            running = True
            AuthenticationView.display_welcome(self.gestion.current_user.username)
            try:
                while running:
                    result = MenuView.menu_choice(self.gestion.current_user.role.code)
                    running = self.call_function(result)
            except KeyboardInterrupt:
                pass
