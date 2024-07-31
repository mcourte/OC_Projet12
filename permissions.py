#  from models.customer import Customer
#  from models.user import User


# REFAIRE LES PERMISSION AVEC HAS_PERMISSION & HAS_OBJECT_PERMISSION

class IsAuthenticad:
    # Peut : voir l'ensemble des Customers, Contracts, Event & Listes des Users en LECTURE SEULE"
    pass


class UserGes:
    # Peut : CRUD un Contract, Ajouter un User(rôle=sup) à un Event
    # Peut : créer un User
    # Ne peut pas : Créer d'Event ou de Customer
    pass


class UserCom:
    # Peut : CRUD un Customer
    # Peut : Modifier un Contract
    # Peut : Créer un Event
    # Ne peut pas : Créer ou Supprimer un Contract
    pass


class UserSup:
    # Peut: Modifier un Event
    # Ne peut pas : Créer ou Supprimer un Event
    pass
