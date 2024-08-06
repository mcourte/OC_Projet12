from models.event import Event
from permissions import has_permission, Permission, Role
from models.user import User
from generic_controllers import sort_items, get_readonly_items
from constantes import get_sortable_attributes


class EventController:
    def __init__(self, session, user_id):
        self.session = session
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            raise ValueError("Utilisateur non trouvé")
        self.user_role = user.role

    def sort_events(self, sort_by: str, order: str = 'asc'):
        if not has_permission(self.user_role, Permission.SORT_EVENT):
            print("Permission refusée : Vous n'avez pas les droits pour trier les évènements.")
            return []
        sortable_attributes = get_sortable_attributes()
        return sort_items(self.session, Event, sort_by, order, self.user_role, sortable_attributes)

    def get_all_events(self):
        if not has_permission(self.user_role, Permission.READ_ACCESS):
            print("Permission refusée : Vous n'avez pas les droits pour afficher les évènements.")
            return []
        return get_readonly_items(self.session, Event)

    def create_event(self, name, start_date, end_date, location, attendees, notes):
        """Permet de créer un Event dans la BD"""
        if not has_permission(self.user_role, Permission.CREATE_EVENT):
            print("Permission refusée : Vous n'avez pas les droits pour supprimer cet évènement.")
            return
        try:

            # Créer un nouveau client
            new_event = Event(
                name=name,
                start_date=start_date,
                end_date=end_date,
                location=location,
                attendees=attendees,
                notes=notes
            )

            # Ajouter le client à la session
            self.session.add(new_event)
            self.session.commit()

            print(f"Nouvel Evenement crée : {new_event.name} ")

        except Exception as e:
            # Autres exceptions possibles
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

        event = self.session.query(Event).filter_by(event_id=event_id).first()

        if event is None:
            print(f"Aucun évènement trouvé avec l'ID {event_id}")
            return

        try:
            self.session.delete(event)
            self.session.commit()
            print(f"Evènement avec l'ID {event_id} supprimé avec succès.")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors de la suppression de l'évènement : {e}")

    def get_event(self):
        return self.session.query(Event).all()
