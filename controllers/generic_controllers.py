# generic_controller.py

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc


def sort_items(session, model, sort_by, order, role, sortable_attributes):
    """Générique méthode pour trier les éléments d'une classe modèle donnée."""

    """Trie les éléments du modèle donné en fonction des attributs spécifiés et du rôle de l'utilisateur."""
    if model not in sortable_attributes or role not in sortable_attributes[model]:
        print(f"Tri non autorisé pour le modèle {model.__name__} et le rôle {role.name}.")
        return []

    if sort_by not in sortable_attributes[model][role]:
        print(f"Attribut de tri non autorisé : {sort_by}")
        return []

    if order == 'asc':
        return session.query(model).order_by(asc(getattr(model, sort_by))).all()
    elif order == 'desc':
        return session.query(model).order_by(desc(getattr(model, sort_by))).all()
    else:
        raise ValueError("L'ordre de tri doit être 'asc' ou 'desc'")


def get_readonly_items(session: Session, model):
    """Méthode générique pour obtenir tous les éléments d'une classe modèle en lecture seule."""
    return session.query(model).all()
