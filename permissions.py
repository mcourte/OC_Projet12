from enum import Enum
from constantes import (
    ROLE_COM, ROLE_GES, ROLE_SUP, ROLE_ADM,
    READ_ACCESS, CREATE_EVENT, EDIT_EVENT, DELETE_EVENT,
    CREATE_USER, EDIT_USER, DELETE_USER,
    CREATE_CUSTOMER, EDIT_CUSTOMER, DELETE_CUSTOMER,
    CREATE_CONTRACT, EDIT_CONTRACT, DELETE_CONTRACT,
    SORT_USER, SORT_CUSTOMER, SORT_CONTRACT, SORT_EVENT
)


class Role(Enum):
    COM = ROLE_COM
    GES = ROLE_GES
    SUP = ROLE_SUP
    ADM = ROLE_ADM


class Permission(Enum):
    READ_ACCESS = READ_ACCESS
    CREATE_EVENT = CREATE_EVENT
    EDIT_EVENT = EDIT_EVENT
    DELETE_EVENT = DELETE_EVENT
    CREATE_USER = CREATE_USER
    EDIT_USER = EDIT_USER
    DELETE_USER = DELETE_USER
    CREATE_CUSTOMER = CREATE_CUSTOMER
    EDIT_CUSTOMER = EDIT_CUSTOMER
    DELETE_CUSTOMER = DELETE_CUSTOMER
    CREATE_CONTRACT = CREATE_CONTRACT
    EDIT_CONTRACT = EDIT_CONTRACT
    DELETE_CONTRACT = DELETE_CONTRACT
    SORT_USER = SORT_USER
    SORT_CUSTOMER = SORT_CUSTOMER
    SORT_CONTRACT = SORT_CONTRACT
    SORT_EVENT = SORT_EVENT


role_permissions = {
    Role.ADM: {
        Permission.READ_ACCESS,
        Permission.CREATE_EVENT,
        Permission.EDIT_EVENT,
        Permission.DELETE_EVENT,
        Permission.CREATE_USER,
        Permission.EDIT_USER,
        Permission.DELETE_USER,
        Permission.CREATE_CUSTOMER,
        Permission.EDIT_CUSTOMER,
        Permission.DELETE_CUSTOMER,
        Permission.CREATE_CONTRACT,
        Permission.EDIT_CONTRACT,
        Permission.DELETE_CONTRACT,
        Permission.SORT_USER,
        Permission.SORT_CUSTOMER,
        Permission.SORT_CONTRACT,
        Permission.SORT_EVENT
    },
    Role.GES: {
        Permission.READ_ACCESS,
        Permission.CREATE_USER,
        Permission.EDIT_USER,
        Permission.CREATE_CONTRACT,
        Permission.EDIT_CONTRACT,
        Permission.DELETE_CONTRACT,
        Permission.EDIT_EVENT,
        Permission.SORT_EVENT,
        Permission.SORT_USER,
    },
    Role.COM: {
        Permission.READ_ACCESS,
        Permission.CREATE_CUSTOMER,
        Permission.EDIT_CUSTOMER,
        Permission.CREATE_EVENT,
        Permission.DELETE_EVENT,
        Permission.EDIT_CONTRACT,
        Permission.SORT_CONTRACT
    },
    Role.SUP: {
        Permission.READ_ACCESS,
        Permission.EDIT_EVENT,
        Permission.SORT_EVENT,
    }
}


def has_permission(role, permission):
    return permission in role_permissions.get(role, set())
