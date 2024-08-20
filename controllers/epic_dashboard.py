import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.contract_controller import ContractBase
from controllers.event_controller import EventBase
from controllers.customer_controller import CustomerBase
from controllers.user_controller import EpicUserBase
from controllers.epic_controller import EpicDatabase

from .session import stop_session


from views.authentication_view import AuthenticationView
from views.menu_view import MenuView


class EpicDashboard:

    def __init__(self, database, host, user, password) -> None:
        # Passez les arguments nécessaires à EpicDatabase
        self.gestion = EpicDatabase(database, host, user, password)
        self.gestion_user = EpicUserBase(self.gestion.session)
        self.gestion_customer = CustomerBase(self.gestion.session)
        self.gestion_contract = ContractBase(self.gestion.session)
        self.gestion_event = EventBase(self.gestion.session)

    def call_function(self, choice) -> bool:
        match choice:
            case '01':
                self.gestion_user.get_user()
                self.gestion_user.update_user()
            case '03':
                self.gestion_customer.get_all_customers()
            case '04':
                self.gestion_contract.get_all_contracts()
            case '05':
                self.gestion_event.get_all_events()
            case '06':
                match self.manager.user.role.code:
                    case 'G':
                        self.gestion_user.get_all_users()
                    case 'C':
                        self.gestion_customer.create_customer()
            case '07':
                match self.gestion.user.role.code:
                    case 'M':
                        self.gestion_user.create_user()
                    case 'C':
                        self.gestion_customer.update_customer()
            case '08':
                match self.gestion.user.role.code:
                    case 'M':
                        self.gestion_user.update_user()
                    case 'C':
                        self.gestion_event.create_event()
            case '09':
                match self.gestion.user.role.code:
                    case 'M':
                        self.gestion_user.inactivate_()
            case '10':
                self.gestion_contract.create_contract()
            case '11':
                self.gestion_contract.update_contract()
            case '12':
                self.gestion_customer.update_customer()
            case '13':
                self.gestion_event.update_event()
            case 'D':
                stop_session()
                return False
            case 'Q':
                self.gestion.refresh_session()
                return False
        return True

    def run(self) -> None:
        if self.gestion.user:
            running = True
            AuthenticationView.display_welcome(self.gestion.user.username)
            try:
                while running:
                    result = MenuView.menu_choice(self.gestion.user.role.code)
                    running = self.call_function(result)
            except KeyboardInterrupt:
                pass
