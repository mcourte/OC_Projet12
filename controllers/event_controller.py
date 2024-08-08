from models.event import Event
from permissions import has_permission, Permission, Role
from models.user import User
from controllers.generic_controllers import get_readonly_items
from constantes import get_sortable_attributes
from datetime import datetime


class EventController:
    def __init__(self, session=None, user_id=None):
        self.session = session
        self.user_id = user_id
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def sort_events(self, attribute):
        if not has_permission(self.user_role, Permission.SORT_EVENT):
            raise PermissionError("Vous n'avez pas les droits pour trier les utilisateurs.")

        sortable_attributes = get_sortable_attributes().get(Event, {}).get(self.user_role, [])
        if attribute not in sortable_attributes:
            print(f"Attribut de tri '{attribute}' non valide pour le rôle {self.user_role}.")
            return []

        sorted_users = sorted(self.get_users(), key=lambda x: getattr(x, attribute))
        return sorted_users

    def get_all_events(self):
        if not has_permission(self.user_role, Permission.READ_ACCESS):
            print("Permission refusée : Vous n'avez pas les droits pour afficher les évènements.")
            return []
        return get_readonly_items(self.session, Event)

    def create_event(self, name, start_date, end_date, location, attendees, notes):
        """Permet de créer un Event dans la BD"""
        if not name or not start_date or not end_date or not location or not attendees or not notes:
            raise ValueError("Tous les champs doivent être remplis.")

        if not has_permission(self.user_role, Permission.CREATE_EVENT):
            raise PermissionError("Vous n'avez pas la permission de créer un Event.")

        print(f"Validation passed for creating event: {name}")
        self._create_event_in_db(name, start_date, end_date, location, attendees, notes)

    def _create_event_in_db(self, name, start_date, end_date, location, attendees, notes):
        """Méthode privée pour créer l'évènement dans la base de données"""
        try:
            new_event = Event(
                name=name,
                start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                end_date=datetime.strptime(end_date, '%Y-%m-%d'),
                location=location,
                attendees=attendees,
                notes=notes
            )
            self.session.add(new_event)
            self.session.commit()
            print(f"Nouvel Evenement créé : {new_event.name}")
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la création de l'évènement : {e}")

    def edit_event(self, event_id, **kwargs):
        if not has_permission(self.user_role, Permission.EDIT_EVENT):
            print("Permission refusée : Vous n'avez pas les droits pour modifier cet évènement.")
            return

        event = self.session.query(Event).filter_by(event_id=event_id).first()
        if event is None:
            print(f"Aucun évènement trouvé avec l'ID {event_id}")
            return

        try:
            for key, value in kwargs.items():
                if self.user_role == Role.SUP and key == 'assignee_id':
                    print("Permission refusée : Vous ne pouvez pas modifier l'attribution.")
                    continue
                setattr(event, key, value)
            self.session.commit()
            print(f"Évènement avec l'ID {event_id} mis à jour avec succès.")
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la mise à jour de l'évènement : {e}")

    def delete_event(self, event_id):
        """Permet de supprimer un évènement de la BD"""
        if not has_permission(self.user_role, Permission.DELETE_EVENT):
            print("Permission refusée : Vous n'avez pas les droits pour supprimer cet évènement.")
            return

        event_to_delete = self.session.query(User).filter_by(event_id=event_id).first()

        try:
            self.session.delete(event_to_delete)
            self.session.commit()
            print(f"Evènement avec l'ID {event_id} supprimé avec succès.")
        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression de l'évènement : {e}")

    def get_event(self):
        return self.session.query(Event).all()
