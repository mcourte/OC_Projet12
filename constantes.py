# Définition des rôles en tant que constantes
ROLE_COM = 'com'
ROLE_GES = 'ges'
ROLE_SUP = 'sup'
ROLE_ADM = 'adm'

# Définition des permissions en tant que constantes
READ_ACCESS = "read_access"
CREATE_EVENT = "create_event"
EDIT_EVENT = "edit_event"
DELETE_EVENT = "delete_event"
CREATE_USER = "create_user"
EDIT_USER = "edit_user"
DELETE_USER = "delete_user"
CREATE_CUSTOMER = "create_customer"
EDIT_CUSTOMER = "edit_customer"
DELETE_CUSTOMER = "delete_customer"
CREATE_CONTRACT = "create_contract"
EDIT_CONTRACT = "edit_contract"
DELETE_CONTRACT = "delete_contract"
SORT_USER = "sort_user"
SORT_CUSTOMER = "sort_user"
SORT_CONTRACT = "sort_user"
SORT_EVENT = "sort_user"


# Constantes pour le tri des élements avec la méthode générique
def get_sortable_attributes():
    from models.contract import Contract
    from models.user import User
    from models.event import Event
    from models.customer import Customer
    from permissions import Role

    return {
        User: {
            Role.ADM: ['user_id', 'first_name', 'last_name', 'username'],
        },
        Contract: {
            Role.ADM: ['contract_id', 'ges_contact_id', 'com_contact_id', 'remaining_amount', 'is_signed'],
            Role.COM: ['is_signed', 'remaining_amount']
        },
        Customer: {
            Role.ADM: ['last_name', 'company_name', 'email', 'com_contact_id', 'creation_time', 'update_time'],
        },
        Event: {
            Role.ADM: ['event_id', 'ges_contact_id', 'ges_support_id', 'customer_id', 'event_date', 'location'],
            Role.GES: ['sup_contact_id'],
            Role.SUP: ['sup_contact_id']
        }
    }
